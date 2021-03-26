# -*- coding: utf-8 -*-
EN = "en"
RO = "ro"
COLOR = "color"

DEFAULT_COLOR = '13,06'
#First number is foreground, second is background
##############################
# COLOR CODES
##############################
#0 	White 	
#1 	Black 	
#2 	Navy 	
#3 	Green 	
#4 	Red 	
#5 	Maroon 	
#6 	Purple 	
#7 	Orange 	
#8 	Yellow 	
#9 	Light Green 
#10 	Teal 	
#11 	Cyan 	
#12 	Royal blue 	
#13 	Magenta 	
#14 	Gray 	
#15 	Light Gray 	
##############################

class Text:
    NEXT = {EN: "Next question:", RO: "Următoarea întrebare:"}
    CLUE = {EN: "Clue: {}", RO: "Pistă: {}"}
    QUESTION = {EN: "Question:", RO: "Întrebare:"}
    GIVE_CLUE = {EN: "Clue: {}", RO: "Pistă: {}"}
    NO_ONE_GOT = {EN: "No one got it. The answer was: {}", RO: "Aşadar, nimeni nu a ştiut-o. Răspunsul era: {}", COLOR: '04,00'}
    WELCOME = {EN: "Welcome to {}!", RO: "Bun-venit la {}!", COLOR: "12,00"}
    HAVE_AN_ADMIN = {EN: "Have an admin start the game when you are ready.", RO: "Ca un admin să pornească jocul când toată lumea e gata."}
    HAVE_HELP = {EN: "For how to use this bot, just say !help or", RO: "Ca să vedeţi instrucţiunile, tastaţi !help sau trivia help."}
    HELP = {EN: "{} help."}
    RESPOND_ON_CHANNEL = {EN: "I'm sorry, answers must be given in the game channel.", RO: "Îmi pare rău dar trebuie să dai răspunsurile pe canalul jocului."}
    USER_GOT_IT = {EN: "{} GOT IT!", RO: "{} A ŞTIUT-O!", COLOR: "02,00"}
    THE_ANSWER_WAS = {EN: "If there was any doubt, the correct answer was: {}", RO: "Dacă cumva aveaţi dubii, răspunsul corect era: {}"}
    POINT_ADDED = {EN: "{} point has been added to your score!", RO: "{} punct a fost adăugat la scorul tău!"}
    POINTS_ADDED = {EN: "{} points have been added to your score!", RO: "{} puncte au fost adăugate la scorul tău!"}
    BELONG = {EN:  "I'm {}'s trivia bot.", RO: "Sunt bot-ul trivia al lui {}."}
    COMMANDS = {EN:  "Commands: score, standings, repeat, help, next, source", RO: "Comenzi pentru jucători: score, standings, repeat, help, next, source"}
    ADMIN_CMDS = {EN: "Admin commands: die, set <user> <score>, start, stop, save, skip", RO: "Comenzi pentru admini: die, set <user> <score>, start, stop, save, skip"}
    NOT_ALLOWED = {EN: "{}: You don't tell me what to do.", RO: "{}: să nu-mi spui tu mie ce să fac."}
    LOOKS_ODLY = {EN: "{} looks at {} oddly.", RO: "{} trivia nu poate procesa ceea ce {} vrea."}
    NOT_PLAYING = {EN: "We aren't playing right now.", RO: "Chiar chiar acuşi nu ne jucăm."}
    ALREADY_VOTED = {EN: "You already voted, {}, give someone else a chance to hate this question", RO: "Bre {}, matale deja ai votat, ar trebui să voteze altcineva."}
    YOU_VOTED = {EN: "{}, you have voted. {} more votes needed to skip.", RO: "{}, ai votat pentru a sări peste întrebarea curentă. Totuşi e nevoie să mai voteze încă {}"}
    THANKS = {EN: 'Much obliged for playing trivia!', RO: 'Mulţumesc că joci trivia!'}
    RANKINGS = {EN: 'Current rankings were:', RO: 'Clasamentul actual:'}
    SEE_YOU = {EN: 'Scores have been saved, and see you next game!', RO: 'Punctajele au fost salvate, ne vedem la următorul joc!'}
    SCORE = {EN:  "Your current score is: {}", RO: "Punctajul tău actual este: {}"}
    IDKU = {EN:  "You aren't in my database.", RO: "Matale nu eşti în baza de date."}
    SKIPPED_THE_ANSWER_WAS = {EN: "Question has been skipped. The answer was: {}", RO: "Păi am sărit peste această întrebare. Răspunsul era: {}", RO: "Deci am sărit peste această întrebare. Răspunsul corect era: {}"}
    STANDINGS = {EN:  "The current trivia standings are: ", RO: "Acesta este clasamentul curent:"}
    TIMMING = {EN: "{} has given the answer in {}.{} seconds.", RO: "{} a dat răspunsul corect în {}.{} secunde."}
    RANKING = {EN: "{} has now {} points and is the {}th in the ranking after {}.", RO: "{} are acum {} puncte şi este al {}-lea în clasament după {}."}
    NUMBER_ONE = {EN: "{} now has {} and is number one in the rankings.", RO: "{} are acum {} şi este pe locul întâi in clasament."}
    RANK_OFF = {EN: "Rank was turned off", COLOR: ''}
    RANK_ON = {EN: "Rank was turned on"}


def genTrans(lang):
    t = Text()
    for k in dir(t):
        if not k.startswith("_"):
            o = getattr(Text, k)
            cc = "{}{}".format('\003', o[COLOR] if COLOR in o else DEFAULT_COLOR)
            if lang in o:
                setattr(t, k, "{}{}".format(cc, o[lang]))
            else:
                setattr(t, k, "{}{}".format(cc, o[EN]))

    return t
