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
# Maximum points that can be awarded without tips
MAX_POINTS = 10
# Number of users from which we start the wealth tax for better distribution of points
MIN_USERS_FOR_PRIVILEDGE = 15
# Users are divided in 10 quantiles, each quantile has a different tax which is a fixed ammount of points to subtract from
# MAX_POINTS. The tax is calculated as something like: ((MAX_POINTS + PRIVILEDGE) * (4 - N_OF_TIPS_GIVEN) / 5)
# key is the quantile number, value is the PRIVILEDGE
PRIVILEDGE = {
    0: 0,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    9: 9,
}
