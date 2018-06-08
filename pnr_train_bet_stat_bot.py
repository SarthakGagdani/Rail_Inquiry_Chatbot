import json
import requests
import time
import urllib
import datetime

last_update_id = None
TOKEN = "559214243:AAHtWX3XkY1z7ioTa-wG7Z6FFKlB6oCZBik"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
api="u5kx6jxvi3"

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


def train_bet_station(src,dest,chat):
    date=datetime.date.today().strftime("%d-%m-%Y")
    bet_url="https://api.railwayapi.com/v2/between/source/{}/dest/{}/date/{}/apikey/{}/".format(src,dest,date,api)
    data=get_json_from_url(bet_url)
    if data['trains']:
        tot_trains="Trains available-"+str(data['total'])
        send_message(tot_trains,chat)
        y=1
        for x in data['trains']:
            name=str(y)+">"+x['name']+"\n"
            from_stat=x['from_station']['name']
            to_stat=x['to_station']['name']
            
            sdt="Source Departure-"+x['src_departure_time']
            dat="Destination Arrival-"+x['dest_arrival_time']
            tt="Travel time-"+x['travel_time']
            send_message((name+"\n"+from_stat+" to "+to_stat+"\n"+sdt+"\n"+dat+"\n"+tt),chat)
            y=y+1
        
    else:
        send_message("No trains between stations.",chat)

        
    

def get_rail_pnr_status(pnr,chat):
    pnr_url="https://api.railwayapi.com/v2/pnr-status/pnr/{}/apikey/{}/".format(pnr,api)
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
        
def last_msg():
    global last_update_id
    updates = get_updates(last_update_id)
    if len(updates["result"]) > 0:
        last_update_id = get_last_update_id(updates) + 1
        for update in updates["result"]:
            msg= update["message"]["text"]
            return msg
    
    
def reply(updates):
    
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        
        if text=="/start":
            text1="Hello,WELCOME to this Indian Rail Services BOT!!"
            send_message(text1, chat)
            send_message("Choose Services-\n1.PNR Status\n2.Train Between Stations",chat)
            
        elif text=='1':
            text2="Please Enter your 10 DIGIT Indian railways PNR NO- "
            send_message(text2, chat)
            
        elif text=='2':
            send_message("Enter Source Station Code-",chat)
            src=last_msg()
            send_message("Enter Destination Station Code-",chat)
            dest=last_msg()
            train_bet_station(src,dest,chat)
            
        elif text.isdigit()and len(text)==10:
            text_pass="Okay,checking your STATUS-"
            send_message(text_pass, chat)
            get_rail_pnr_status(text,chat)
            
       
        elif text.isalpha():
            text_error2="I am not a CHAT BOT!!Please Enter valid Option-"
            send_message(text_error2, chat)
            send_message("Choose Services-\n1.PNR Status\n2.Train Between Stations",chat)
            
        else: 
            text_error1="Ooops wrong Option,Please Enter valid Option-"
            send_message(text_error1, chat)
            send_message("Choose Services-\n1.PNR Status\n2.Train Between Stations",chat)
        
        
def main():
    global last_update_id
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            reply(updates)
        time.sleep(0.5)
       

if __name__ == '__main__':
    main()


    