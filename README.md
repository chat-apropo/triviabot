triviabot
=========

A IRC trivia bot written in python using twisted.

Features
--------

Simple implementation. Questions are <string>`<string> formatted in plain text files.

Configurable colored text to help differentiate game text from user text.

Event driven implementation: uses very little cycles.

Implementation
--------------

triviabot uses a config.py and comes with an example for you to tweak and use.

Questions exist in files under $BOTDIR/questions.
Each round, a file is selected at random, then a line is selected at random from the file.

The answer is then masked and the question is asked. Periodically, the bot will ask the current question
again and unmask a letter. This happens three times before the answer is revealed.

What the bot doesn't do.
------------------------

  * It doesn't have multiple answers to a question. It shows you the format. Part of the game is to match its formatting.

  * Have error-free questions: the questions come from other bot implementations which themselves had horrible typos.
There needs to be an army of editors to go through the 350+k lines and format them to the standard format for the bot.
The bot was written to catch malformed questions so it wouldn't crash, but if it technically matches <string>`<string>
there's no way for the bot to understand that's not part of the question.


Todo:
-----

Look at the issues. Pull requests welcome.


Contact, Support, Development:
------------------------------

Quakenet IRC - #triviabot-dev
http://webchat.quakenet.org/?channels=triviabot-dev

GitHub Issues/Tickets
https://github.com/rawsonj/triviabot/issues


License:
--------

Released under the GPLv3.


Modifications:
--------------

The authors of these modifications are Gabriel Artigue and Matheus Fillipe (gartigue@gmx.com).

### Installation

* Clone this repo

```bash
git clone https://github.com/matheusfillipe/triviabot.git
```

* Have python 3 installed and python virtualenv

```bash
# Debian, ubuntu 
sudo apt install python3-virtualenv

# Archlinux
sudo pacman -S pyton-virtualenv

# Or with pip/pip3
pip3 install virtualenv
```

* Create a virtual environment

This will create a venv inside the "venv" folder.

```bash
cd triviabot
python -m venv venv # can also be python3 in some distros
```


* Install dependencies

Source the environment and install dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

* Copy the example configuration

```bash
mv example_config.py config.py
```

Open `config.py` and edit the pertinent values like `SERVER`, `ADMIN` etc. If you wish to add more languages you can create your translations on the `strings.py` file. Make sure to set a server, port, ssl, channel, and admin nick that makes sense.

* Create the scores file

```bash
touch savedata/scores.json
```

* Create the questions folder

You can create questions by adding files that will be recursively looked up inside the `Q_DIR` folder that defaults to "questions" on the config. The format uses `:` and \` as separators.

```
THEME: questions text here?`answer now
```

You can also just grab the questions from the upstream questions folder: https://github.com/rawsonj/triviabot/tree/master/questions


* And now you can test run it

```bash
python trivia.py
```

### Production

If you want the bot to auto start on boot and be able to have it always running on background i recommend using pm2: https://pm2.keymetrics.io/docs/usage/quick-start/

It requires nodejs and npm:

```bash
npm install pm2@latest -g
```

Then go into the `triviabot` directory and run:

```bash
pm2 start trivia.py --name trivia --interpreter "$(pwd)/venv/bin/python3"
```

Now you are all set up. You can see logs with `pm2 logs trivia`, start, restart or stop with `pm2 start trivia` and so on.


### Usage

The bot has a nice `!help` command that will PM you with the commands you are allowed to use. Admins have extra commands.

    unpriviledged_commands = {'score'
                              'help'
                              'source'
                              'rank'
                              'repeat'
                              'next'
                              }

    priviledged_commands = {'die'
                            'restart'
                            'update'
                            'set'
                            'start'
                            'stop'
                            'save'
                            'rankon'
                            'rankoff'
                            'skip'
                            }

You can specify a custom config passing it to the script as the first argument. This should be a python file like `example_config.py` and needs to reside in the same directory as `trivia.py`:

```sh
python trivia.py config_en.py
```
