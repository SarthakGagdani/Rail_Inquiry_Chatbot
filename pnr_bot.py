import json
import requests
import time
import urllib

TOKEN = #get it from the BotFather in telegram app
#<api_key> Not mentioned.
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)
    
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def get_rail_pnr_status(pnr,chat):
    pnr_url="https://api.railwayapi.com/v2/pnr-status/pnr/{}/apikey/<api_key>/".format(pnr)
    data=get_json_from_url(pnr_url)
    if data['passengers']:
        
        train_name="Train:"+data['train']['name']
        train_no="No:"+data['train']['number']
        pnr_no="PNR:"+data['pnr']
        doj="Date:"+data['doj']
        pass_no="Passengers:"+str(data['total_passengers'])
        
        if data['chart_prepared']:
            chart_stat="Chart Prepared."
        else:
            chart_stat="Chart Not Prepared."
            
        from_st="From:"+data['from_station']['name']
        to_st="To:"+data['to_station']['name']
        class_coach="Class:"+data['journey_class']['code']
        
        for x in data['passengers']:
            y=1
            curr_stat="Current Stat:"+x['current_status']
            book_stat="Booking Stat:"+x['booking_status']
            send_message(("Passenger "+str(y)+":"+"\n"+book_stat+"\n"+curr_stat),chat)
            y=y+1
            
        send_message(("Other Details-\n\n"+pnr_no+"\n"+train_name+"\n"+train_no+"\n"+doj+"\n"+pass_no+"\n"+from_st+"\n"+to_st+"\n"+class_coach+"\n"+chart_stat),chat)
    else:
        send_message("Wrong PNR.Enter correct PNR.",chat)
    
def reply(updates):
    
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        
        if text=="/start":
            text1="Hello,WELCOME to this PNR BOT!!"
            send_message(text1, chat)
            text2="Please Enter your 10 DIGIT Indian railways PNR NO- "
            send_message(text2, chat)
            
        elif text.isdigit()and len(text)==10:
            text_pass="Okay,checking your STATUS-"
            send_message(text_pass, chat)
            get_rail_pnr_status(text,chat)
            
       
        elif text.isalpha():
            text_error2="I am not a CHAT BOT!!Please Enter a valid 10 DIGIT PNR NO-"
            send_message(text_error2, chat)
            
        else: 
            text_error1="Ooops wrong PNR,Enter 10 DIGIT PNR NO-"
            send_message(text_error1, chat)
        
        
def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            reply(updates)
        time.sleep(0.5)
       

if __name__ == '__main__':
    main()


    
