
from google import search
import json

# def Search(sentence,_stop):
#     res=search(sentence,stop=int(_stop))
#     return res

#"image_url": "https://techcrunch.comimg/collection.png",
                    # "subtitle": "See all our colors",
def create_template(recipient,search_title):
    
    res=search(search_title,stop=3)
    if res==None:
        print ("Error in search result")
        return "Error"
    else:
        data=list_template(recipient)
        count=0
        for url in res:
            count=count+1
            if len(url)==0:
                break
            d={
                    "title": search_title,
                    "image_url":"https://yt3.ggpht.com/-v0soe-ievYE/AAAAAAAAAAI/AAAAAAAAAAA/OixOH_h84Po/s900-c-k-no-mo-rj-c0xffffff/photo.jpg",
                    
                    "subtitle":url,
                    
                    "buttons": [
                        {
                            "title": "View result",

                            "type": "web_url",
                            "url": url
                                                   
                        }
                    ]
                }
            if count==5:
                break
            
            # d['title']=search_title
            # d['buttons'][0]['url']=url

            data["message"]["attachment"]["payload"]["elements"].append(d)

        print("Count:")
        print(count)

        print(data)

        return json.dumps(data)








def list_template(recipient):
    data=   {
    "recipient":{
    "id":recipient
    }, "message": {
    "attachment": {
        "type": "template",
        "payload": {
            "template_type": "list",
            "elements": [
                 
            ] 
        }
    }
    }
    


}   


    return (data)