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


dbSetUp()






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

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    
                    msg_lst=message_text.split(" ")



                    '''SAVE FUNCTIONS '''


                    if msg_lst[0].lower()=="save":
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

                                send_message(sender_id,None,data)





                    ''' SAY/TELL FUNCTIONs '''
                    if msg_lst[0].lower()=="say" or msg_lst[0].lower()=="tell":
                        if msg_lst[-1].lower()=="joke":
                            send_message(sender_id,get_jokes())

                        if msg_lst[-1].lower()=="fact":
                            send_message(sender_id,get_fact())

                        if msg_lst[-1].lower()=="quote":
                            send_message(sender_id,get_quote())





                            #send_message(sender_id, article.summary[:600])
                    else:
                        send_message(sender_id,"CHAT")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text,data=None):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": "EAAPJyQPXUXMBAHcfCZChSIaJzaNahe04jsGkBSdlhTz637ZA3rUmBcUXJ6cQKbOVmLUAfSLT4hA5zY5ZCfi2Lv6uk7lTxKM5OT29nHMhrNJSOq0lzZCSeftHAPnt7CPdiTCZAsVi4Vdnc4li83Ml0MbloINZCJmFZCItKD9e7IYZCwZDZD"
    }
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
    #             "url": "https://peterssendreceiveapp.ngrok.io/view?item=103",
    #             "messenger_extensions": True,
    #             "webview_height_ratio": "tall",
    #             "fallback_url": "https://peterssendreceiveapp.ngrok.io/"
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
    connection=r.connect("localhost",28015)
    res=list(r.db('remember_bot').table('post').filter((r.row['sender_id']==sender_id) & (r.row['key']==key) ).run(connection))
    return (res)




def get_jokes():
    t=randint(0,len(jokes))
    return jokes[t]



def get_fact():
    t=randint(0,len(facts))
    return facts[t]

def get_quote():
    t=randint(0,len(quotes))
    return quotes[t]