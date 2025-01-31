# Example config for triviabot
#
# This file is part of triviabot
# Web site: https://github.com/rawsonj/triviabot)
#
# Copy this file to 'config.py', then edit 'config.py' to
# set your preferences.

GAME_CHANNEL = '#trivia'

# Nick of person running this bot? (the nick included here will be
# automatically added to the list of ADMINS)
# It will be displayed to user when ?help option is run
OWNER = 'your_nick'

# or a comma separated list of nicks
ADMINS = []

# Automatically attempt to OP users in admin list
AUTO_OP_ADMINS = True

# Directory the questions are stored at
Q_DIR = './questions/'

# Directory the scores are stored at
SAVE_DIR = './savedata/'

IDENT_STRING = 'x1x2x3x4x5iojfaJsi39'

# Time (in seconds) between clues, and the wait time between questions.
# If ?skip is used, the interval doesn't apply
WAIT_INTERVAL = 10

# Colorize the text so it contrasts with the channel text.
# This makes it easier to play the game when people are chatting.
#
# \003 is the color-code prefix, the next two numbers
# is the foreground code, the last two numbers is the background code.
# A more in-depth explanation is at http://en.wikichip.org/wiki/irc/colors
COLOR_CODE = '\00308,01'

# How fast will the bot output messages to the channel
LINE_RATE = 0.2

DEFAULT_NICK = 'trivia'

SERVER = 'irc.server.com'

# Some servers support SSL, and some do not. If you have trouble connecting
# to your IRC network, you may have to disable SSL or change the server port
SERVER_PORT = 6667
USE_SSL = "NO"

# Language iso code. Create more translations at strings.py
LANG = "en"

# Script to be called at restart. Leave blank.
UPDATE_SCRIPT = ""

### AUDIO MODE ####
# In this mode the bot will DM the questions to a admin user that is supposed to be narrate it.
# URL of the audio stream for audio mode 
AUDIO_URL = "https://radio.dot.org.es/stream.ogg"
# On audio mode this is the interval between questions
AUDIO_WAIT_INTERVAL = 10
# How much to wait before giving clues
AUDIO_DELAY = 10

# Messages  and annmouncements
# List of messages to be displayed to the channel randomly picked line by line
ANNOUNCEMENTS_TXT = "./messages.txt"
# Interval between messages
ANNOUNCEMENTS_DELAY = 60*4
# Should the rank top 5 also be announced from time to time?
MESSAGE_RANKING = True


# Ranking system
# Maximum points that can be awarded without priviledge
BASE_POINTS = 10
# Number of users from which we start applying progressive points system. Set to None to disable this feature altogether.
MIN_USERS_FOR_PRIVILEDGE = 15
# Maximum points that can be awarded with priviledge interpolated between newcommers and UNPRIVILEDGED_GROUP. Set to "increasing" to have it increase with the number of users
# With "increasing" it will compute MAX_POINTS proportionally to the average score of the top CONTROL_GROUP users.
MAX_POINTS = "increasing"
# 10 Means that the top 10 users will be used to compute the average score for increasing max points and don't receive any extra points
UNPRIVILEDGED_GROUP = 10


# Rewarding system.
# Set to true to enable it
ENABLE_REWARDS = False
# Keys are the minimum rank required for reward and the keys are the IRC modes. The top X users will be rewarded with the MODE.
RANK_REWARDS_MAP = {
    10: "o",
    20: "h",
    30: "v",
}
# Streak rewards. Works the same way but the values refer to the number of consecutive correct answers
STREAK_REWARDS_MAP = {
    4: "o",
    2: "h",
    1: "v",
}
