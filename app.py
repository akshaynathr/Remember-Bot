'''Main file'''
import os
import sys
import json

import requests
from flask import Flask, request
from wiki import *
from models import dbSetUp,r
from jokes import jokes
from facts import facts
from quotes import quotes
from random import randint
from news import *
import datetime
from search import *
from manager import *
import arrow

dbSetUp()


_chatbot_agent=None



app = Flask(__name__)

token="remember_bot"
@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == token:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    previous=""
    # endpoint for processing incoming messaging events
    flag=0

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get('read'):
                    print("Message read")
                    continue


                if messaging_event.get('delivery'):
                    print("Message delivered")
                    continue


                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    if messaging_event["message"].get("text"):
                        message_text = messaging_event["message"]["text"]
                        message_text =message_text.strip("?")
                        message_text =message_text.strip(".")
                        message_text =message_text.strip("~")
                        #message_text.strip("\")
                        message_text =message_text.strip("!")
                        message_text =message_text.strip("$")
                        message_text =message_text.strip("%")
                        message_text =message_text.strip("*")
                        message_text =message_text.strip("-")
                        message_text =message_text.strip("'")

                        #return "ok",200
                        if previous==message_text.lower():
                            return "ok",200
                        else:
                            previous=message_text#.lower()

                        msg_lst=message_text.split(" ")



                        '''SAVE FUNCTIONS '''


                        if msg_lst[0].lower()=="save":
                            flag=1
                            l=len(msg_lst[0])
                            if len(message_text)==l or len(msg_lst)==2:
                                send_message(sender_id,"Please specify something to save. Type 'Save ExamId 12345' ")
                            else:
                                y=message_text.lower()
                                t=y.split()
                                value=t[-1]

                                key=t[1:len(t)-1]
                                k=""
                                for i in key:
                                    if i!='as' or i!='on' or i!='is':
                                        k=k+" "+i

                                k=k[1:]

                                k=k.strip()

                                res=save_post(sender_id,k,value)

                                if res:
                                    print("Successfully saved")
                                    send_message(sender_id,"saved successfully")

                                else:
                                    print("Error in db save")
                                    send_message(sender_id,"Error in saving. Please try again")








                        '''GET FUNCTIONS'''
                        if msg_lst[0].lower()=="get" or msg_lst[0].lower()=="recall":
                            flag=1
                            key=msg_lst[1:]
                            print (key)
                            k=""
                            for i in key:
                                k=k+" "+i
                            k=k[1:]
                            k=k.strip(" ")
                            print (k)

                            res=get_post(sender_id,k)
                            if len(res)==0:
                                send_message(sender_id,"Oops no memories found")
                            else:
                                send_message(sender_id,res[0]["value"])







                        ''' WIKI FUNCTIONS '''
                        if msg_lst[0].lower()=="wiki":
                            flag=1
                            l=len(msg_lst[0])
                            if len(message_text)==l:
                                send_message(sender_id,"You specified nothing to search. Type 'Wiki search_term' ")
                            else:
                                search=message_text[l:]
                                result=search_wiki(search) 
                                if len(result)==0:
                                    send_message(sender_id,"Oops. Cannot find anything in wiki")
                                else:

                                    article=get_results_wiki(result[0])


                                    heading = article.heading
                                    image=article.image
                                    url=article.url
                                    fall_back_url="https://en.wikipedia.org/"
                                    data=generic_template(url=url,img_url=image,title=heading,sub_title=None,fall_back_url=fall_back_url,btn_url=url,btn_title="Go to wiki",recipient=sender_id)
                                    #send_message(sender_id,"test")
                                    #send_message(sender_id,"Fetching data from wikipedia")
                                    send_message(sender_id,None,data)
                                    return "Ok",200





                        ''' SAY/TELL FUNCTIONs '''
                        if msg_lst[0].lower()=="say" or msg_lst[0].lower()=="tell":
                            flag=1

                            if len(msg_lst)<=1:
                                send_message(sender_id,"What should i say?")
                                return "ok",200
                            else:
                                if msg_lst[-1].lower()=="joke":
                                    send_message(sender_id,get_jokes())
                                    return "ok",200
                                elif msg_lst[-1].lower()=="fact":
                                    send_message(sender_id,get_fact())
                                    return "ok",200
                                elif msg_lst[-1].lower()=="quote":
                                    send_message(sender_id,get_quote())
                                    return "ok",200
                                else:
                                    send_message(sender_id,message_text[5:])
                                    return "ok",200

                        ''' news function '''

                        if message_text.lower()=="what's new in techcrunch?" or message_text.lower()=="whats new in techcrunch?" or message_text.lower()=="show me techcrunch" or message_text.lower()=="news in techcrunch" or message_text.lower()=="what's new in techcrunch" or (msg_lst[0].lower()!="search" and message_text.lower().find("techcrunch")!=-1):
                            flag=1
                            news=get_news()
                            data=news_generic_template(news,sender_id)
                            print (data)

                            send_message(sender_id,None,data)
                            return "ok",200

                       
                        ''' REMIND FUNCTION '''


                        if msg_lst[0].lower()=='remind':
                            flag=1
                            if len(msg_lst)<2:
                                send_message(sender_id,"Please tell me something to remind you. Eg: Remind me to watch sherlock tomorrow")
                            else:

                                if message_text.find("hours") !=-1:
                                    connection=r.connect("localhost",28015)
                                    delta=int(msg_lst[-2])
                                    time=arrow.utcnow().to('Asia/Calcutta')
                                    time=time.replace(hours=+delta)
                                    _t=time

                                    time=time.for_json()
                                    topic=msg_lst[3]+msg_lst[4]
                                    r.db('remember_bot').table('reminder').insert({"sender_id":sender_id, "time":time,"active":1,"topic":topic}).run(connection)
                                    t="Reminder is set on "
                                    t=t+str(_t.format('YYYY-MM-DD HH:mm:ss'))
                                    connection.close()
                                    send_message(sender_id,t)
                                    return "ok",200

                                if message_text.find("minutes")!=-1 or message_text.find("minute")!=-1:
                                    connection=r.connect("localhost",28015)

                                    delta=(msg_lst[-2])
                                    if delta=='one':
                                        delta=1
                                    elif delta=='two':
                                        delta=2
                                    elif delta=='three':
                                        delta=3
                                    elif delta=='four':
                                        delta=4
                                    elif delta=='five':
                                        delta=5
                                    elif delta=='six':
                                        delta=6
                                    elif delta=='seven':
                                        delta=7
                                    elif delta=='eight':
                                        delta=8
                                    elif delta=='nine':
                                        delta=9




                                    else:
                                        delta=int(msg_lst[-2])
                                    time=arrow.utcnow().to('Asia/Calcutta')

                                    
                                    time=time.replace(minutes=+delta)
                                    _t=time
                                    time=time.for_json()
                                    topic=msg_lst[3]+msg_lst[4]
                                    r.db('remember_bot').table('reminder').insert({"sender_id":sender_id, "time":time,"active":1,"topic":topic}).run(connection)
                                    t="Reminder is set on "
                                    t=t+str(_t.format('YYYY-MM-DD HH:mm:ss'))
                                    connection.close()
                                    send_message(sender_id,t)
                                    return "ok",200


                                if message_text.find("tomorrow")!=-1:
                                    if msg_lst[-1]=="tomorrow":
                                        connection=r.connect("localhost",28015)
                                        time=arrow.utcnow().to('Asia/Calcutta')
                                        time=time.replace(days=+1)
                                        _t=time
                                        time=time.for_json()
                                        topic=msg_lst[3]+" "+msg_lst[4]
                                        r.db('remember_bot').table('reminder').insert({"sender_id":sender_id, "time":time,"active":1,"topic":topic}).run(connection)
                                        t="Reminder is set on "
                                        t=t+str(_t.format('YYYY-MM-DD HH:mm:ss'))
                                        connection.close()
                                        send_message(sender_id,t)
                                        return "ok",200

                                        

                        ''' name '''
                        message_text.strip('?')
                        if message_text=="What's your name":
                            flag=1
                            send_message(sender_id,"I am remember bot")
                            return "ok",200

                        ''' search  '''

                        if msg_lst[0].lower()=="search":

                            flag=1
                            data=create_template(recipient=sender_id,search_title=message_text[7:])
                            if data=="Error":
                                send_message(sender_id,"Cannot find any result")
                            else:
                                send_message(sender_id,"Showing top three results from google")
                                send_message(sender_id,None,data)
                                return "ok",200

                        
                       
                            
                        ''' help '''
                        if msg_lst[0].lower()=="help" or msg_lst[0].lower()=="what can you do?"  or msg_lst[0].lower()=="what are your superpowers?" or msg_lst[0].lower()=="superpowers?":
                            flag=1
                            powers='''Hi , I am remember bot. I have the following superpowers.\n\nI can show you news from techcrunch. Just say "What's new in techcrunch?"\n\nI can search wiki . Just say "Wiki <search term>"\n\nI can tell you a joke, a quote, or a fact. Just ask me "Tell a joke".\n\nI can google search for you. Tell "Search <search term>"\n\nI can store your important posts. Say "Save ExamId 12345"\n\nI can remind you things too. Ex: Remind me to call anand after 10 minutes.\n\n'''



                            
                            send_message(sender_id,powers)
                            return "ok",200

                        if message_text.lower()=="thank you" or message_text.lower()=="thanks":
                            flag=1
                            send_message(sender_id,"Welcome")
                            return "ok",200

                            

                        ''' chat functions '''

                        if flag==0:
                            flag=1
                            if len(msg_lst)>0:
                                global _chatbot_agent
                                if _chatbot_agent==None:
                                    _chatbot_agent=initialize_bot()

                                reply=ask_bot(message_text,_chatbot_agent)

                                send_message(sender_id,reply)
                                return "ok",200
                            else:
                                send_message(sender_id,"I don't understand your question. Sorry..")
                                return "ok",200

                        #return "ok", 200
                    else:
                          # the message's text
                        send_message(sender_id,"Thank you :)")
                        return "ok",200


                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass
        print("Ok")
        return "ok",200


def send_message(recipient_id, message_text,data=None):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    #remember bot
    params = {
        "access_token": "EAAPJyQPXUXMBAHcfCZChSIaJzaNahe04jsGkBSdlhTz637ZA3rUmBcUXJ6cQKbOVmLUAfSLT4hA5zY5ZCfi2Lv6uk7lTxKM5OT29nHMhrNJSOq0lzZCSeftHAPnt7CPdiTCZAsVi4Vdnc4li83Ml0MbloINZCJmFZCItKD9e7IYZCwZDZD"
    }
    # params = {
    #      "access_token": "EAAPJyQPXUXMBABoBaAiDgOTpa8RgZBNNzUqkyYqIkipL7ZBvrbeZB0ZAziTeMqqmiJSFTZAjF27NeApDl8zZBBwP5t3s8mZAVjZBnLB6pHH2LgiYjaQDDnKETPZBLy6QXTmsmBsSQYM7AQenKIHUzW8e01ayaZA7MxXUCtNYOsSaP40AZDZD"
    #      }
    headers = {
        "Content-Type": "application/json"
    }
    
    #data=generic_template()
    data2 = json.dumps({
        "recipient": {
            "id": recipient_id
        },
      
        "message": {
            "text": message_text
        }
    })
    if data==None:
        data=data2


    send_writing(recipient_id)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
    else:
        print("Code:")
        log(r.status_code)


def log(message):  # simple wrapper for logging to stdout on heroku
    print( str(message))
    sys.stdout.flush()









def generic_template(url,img_url,title,sub_title,fall_back_url,btn_url,btn_title,recipient):
    #   data2=json.dumps({
    #     "recipient": {
    #           "id": recipient_id
    #       },
     
    #       "message":{
    #   "attachment":{
    #     "type":"template",
    #     "payload":{
    #       "template_type":"generic",
    #       "elements":[
    #          {
    #           "title":"Welcome to Peter\'s Hats",
    #           "image_url":"http://www.villagehatshop.com/photos/product/standard/4511390S61417/mens-hats/mj-panama-straw-outback-hat.jpg",#"https://petersfancybrownhats.com/company_image.png",
    #           "subtitle":"We\'ve got the right hat for everyone.",
    #           "default_action": {
    #             "type": "web_url",
    #             "url": "https://techcrunch.comview?item=103",
    #             "messenger_extensions": True,
    #             "webview_height_ratio": "tall",
    #             "fallback_url": "https://techcrunch.com"
    #           },
    #           "buttons":[
    #             {
    #               "type":"web_url",
    #               "url":"https://petersfancybrownhats.com",
    #               "title":"View Website"
    #             },{
    #               "type":"postback",
    #               "title":"Start Chatting",
    #               "payload":"DEVELOPER_DEFINED_PAYLOAD"
    #             }              
    #           ]      
    #         }
    #       ]
    #     }
    #   }
    # }

    #       })

    data2=json.dumps({
        "recipient": {
              "id": recipient
          },
     
          "message":{
      "attachment":{
        "type":"template",
        "payload":{
          "template_type":"generic",
          "elements":[
             {
              "title":title,
              "image_url":img_url,#"https://petersfancybrownhats.com/company_image.png",
              "subtitle":sub_title,
              "default_action": {
                "type": "web_url",
                "url": url,
                "messenger_extensions": True,
                "webview_height_ratio": "tall",
                "fallback_url": fall_back_url
              },
              "buttons":[
                {
                  "type":"web_url",
                  "url":btn_url,
                  "title":"Read more"
                }          
              ]      
            }
          ]
        }
      }
    }

          })

    print (data2)
    return data2





''' this function sends the typing bubble '''

def send_writing(recipient):

    data=json.dumps({
    "recipient":{
          "id":recipient
    },
    "sender_action":"typing_on"  
})  

    params = {
        "access_token": "EAAPJyQPXUXMBAHcfCZChSIaJzaNahe04jsGkBSdlhTz637ZA3rUmBcUXJ6cQKbOVmLUAfSLT4hA5zY5ZCfi2Lv6uk7lTxKM5OT29nHMhrNJSOq0lzZCSeftHAPnt7CPdiTCZAsVi4Vdnc4li83Ml0MbloINZCJmFZCItKD9e7IYZCwZDZD"
    }
    headers = {
        "Content-Type": "application/json"
    }

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)





''' DATABASE QUERIES '''

def save_post(sender_id,key,value):
    connection=r.connect("localhost",28015)
    res=r.db('remember_bot').table('post').insert({'sender_id':sender_id, 'key':key,'value':value} ).run(connection)
    connection.close()
    return res


def get_post(sender_id,key):
    key=key.lower()
    connection=r.connect("localhost",28015)
    res=list(r.db('remember_bot').table('post').filter((r.row['sender_id']==sender_id) & (r.row['key']==key) ).run(connection))
    return (res)



''' JOKE , FACT ,QUOTE FUNCTIONS '''


def get_jokes():
    t=randint(0,len(jokes))
    return jokes[t]



def get_fact():
    t=randint(0,len(facts))
    return facts[t]

def get_quote():
    t=randint(0,len(quotes))
    return quotes[t]


'''-------------------------------------------------'''


'''  REMINDER SUPPORTING FUNCTIONS '''

 


