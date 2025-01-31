# Copyright (C) 2013 Joe Rawson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# The bot should respond to /msgs, so that users can check their scores,
# and admins can give admin commands, like die, show all scores, edit
# player scores, etc. Commands should be easy to implement.
#
# Every so often between questions the bot should list the top ranked
# players, wait some, then continue.
#

import json
import os
import string
import subprocess
import sys
from typing import Optional
import urllib
from datetime import datetime
from os import execl, listdir, path
from random import choice
from sys import stdout

from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.internet.task import LoopingCall
from twisted.python.log import startLogging
from twisted.words.protocols import irc

if len(sys.argv) > 1:
    import importlib

    config_file = sys.argv[1]
    if os.path.isfile(config_file):
        try:
            config = importlib.import_module(os.path.splitext(config_file)[0])
        except ImportError:
            print("Error importing config file.")
            sys.exit(1)
    else:
        raise FileNotFoundError("Config file not found.")
else:
    import config

from lib.answer import Answer
from strings import genTrans
from utils import interp

text = genTrans(config.LANG)

if not os.path.exists(config.SAVE_DIR):
    os.makedirs(config.SAVE_DIR)

if config.USE_SSL.lower() == "yes":
    from twisted.internet import ssl
elif config.USE_SSL.lower() != "no":
    # USE_SSL wasn't yes and it's not no, so raise an error.
    raise ValueError("USE_SSL must either be 'yes' or 'no'.")

# Determine text color
try:
    config.COLOR_CODE
except AttributeError:
    config.COLOR_CODE = ""

points = {
    0: 1,
    1: 3 / 5,
    2: 2 / 5,
    3: 1 / 5,
}


def is_higher_mode(mode1: str, mode2: Optional[str]) -> bool:
    """Check if mode1 is higher than mode2."""
    modes = ["v", "h", "o", "a", "q"]
    return mode2 is None or modes.index(mode1) > modes.index(mode2)


class triviabot(irc.IRCClient):
    """This is the irc bot portion of the trivia bot.

    It implements the whole program so is kinda big. The algorithm is
    implemented by a series of callbacks, initiated by an admin on the
    server.
    """

    def __init__(self):
        self._answer = Answer()
        self._question = ""
        self._scores = {}
        self._streak = {}
        self._rewarded_modes = {}
        self._clue_number = 0
        self._block_rank = False
        self._admins = list(config.ADMINS)
        self._admins.append(config.OWNER)
        self._game_channel = config.GAME_CHANNEL
        self._questions_dir = config.Q_DIR
        self._locutor_mode = False
        self._locutor_nick = ""
        self._lc = LoopingCall(self._play_game)
        self._quit = False
        self._restarting = False
        self._load_game()
        self._votes = 0
        self._voters = []
        self.nickname = config.DEFAULT_NICK
        self._load_freezelist()
        self.load_announcements()

    def load_announcements(self):
        """Load messages."""
        self._messages = []
        if config.MESSAGE_RANKING:
            self._messages.append(None)
        try:
            with open(config.ANNOUNCEMENTS_TXT, "r") as f:
                for message in f.readlines():
                    self._messages.append(message.strip())
        except FileNotFoundError:
            print(f"No messages file found at {config.ANNOUNCEMENTS_TXT}")

    def _get_nickname(self):
        return self.factory.nickname

    def _get_lineRate(self):
        return self.factory.lineRate

    lineRate = property(_get_lineRate)

    def _cmsg(self, dest, msg):
        """Write a colorized message."""
        # self.msg(dest, "{}{}".format(config.COLOR_CODE, msg))
        self.msg(dest, msg)

    def _gmsg(self, msg):
        """Write a message to the channel playing the trivia game."""
        self._cmsg(self._game_channel, msg)

    def _delayed_start(self):
        """Start for audio mode."""
        self._clue_number = 1
        self._start_time = datetime.now()
        self._gmsg(text.CLUE.format(self._answer.current_clue()))
        self._lc.start(config.WAIT_INTERVAL if not self._locutor_mode else config.AUDIO_WAIT_INTERVAL, now=False)

    def _display_announcements(self):
        """Display announcements to the channel."""
        if self._messages:
            m = choice(self._messages)
            if m is None:  # we display ranking
                self._standings(None, self._game_channel, None)
            else:
                self._gmsg(m)

        self.load_announcements()
        reactor.callLater(config.ANNOUNCEMENTS_DELAY, self._display_announcements)

    def _new_question(self):
        self._clue_number = 0
        self._votes = 0
        self._voters = []
        self._get_new_question()
        if self._locutor_mode:
            self._cmsg(self._locutor_nick, text.QUESTION)
            self._cmsg(self._locutor_nick, text.QUESTION_COLOR.format(self._question))
            self._cmsg(self._locutor_nick, f"{len(self._answer)} characters")
            self._gmsg(text.BLUE_COLOR.format(f"--> {config.AUDIO_URL}"))
            if self._lc.running:
                self._lc.stop()
            reactor.callLater(config.AUDIO_DELAY, self._delayed_start)
        else:
            self._gmsg(text.NEXT)
            self._gmsg(text.QUESTION_COLOR.format(self._question))
            self._gmsg(text.CLUE.format(self._answer.current_clue()))
            self._clue_number += 1
            self._start_time = datetime.now()

    def _play_game(self):
        """Implements the main loop of the game."""
        if self._clue_number == 0:
            self._new_question()
        # we must be somewhere in between
        elif self._clue_number < 4:
            if not self._locutor_mode:
                self._gmsg(text.QUESTION)
                self._gmsg(text.QUESTION_COLOR.format(self._question))
            self._gmsg(text.GIVE_CLUE.format(self._answer.give_clue()))
            self._clue_number += 1
        # no one must have gotten it.
        else:
            self._gmsg(text.NO_ONE_GOT.format(self._answer.answer))
            self.reest_streak()
            self._new_question()

    def signedOn(self):
        """Actions to perform on signon to the server."""
        self.join(self._game_channel)
        self.msg("NickServ", "identify {}".format(config.IDENT_STRING))
        print("Signed on as {}.".format(self.nickname))
        #        if self.factory.running:
        #            self._start(None, None, None)
        #        else:
        self._gmsg(text.WELCOME.format(self._game_channel))
        self._gmsg(text.HAVE_AN_ADMIN)
        self._gmsg(text.HAVE_HELP)
        self._gmsg(text.HELP.format(self.nickname))
        self._start(None, None, None)

    def joined(self, channel):
        """Callback runs when the bot joins a channel."""
        print("Joined {}.".format((channel)))

    def privmsg(self, user, channel, msg):
        """Parses out each message and initiates doing the right thing with
        it."""
        user, temp = user.split("!")
        print(user + " : " + channel + " : " + msg)
        # need to strip out non-printable characters if present.
        printable = string.printable
        msg = "".join(filter(lambda x: x in printable, msg))

        # parses each incoming line, and sees if it's a command for the bot.
        try:
            if msg[0] == "!":
                command = msg.replace("!", "").split()[0]
                args = msg.replace("!", "").split()[1:]
                self.select_command(command, args, user, channel)
                return
            elif msg.split()[0].find(self.nickname) == 0:
                command = msg.split()[1]
                args = msg.replace(self.nickname, "").split()[2:]
                self.select_command(command, args, user, channel)
                return
            # if not, try to match the message to the answer.
            else:
                if msg.casefold().strip() == self._answer.answer.casefold().strip():
                    self._winner(user, channel)
                    self._save_game()
        except Exception as e:
            print(e)
            return

    def userJoined(self, user, channel):
        """Called when I see another user joining a channel."""
        if user in self._rewarded_modes:
            del self._rewarded_modes[user]

        if channel != self._game_channel:
            return

        if config.AUTO_OP_ADMINS and user in config.ADMINS:
            self.mode(self._game_channel, True, "o", user=user)
            self._rewarded_modes[user] = "o"
            return

        if user in self._scores:
            r = self._get_rank(user)
            if r is not None:
                rank, _, _ = r
                self._check_rank_rewards(user, rank)

    def _freeze(self, args, user, channel):
        """Freezes a nick from increasing its score."""
        nick = args[0].strip()
        if nick not in self._scores:
            self._cmsg(user, f"WARNING: {nick} doesn't have any score. He will be blacklisted anyway.")
        if nick in self._frost_nicks:
            self._cmsg(user, f"WARNING: {nick} is already frozen.")
        self._frost_nicks.add(nick)
        self._gmsg(text.FREEZE.format(nick))
        self._save_freezelist()

    def _unfreeze(self, args, user, channel):
        """Unfreezes a nick from increasing its score."""
        nick = args[0].strip()
        if nick not in self._frost_nicks:
            self._cmsg(user, f"WARNING: {nick} is not frozen.")
            return
        self._frost_nicks.remove(nick)
        self._gmsg(text.UNFREEZE.format(nick))
        self._save_freezelist()

    def _frostlist(self, args, user, channel):
        """Lists all frozen nicks."""
        self._cmsg(user, "The following users have frozen scores: " + ", ".join(self._frost_nicks))

    def _check_rank_rewards(self, user, rank) -> bool:
        """Check for rank rewarding."""
        if not config.ENABLE_REWARDS:
            return False

        aquired_mode = None
        aquired_rank = None
        for required_rank, mode in config.RANK_REWARDS_MAP.items():
            if rank < required_rank and (aquired_rank is None or aquired_rank > required_rank):
                aquired_rank = required_rank
                aquired_mode = mode

        if aquired_mode is not None:
            if not is_higher_mode(aquired_mode, self._rewarded_modes.get(user)):
                return False

            self._gmsg(text.ON_RANK_MODE_REWARD.format(user, aquired_mode))
            self.mode(self._game_channel, True, aquired_mode, user=user)
            self._rewarded_modes[user] = aquired_mode
            return True

        return False

    def _average_score(self, top_users=None):
        """Computes and outputs the average score users."""
        if top_users is None:
            s = sum(self._scores.values())
            n = len(self._scores)
        else:
            from future.utils import iteritems

            sorted_scores = sorted(iteritems(self._scores), key=lambda d: d[1], reverse=True)
            # Only the first top_users are considered.
            group = sorted_scores[:top_users]
            n = len(group)
            s = sum([score for _, score in group])

        return s / n

    def _add_points_to_user(self, user):
        n_players = len(self._scores)
        if user not in self._scores:
            rank = n_players + 1
            n_players += 1
        else:
            rank_info = self._get_rank(user)
            if rank_info is None:
                rank = len(self._scores) + 1
            else:
                rank, _, _ = rank_info

        base_points = config.BASE_POINTS
        if config.MIN_USERS_FOR_PRIVILEDGE is not None and n_players > config.MIN_USERS_FOR_PRIVILEDGE:
            if config.MAX_POINTS == "increasing":
                max_points = int(
                    max(
                        self._average_score(top_users=config.UNPRIVILEDGED_GROUP) / (config.BASE_POINTS * 6),
                        config.BASE_POINTS * 1.5,
                    )
                )
            else:
                max_points = config.MAX_POINTS

            base_points = max(
                float(interp(rank, config.UNPRIVILEDGED_GROUP, n_players, config.BASE_POINTS, max_points)),
                config.BASE_POINTS,
            )
            self._gmsg(text.MAX_POINT_ANNOUNCE.format(max_points))

        winner_points = int(max(base_points, config.BASE_POINTS) * points[min(self._clue_number - 1, len(points) - 1)])

        if user in self._scores:
            self._scores[user] += winner_points
        else:
            self._scores[user] = winner_points

        if winner_points == 1:
            self._gmsg(text.POINT_ADDED.format(str(winner_points)))
        else:
            self._gmsg(text.POINTS_ADDED.format(str(winner_points)))

        had_rank_reward = False
        rank, score, after = self._get_rank(user)
        if rank:
            if not after and rank == 1:
                self._gmsg(text.NUMBER_ONE.format(user, score))
            else:
                self._gmsg(text.RANKING.format(user, score, rank, after))
            had_rank_reward = self._check_rank_rewards(user, rank)

        self.reest_streak(user)
        if user in self._streak:
            self._streak[user] += 1
        else:
            self._streak[user] = 1

        if config.ENABLE_REWARDS and not had_rank_reward:
            streak = self._streak[user]
            if streak in config.STREAK_REWARDS_MAP:
                mode = config.STREAK_REWARDS_MAP[streak]

                if is_higher_mode(mode, self._rewarded_modes.get(user)):
                    self._gmsg(text.ON_STREAK_MODE_REWARD.format(user, mode))
                    self.mode(self._game_channel, True, mode, user=user)
                    self._rewarded_modes[user] = mode

    def reest_streak(self, keep_user: Optional[str] = None):
        """Resets streak of all users, if keep_user is not None, it will keep the streak of that user."""
        for user in list(self._streak.keys()):
            if user == keep_user:
                continue
            del self._streak[user]

    def _winner(self, user, channel):
        """Congratulates the winner for guessing correctly and assigns points
        appropriately, then signals that it was guessed."""
        if channel != self._game_channel:
            self.msg(channel, text.RESPOND_ON_CHANNEL)
            return

        self._gmsg(text.USER_GOT_IT.format(user.upper()))
        self._gmsg(text.THE_ANSWER_WAS.format(self._answer.answer))

        if user in self._frost_nicks:
            self._gmsg(text.ON_FROST_WIN.format(user))
        else:
            self._add_points_to_user(user)

        self._clue_number = 0
        time_ran = datetime.now() - self._start_time
        self._gmsg(text.TIMMING.format(user, time_ran.seconds, round(time_ran.microseconds / 10000)))

        # Restart loop
        self._lc.stop()
        self._lc.start(config.WAIT_INTERVAL if not self._locutor_mode else config.AUDIO_WAIT_INTERVAL, now=True)

    def ctcpQuery(self, user, channel, msg):
        """Responds to ctcp requests.

        Currently just reports them.
        """
        print("CTCP recieved: " + user + ":" + channel + ": " + msg[0][0] + " " + msg[0][1])

    def _help(self, args, user, channel):
        """Tells people how to use the bot.

        Replies differently if you are an admin or a regular user. Only
        responds to the user since there could be a game in progress.
        """
        try:
            self._admins.index(user)
        except ValueError:
            self._cmsg(user, text.BELONG.format(config.OWNER))
            self._cmsg(user, text.COMMANDS)
            return
        self._cmsg(user, text.BELONG.format(config.OWNER))
        self._cmsg(user, text.COMMANDS)
        self._cmsg(user, text.ADMIN_CMDS)

    def _show_source(self, args, user, channel):
        """Tells people how to use the bot.

        Only responds to the user since there could be a game in
        progress.
        """
        self._cmsg(user, "My source can be found at: " "https://github.com/matheusfillipe/triviabot")

    def set_rank_block(self, b, args, user, channel):
        self._block_rank = b
        if b:
            self._cmsg(user, text.RANK_OFF)
        else:
            self._cmsg(user, text.RANK_ON)

    def select_command(self, command, args, user, channel):
        """Callback that responds to commands given to the bot.

        Need to differentiate between priviledged users and regular
        users.
        """
        # set up command dicts.
        unpriviledged_commands = {
            "score": self._score,
            "help": self._help,
            "source": self._show_source,
            "rank": self._standings,
            "repeat": self._give_clue,
            "next": self._next_vote,
        }
        priviledged_commands = {
            "die": self._die,
            "restart": self._restart,
            "update": self._update,
            "set": self._set_user_score,
            "start": self._start,
            "stop": self._stop,
            "save": self._save_game,
            "rankon": lambda a, u, c: self.set_rank_block(False, a, u, c),
            "rankoff": lambda a, u, c: self.set_rank_block(True, a, u, c),
            "skip": self._next_question,
            "audio": self._audio,
            "text": self._text,
            "freeze": self._freeze,
            "unfreeze": self._unfreeze,
            "frostlist": self._frostlist,
        }
        print(command, args, user, channel)
        try:
            self._admins.index(user)
            is_admin = True
        except ValueError:
            is_admin = False

        # the following takes care of sorting out functions and
        # priviledges.
        if not is_admin and command in priviledged_commands:
            self.msg(channel, text.NOT_ALLOWED.format(user))
            return
        elif is_admin and command in priviledged_commands:
            priviledged_commands[command](args, user, channel)
        elif command in unpriviledged_commands:
            unpriviledged_commands[command](args, user, channel)
        else:
            self.describe(channel, text.LOOKS_ODLY.format(config.COLOR_CODE, user))

    def _next_vote(self, args, user, channel):
        """Implements user voting for the next question.

        Need to keep track of who voted, and how many votes.
        """
        if not self._lc.running:
            self._gmsg(text.NOT_PLAYING)
            return
        try:
            self._voters.index(user)
            self._gmsg(text.ALREADY_VOTED.format(user))
            return
        except:
            if self._votes < 2:
                self._votes += 1
                self._voters.append(user)
                print(self._voters)
                self._gmsg(text.YOU_VOTED.format(user, str(3 - self._votes)))
            else:
                self._votes = 0
                self._voters = []
                self._next_question(None, None, None)

    def _start(self, args, user, channel):
        """Starts the trivia game.

        TODO: Load scores from last game, if any.
        """
        if self._lc.running:
            return
        else:
            reactor.callLater(config.ANNOUNCEMENTS_DELAY, self._display_announcements)
            self._lc.start(config.WAIT_INTERVAL)
            self.factory.running = True

    def _stop(self, *args):
        """Stops the game and thanks people for playing, then saves the
        scores."""
        if not self._lc.running:
            return
        else:
            self._lc.stop()
            self._gmsg(text.THANKS)
            self._gmsg(text.RANKINGS)
            self._standings(None, self._game_channel, None)
            self._gmsg(text.SEE_YOU)
            self._save_game()
            self.factory.running = False

    def _audio(self, args, user, channel):
        """Turns audio mode on."""
        self._locutor_mode = True
        self._locutor_nick = user
        self._gmsg(text.AUDIO_ON)
        self._cmsg(user, "------------------------------------------------")
        self._new_question()

    def _text(self, *args):
        """Turns audio mode off."""
        self._locutor_mode = False
        self._gmsg(text.AUDIO_OFF)
        self._new_question()

    def _save_freezelist(self, *args):
        """Saves the freeze list to the data directory."""
        with open(os.path.join(config.SAVE_DIR, "freeze.json"), "w") as savefile:
            json.dump(list(self._frost_nicks), savefile)
            print("Freeze list has been saved.")

    def _load_freezelist(self):
        """Loads the freeze list from previous games."""
        # ensure initialization
        self._frost_nicks = set()
        if not path.exists(config.SAVE_DIR):
            print("Save directory doesn't exist.")
            return
        try:
            with open(os.path.join(config.SAVE_DIR, "freeze.json"), "r") as savefile:
                temp_list = json.load(savefile)
        except:
            print("Save file doesn't exist.")
            return
        self._frost_nicks = set(temp_list)
        print("Freeze list has been loaded.")

    def _save_game(self, *args):
        """Saves the game to the data directory."""
        with open(os.path.join(config.SAVE_DIR, "scores.json"), "w") as savefile:
            json.dump(self._scores, savefile)
            print("Scores have been saved.")

    def _load_game(self):
        """Loads the running data from previous games."""
        # ensure initialization
        self._scores = {}
        if not path.exists(config.SAVE_DIR):
            print("Save directory doesn't exist.")
            return
        try:
            with open(os.path.join(config.SAVE_DIR, "scores.json"), "r") as savefile:
                temp_dict = json.load(savefile)
        except:
            print("Save file doesn't exist.")
            return
        for name in temp_dict.keys():
            self._scores[str(name)] = int(temp_dict[name])
        print(self._scores)
        print("Scores loaded.")

    def _set_user_score(self, args, user, channel):
        """Administrative action taken to adjust scores, if needed."""
        try:
            self._scores[args[0]] = int(args[1])
        except:
            self._cmsg(user, args[0] + " not in scores database.")
            return
        self._cmsg(user, args[0] + " score set to " + args[1])

    def _die(self, *args):
        """Terminates execution of the bot."""
        self._quit = True
        self.quit(message="This is triviabot, signing off.")

    def _restart(self, *args):
        """Restarts the bot."""
        self._restarting = True
        print("Restarting")
        self.quit(message="Triviabot restarting.")

    def _update(self, *args):
        self.quit(message="I will update now! Wait a few minutes")
        subprocess.Popen(config.UPDATE_SCRIPT + " &", shell=True)

    def connectionLost(self, reason):
        """Called when connection is lost."""
        global reactor
        if self._restarting:
            try:
                execl(sys.executable, *([sys.executable] + sys.argv))
            except Exception as e:
                print("Failed to restart: {}".format(e))
        if self._quit:
            reactor.stop()

    def _score(self, args, user, channel):
        """Tells the user their score."""
        try:
            self._cmsg(user, text.SCORE.format(str(self._scores[user])))
        except:
            self._cmsg(user, text.IDKU)

    def _next_question(self, args, user, channel):
        """Administratively skips the current question."""
        if not self._lc.running:
            self._gmsg(text.NOT_PLAYING)
            return
        self._gmsg(text.SKIPPED_THE_ANSWER_WAS.format(self._answer.answer))
        self._clue_number = 0
        self.reest_streak()
        self._lc.stop()
        self._lc.start(config.WAIT_INTERVAL if not self._locutor_mode else config.AUDIO_WAIT_INTERVAL)

    def _get_rank(self, user):
        from future.utils import iteritems

        sorted_scores = sorted(iteritems(self._scores), key=lambda d: d[1], reverse=True)
        i = 0
        after = None
        for rank, (player, score) in enumerate(sorted_scores, start=1):
            if player == user:
                return rank, score, after
            after = player
            i += 1

    def _standings(self, args, user, channel):
        """Tells the user the complete standings in the game."""
        if self._block_rank:
            return

        from future.utils import iteritems

        if user:
            self._cmsg(user, text.STANDINGS)
        else:
            self._gmsg(text.STANDINGS)
        sorted_scores = sorted(iteritems(self._scores), key=lambda d: d[1], reverse=True)

        i = 0
        end = max(0, int(args[0]) - 1 if args and len(args) and args[0].isdigit() else 9)
        formatted_score = ""
        for rank, (player, score) in enumerate(sorted_scores, start=1):
            formatted_score += "{}: {}: {}".format(rank, player, score)
            if i % 5 == 0:
                if user:
                    self._cmsg(user, formatted_score)
                else:
                    self._gmsg(formatted_score)
                formatted_score = ""
            else:
                formatted_score += " | "
            i += 1
            if i >= end:
                break

    def _give_clue(self, args, user, channel):
        if not self._lc.running:
            self._gmsg(text.NOT_PLAYING)
            return
        self._cmsg(channel, text.QUESTION)
        self._cmsg(channel, text.QUESTION_COLOR.format(self._question))
        self._cmsg(channel, text.CLUE.format(self._answer.current_clue()))

    def load_file(self):
        filename = choice(listdir(self._questions_dir))
        fd = open(os.path.join(config.Q_DIR, filename), encoding="utf8", errors="ignore")
        lines = fd.read().splitlines()
        fd.close()
        return lines

    def _get_new_question(self):
        """Selects a new question from the questions directory and sets it."""
        damaged_question = True
        while damaged_question:
            # randomly select file
            if hasattr(config, "URL"):
                url = config.URL
                try:
                    res = urllib.request.urlopen(url)
                    if res.getcode() == 200:
                        print("Loading from ", url)
                        lines = res.readlines()
                    else:
                        lines = self.load_file()
                except:
                    lines = self.load_file()
            else:
                lines = self.load_file()
            myline = choice(lines)
            myline = myline.decode() if type(myline) == bytes else myline
            try:
                self._question, temp_answer = myline.split("`")
            except ValueError:
                print("Broken question:")
                print(myline)
                continue
            self._answer.set_answer(temp_answer.strip())
            damaged_question = False


class ircbotFactory(ClientFactory):
    protocol = triviabot

    def __init__(self, nickname=config.DEFAULT_NICK):
        self.nickname = nickname
        self.running = False
        self.lineRate = config.LINE_RATE

    def clientConnectionLost(self, connector, reason):
        print("Lost connection ({})".format(reason))
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("Could not connect: {}".format(reason))
        connector.connect()


if __name__ == "__main__":
    # SSL will be attempted in all cases unless "NO" is explicity specified
    # in the config
    startLogging(stdout)

    if config.USE_SSL.lower() == "no":
        reactor.connectTCP(config.SERVER, config.SERVER_PORT, ircbotFactory())
    else:
        reactor.connectSSL(config.SERVER, config.SERVER_PORT, ircbotFactory(), ssl.ClientContextFactory())

    reactor.run()
