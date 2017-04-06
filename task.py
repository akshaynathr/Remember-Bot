import schedule
import time
import threading
import rethinkdb as r
from send_sms import sendSms
import sys
import json
import requests
import arrow
import datetime

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


''' -----------------------------------------------------------------------------'''


def fetch(erew):
	
	connection=r.connect('localhost',28015)
	reminders=list(r.db('remember_bot').table('reminder').filter(((r.row["active"]==1))).run(connection))
	cur_time=arrow.utcnow().to('Asia/Calcutta')
	print (reminders)
	print(cur_time)
	for i in reminders:
		sender_id=i["sender_id"]
		topic=i["topic"]
		text="Hi you asked to me to remind you about "
		_time=i["time"]
		y=arrow.get(_time)
		delta=y-cur_time
		if (delta<datetime.timedelta(0,0,0,1)):
			text=text + topic
			r.db('remember_bot').table('reminder').filter({"sender_id":sender_id,"active":1,"time":_time}).update({"sender_id":sender_id,"active":0,"time":_time}).run(connection)
			send_message(sender_id,text)	

	connection.close()	


def job():
    print("I'm running on thread %s" % threading.current_thread())
    send_message('1090822354356813',"Hello")


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


schedule.every(10).seconds.do(fetch, None)
 

while 1:
    schedule.run_pending()
    time.sleep(1)


