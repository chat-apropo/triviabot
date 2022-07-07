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
