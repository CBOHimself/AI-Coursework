from translate import Translator
from sportsreference.fb.team import Team
import wikipedia
import json, requests
from nltk.sem import Expression
import pandas
from nltk.inference import ResolutionProver
ArithmeticError  # !/usr/bin/env python3
# -*- coding: utf-8 -*-


# OpenWeathermap API key
APIkey = "281a5596875cae9561b2195ba39b422a"

#  Initialise NLTK Inference
#######################################################

read_expr = Expression.fromstring

#######################################################
#  Initialise Knowledgebase.
#######################################################

kb=[]
data = pandas.read_csv('kb.csv', header=None)
[kb.append(read_expr(row)) for row in data[0]]


#######################################################
#  Initialise AIML agent
#######################################################
import aiml

# Create a Kernel object. No string encoding (all I/O is unicode)
kern = aiml.Kernel()
kern.setTextEncoding(None)

kern.bootstrap(learnFiles="assignment.xml")

print("Welcome to the Football Chatbot!")
print("You can also ask me general knowledge questions. I know a lot")
print("Allow me to introduce myself, I'm footy the football chatbot. What is your name?")


while True:
    # get user input
    try:
        userInput = input("YOU: ")
    except (KeyboardInterrupt, EOFError) as e:
        print("Goodbye!")
        break
    # pre-process user input and determine response agent (if needed)
    responseAgent = 'aiml'
    # activate selected response agent
    if responseAgent == 'aiml':
        answer = kern.respond(userInput)
    # post-process the answer for commands
    if answer[0] == '#':
        params = answer[1:].split('$')
        cmd = int(params[0])
        if cmd == 0:
            print(params[1])
            break
        elif cmd == 1:
            # Wikipedia Library
            try:
                wSummary = wikipedia.summary(params[1], sentences=3, auto_suggest=False)
                print(wSummary)
            except:
                print("Sorry, I do not know that. Be more specific!")
        elif cmd == 3:
            #Translator Library
            try:
                translateTo = kern.getPredicate('translateTo')
                translator = Translator(to_lang=translateTo)

                responseTranslate = kern.getPredicate('response')
                translation = translator.translate(responseTranslate)
                print(translation)
            except:
                print("I cant translate to that language")
        elif cmd == 4:
            #Football Library
            try:

                x = ""
                teamName = kern.getPredicate('teamName')
                x = str(teamName)

                print(
                        "NAME: " + Team(x).name + "\n"
                        "MANAGER: " + Team(x).manager + "\n" + "COUNTRY: " + Team(x).country + "\n" +
                        "LEAGUE: " + Team(x).league + "\n" + "LEAGUE POSITION: " + str(Team(x).position))

            except:
                print("Could not find team stat")

        elif cmd == 5:
            #Weather Library
            succeeded = False
            api_url = r"http://api.openweathermap.org/data/2.5/weather?q="
            response = requests.get(api_url + params[1] + r"&units=metric&APPID="+APIkey)
            if response.status_code == 200:
                response_json = json.loads(response.content)
                if response_json:
                    t = response_json['main']['temp']
                    tmi = response_json['main']['temp_min']
                    tma = response_json['main']['temp_max']
                    hum = response_json['main']['humidity']
                    wsp = response_json['wind']['speed']
                    wdir = response_json['wind']['deg']
                    conditions = response_json['weather'][0]['description']
                    print("The temperature is", t, "°C, varying between", tmi, "and", tma, "at the moment, humidity is", hum, "%, wind speed ", wsp, "m/s,", conditions)
                    succeeded = True
            if not succeeded:
                print("Sorry, I could not resolve the location you gave me.")

        elif cmd == 6:
            # Adds new information to knowledge base
            object,subject = params[1].split(' is in ')
            expr = read_expr(subject + '(' + object + ')')
            kb.append(expr)
            print('Alright, I will note that',object,'is in ', subject)

        elif cmd == 7:
            # Makes comparison with knowledge in kb
            object,subject = params[1].split(' is in ')
            expr = read_expr(subject + '(' + object + ')')
            answer = ResolutionProver().prove(expr, kb, verbose=True)
            if answer:
               print('That is right.')
            else:
               print('That is not true')

        elif cmd == 99:
            print("I couldn't understand you there. Please rephrase that.")
    else:
        print(answer)
