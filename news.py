import json
import requests
token="ee8fca01e8104b02a2271f0ad908fad1"


def get_news():
  r = requests.get(" https://newsapi.org/v1/articles?source=techcrunch&apiKey=ee8fca01e8104b02a2271f0ad908fad1")

  if r.status_code != 200:
      print(r.status_code)

      return []

  else:
      return json.loads(r.text)



def news_generic_template(data,recipient):
  l=data['articles']
  d={}
  data2=news_generic_template_creator(recipient)
  for i in l:
      d={   "title":i['title'],
              "image_url":i['urlToImage'],#"https://petersfancybrownhats.com/company_image.png",
              "subtitle":i['description']#,
              # "default_action": {
              #   "type": "web_url",
              #   "url": "",
              #   "messenger_extensions": True,
              #   "webview_height_ratio": "tall",
              #   "fallback_url": ""
              # }
              ,
              "buttons":[
                {
                  "type":"web_url",
                  "url":i['url'],#"https://www.techcrunch.com",
                  "title":"Read story"
                },
                {
                   "type":"element_share"
                }                        
              ]      
        }
      data2["message"]["attachment"]["payload"]["elements"].append(d)
  return json.dumps(data2)


def news_generic_template_creator(recipient):
    
  data2={
        "recipient": {
              "id": recipient
          },
     
          "message":{
      "attachment":{
        "type":"template",
        "payload":{
          "template_type":"generic",
          "elements":[
              
          ]
            } 
          }
        }

          }
  return data2



def whitelist(data):
  t=[]
  l=data[0]["message"]["attachment"]["payload"]["elements"]
  for i in l:
    t.append(i['url'])

  params = {
        "access_token": "EAAPJyQPXUXMBAHcfCZChSIaJzaNahe04jsGkBSdlhTz637ZA3rUmBcUXJ6cQKbOVmLUAfSLT4hA5zY5ZCfi2Lv6uk7lTxKM5OT29nHMhrNJSOq0lzZCSeftHAPnt7CPdiTCZAsVi4Vdnc4li83Ml0MbloINZCJmFZCItKD9e7IYZCwZDZD"
    }
  headers = {
        "Content-Type": "application/json"
    }
  print (t)
  r=requests.post("https://graph.facebook.com/v2.6/me/thread_settings?",params=params,headers=headers,data=t)
  
