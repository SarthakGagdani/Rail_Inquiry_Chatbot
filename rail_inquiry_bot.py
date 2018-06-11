import json
import requests
import time
import urllib
from datetime import datetime, timedelta

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

def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)
    
    
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def station_to_code(station):
    code_url="https://api.railwayapi.com/v2/name-to-code/station/{}/apikey/{}/".format(station.upper(),api)
    data=get_json_from_url(code_url)
    if data['stations']:
        for x in data['stations']:
            if x['name'].split()[0]==station.upper():
                return x['code']
    else:
        return 'err'
        
def train_bet_station(chat):
    send_message("Enter Source Station-",chat)
    src=station_to_code(last_msg())
    send_message("Enter Destination Station-",chat)
    dest=station_to_code(last_msg())
    
    if src=='err' or dest=='err':
        send_message("Wrong Station Name",chat)
        send_message("Enter Source Station-",chat)
        src=station_to_code(last_msg())
        send_message("Enter Destination Station-",chat)
        dest=station_to_code(last_msg())
        if src=='err' or dest=='err':
            send_message("Wrong Station Name",chat)
            return

    date=datetime.now().strftime("%d-%m-%Y")
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
        send_message("Wrong PNR.",chat)
        
def last_msg():
    global last_update_id
    updates = get_updates(last_update_id)
    if len(updates["result"]) > 0:
        last_update_id = get_last_update_id(updates) + 1
        for update in updates["result"]:
            msg= update["message"]["text"]
            return msg
        
def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def live_train_status(train_no,chat):
    items=['Today','Yesterday']
    keyboard = build_keyboard(items)
    send_message("Train start date?",chat,keyboard)
    date1=last_msg()
    
    if date1=='Today':
        date=datetime.now().strftime("%d-%m-%Y")
    else:
        date=(datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y")
        
    status_url="https://api.railwayapi.com/v2/live/train/{}/date/{}/apikey/{}/".format(train_no,date,api)
    data=get_json_from_url(status_url)
    
    if data['position']:
        send_message(data['position'],chat)
    else:
        send_message("Oops!!No such train available",chat)
        
def reply(updates):
    
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        sender_name=update["message"]["chat"]["first_name"]
        menu_msg="Choose Services-\n1.PNR Status\n2.Train Between Stations\n3.Live Train Status\n\nPress 4 to Exit."
        
        if text=="/start":
            send_message("HELLO "+sender_name+",\nWELCOME to this Indian-Rail-Enquiry BOT.",chat)
            send_message(menu_msg,chat,build_keyboard(['1','2','3','4']))
            
        elif text=='1':
            send_message("Please Enter your 10 DIGIT Indian railways PNR NO- ", chat)
            pnr_no=last_msg()
            if pnr_no.isdigit()and len(pnr_no)==10:
                send_message("Okay,checking your STATUS-", chat)
                get_rail_pnr_status(pnr_no,chat)
            else:
                send_message("Wrong PNR.",chat)
                
            send_message(menu_msg,chat,build_keyboard(['1','2','3','4']))
            
        elif text=='2':
            train_bet_station(chat)
            send_message(menu_msg,chat,build_keyboard(['1','2','3','4']))
          
        elif text=='3':
            send_message("Enter Train Number-",chat)
            train_no=last_msg()
            if train_no.isdigit():
                live_train_status(train_no,chat)
            else:
                send_message("Ufff..I am not a CHATBOT!!",chat)
            send_message(menu_msg,chat,build_keyboard(['1','2','3','4']))
            
        elif text=='4':
            send_message("THANK YOU for using this bot,press \"/start\" to use services again.\nBye!",chat)
            
        elif text.isalpha():
            send_message("Ufff..I am not a CHATBOT!!",chat)
            send_message(menu_msg,chat,build_keyboard(['1','2','3','4']))
            
        else: 
            send_message("Something went wrong!", chat)
            send_message(menu_msg,chat,build_keyboard(['1','2','3','4']))
        
        
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


    