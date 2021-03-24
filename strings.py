# -*- coding: utf-8 -*-
EN = "en"
RO = "ro"


class Text:
    NEXT = {EN: "Next question:", RO: "Următoarea întrebare:"}
    CLUE = {EN: "Clue: {}", RO: "Pistă: {}"}
    QUESTION = {EN: "Question:", RO: "Întrebare:"}
    GIVE_CLUE = {EN: "Clue: {}", RO: "Pistă: {}"}
    NO_ONE_GOT = {EN: "No one got it. The answer was: {}", RO: "Aşadar, nimeni nu a ştiut-o. Răspunsul era: {}"}
    WELCOME = {EN: "Welcome to {}!", RO: "Bun-venit la {}!"}
    HAVE_AN_ADMIN = {EN: "Have an admin start the game when you are ready.", RO: "Ca un admin să pornească jocul când toată lumea e gata."}
    HAVE_HELP = {EN: "For how to use this bot, just say !help or", RO: "Ca să vedeţi instrucţiunile, tastaţi !help sau trivia help."}
    HELP = {EN: "{} help."}
    RESPOND_ON_CHANNEL = {EN: "I'm sorry, answers must be given in the game channel."}
    USER_GOT_IT = {EN: "{} GOT IT!", RO: "{} A ŞTIUT-O!"}
    THE_ANSWER_WAS = {EN: "If there was any doubt, the correct answer was: {}", RO: "Dacă cumva aveaţi dubii, răspunsul corect era: {}"}
    POINT_ADDED = {EN: "{} point has been added to your score!", RO: "{} puncte au fost adăugate la scorul tău!"}
    POINTS_ADDED = {EN: "{} points have been added to your score!", RO: "{} puncte au fost adăugate la scorul tău!"}
    BELONG = {EN:  "I'm {}'s trivia bot.", RO: "Sunt bot-ul trivia al lui {}."}
    COMMANDS = {EN:  "Commands: score, standings, hint, help, next, source", RO: "Comenzi pentru jucători: score, standings, hint, help, next, source"}
    ADMIN_CMDS = {EN: "Admin commands: die, set <user> <score>, start, stop, save, skip", RO: "Comenzi pentru admini: die, set <user> <score>, start, stop, save, skip"}
    NOT_ALLOWED = {EN: "{}: You don't tell me what to do."}
    LOOKS_ODLY = {EN: "{} looks at {} oddly.", RO: "{} trivia nu poate procesa ceea ce {} vrea."}
    NOT_PLAYING = {EN: "We aren't playing right now."}
    ALREADY_VOTED = {EN: "You already voted, {}, give someone else a chance to hate this question", RO: "Bre {}, matale deja ai votat, ar trebui să voteze altcineva."}
    YOU_VOTED = {EN: "{}, you have voted. {} more votes needed to skip.", RO: "{}, ai votat pentru a sări peste întrebarea curentă. Totuşi e nevoie să mai voteze încă {}"}
    THANKS = {EN: 'Thanks for playing trivia!'}
    RANKINGS = {EN: 'Current rankings were:'}
    SEE_YOU = {EN: 'Scores have been saved, and see you next game!'}
    SCORE = {EN:  "Your current score is: {}"}
    IDKU = {EN:  "You aren't in my database."}
    SKIPPED_THE_ANSWER_WAS = {EN: "Question has been skipped. The answer was: {}", RO: "Păi am sărit peste această întrebare. Răspunsul era: {}", RO: "Deci am sărit peste această întrebare. Răspunsul corect era: {}"}
    STANDINGS = {EN:  "The current trivia standings are: "}


def genTrans(lang):
    t = Text()
    for k in dir(t):
        if not k.startswith("_"):
            o = getattr(Text, k)
            if lang in o:
                setattr(t, k, o[lang])
            else:
                setattr(t, k, o[EN])

    return t
