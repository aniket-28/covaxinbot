from middleware import Middleware
from database_handler import Database_Handler
from vaccine_api import COWIN_API
import telebot
import os
import dotenv


# dotenv.load_dotenv()
# API_KEY = os.getenv('API_KEY')
# bot = telebot.TeleBot(API_KEY)
# middleware = Middleware()
# api = COWIN_API()
# option_selected = {}
# data = {}

dotenv.load_dotenv()
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)

def init_bot():
    print("Initializing bot data")
    global data, middleware, api, data, option_selected
        # print(data)


    middleware = Middleware()
    api = COWIN_API()
    data = api.get_geo_data()
    option_selected = {}



@bot.message_handler(commands=['Hi', 'Hello', 'hello', 'hi'])
def greet(message):
    bot.reply_to(message, "Hi How can I help you ?")


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        print(f"\n\n User : {message.from_user}")
        with Database_Handler() as db:
            db.register_user(message.from_user)

        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        options = ["Find Vaccine By Pincode", "Find Vaccine By District", "Notify Me"]
        print(f"Options : {options}")
        for option in options:
            keyboard.add(telebot.types.KeyboardButton(option))
        bot.send_message(message.chat.id, 'Hello!', reply_markup=keyboard)

    except Exception as e:
        print(e)


def load_states_keyboard(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    select_user_option(message, 'state')
    print(f"Loading States keyboard ")
    for state_id, bundle in data.items():
        states_button = telebot.types.InlineKeyboardButton(
            text=bundle['state_name'], callback_data=f"state:{state_id}")
        keyboard.add(states_button)

    bot.send_message(message.chat.id, 'Select State', reply_markup=keyboard)


def load_districts_keyboard(cbquery, state_id):
    select_user_option(cbquery.message, 'district')
    # option_selected[cbquery.message.chat.id]['state'] = True
    keyboard = telebot.types.InlineKeyboardMarkup()

    selected = int(state_id)
    print(
        f"Load Districts Keyboard Selected option : {data.get(selected)['state_name']}")
    districts = data.get(selected)['districts']

    for district_id, district_name in districts.items():
        districts_button = telebot.types.InlineKeyboardButton(
            text=district_name, callback_data=f"state:{state_id}:district:{district_id}")
        keyboard.add(districts_button)

    bot.send_message(cbquery.message.chat.id,
                     'Select District', reply_markup=keyboard)


def get_user_option(message, option, data=None):

    split_key = {'state': 0, 'district':2}

    try:
        if option in ['state', 'district'] and data != None:
            return option == data.split(':')[split_key[option]]
        return option_selected[message.chat.id][option]
    except Exception as e:
        print(e)
    return False

def select_user_option(message, option):
    option_selected.update({message.chat.id : {
        'pincode' : False,
        'state' : False,
        'district' : False,
        'getAlert': False
    }})

    option_selected[message.chat.id][option] = True

def send_message(message, text):
    print(f"Sending Custom Message len : {len(text)}")
    if len(text) > 2200:
        print('Message Larger than Limit')
        msg_list = text.split('------------------------------------------------------------')
        
        for msg in msg_list:
            if msg != '':
                bot.send_message(message.chat.id, msg, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, text, parse_mode='Markdown')


@bot.callback_query_handler(func= lambda m : get_user_option(m.message, 'district', m.data))
def district_option_callback(cbquery):

    option_selected[cbquery.message.chat.id]['district'] = False
    print("District callback query")

    state_id = int(cbquery.data.split(":")[1])
    district_id = cbquery.data.split(":")[3]
    try:
        print( f"Selected option : {data.get(state_id)['districts'][int(district_id)]}")
        # cal_vaccine_slots_json = api.get_vaccine_by_district_cal_api( district_id )
        # print(f"Vaccine Slots : {cal_vaccine_slots_json}")
        
        cal_vaccine_slots_json = middleware.find_vaccine_by_district(district_id)
        print(f"cal_vaccine_slot : {cal_vaccine_slots_json}")

        vac_data = 'No Slots'

        if cal_vaccine_slots_json != None:
            vac_data = middleware.format_cal_results(cal_vaccine_slots_json)
        
        print(f"\n\n VacData : {vac_data}\n\n")
        # bot.send_message(cbquery.message.chat.id, vac_data, parse_mode='Markdown')

        send_message(cbquery.message, vac_data)
    
    except Exception as e:
    
        print(f"\n\n------------\n\n{e}")
        bot.send_message(cbquery.message.chat.id, "No Slots")


def find_vaccine_by_pincode(message, pincode):
    if pincode == 'find vaccine by district':
        # select_user_option(message, 'district')
        load_states_keyboard(message)
    
    if pincode== 'notify me':
        # select_user_option(message, 'getAlert')
        subscribe_to_notification(message)

    vac_data = 'No Data'
    try:
        # option_selected[message.chat.id]['pincode'] = False
        print(f"Pincode : {pincode}")
        # vac_json = api.get_vaccine_by_pincode_cal_api(pincode)
        vac_json =  middleware.find_vaccine_by_pincode(pincode)
        print(f"Vac_JSON : {vac_json}")
        
        if vac_json != None:
            vac_data = middleware.format_cal_results(vac_json)
    except Exception as e:
        print(e)
        vac_data = None
    select_user_option(message, 'reset')
    return vac_data


@bot.callback_query_handler(func=lambda a: get_user_option(a.message, 'state', a.data))
def states_option_callback(cbquery):
    selected = -1

    try:
        selected = int(cbquery.data.split(":")[1])
        print(f"Selected option : {data.get(selected)['state_name']}")
        print(f"Data Passed : {cbquery.data}")
        load_districts_keyboard(cbquery, selected)

    except:
        bot.send_message(cbquery.message.chat.id, "Invalid Option")

def subscribe_to_notification(message):
    text = message.text.lower()
    reply = "Incorrect Pincode"
    if str.isdecimal(text):
        print(f"Pincode Valid : {text}")
        reply = 'Error Occured'
        with Database_Handler() as db:
            db.subscribe_alerts_to_user(message.from_user, text)
            reply = f"Registered Pincode : {text}"
    bot.send_message(message.chat.id, reply)

@bot.message_handler()
def get_message(message):
    try:
        text = message.text.lower()

        global option_selected
        print(text)

        bot_response = "Select a valid option"

        if text == "find vaccine by pincode":
            select_user_option(message, 'pincode')
            bot_response = "Enter Pincode"
            bot.send_message(message.chat.id, bot_response)

        elif get_user_option(message, 'pincode'):
            vac_data = find_vaccine_by_pincode(message, text)
            bot.send_message(message.chat.id, vac_data, parse_mode='Markdown')

        elif text == 'find vaccine by district':
            select_user_option(message, 'state')
            load_states_keyboard(message)

        elif text== 'notify me':
            select_user_option(message, 'getAlert')
            bot.send_message(message.chat.id, "Enter the pincode to get Alerts")

        elif get_user_option(message, 'getAlert'):
            print("Subscribing User")
            subscribe_to_notification(message)
            
    
    except Exception as e:
        print(e)


def bot_main():
    init_bot()
    bot.polling()

if __name__=='__main__':
    bot_main()

# def api_test():
#   api_url = 'https://cdn-api.co-vin.in/api/v2/admin/location/states'
#   res = requests.get(api_url)
#   if res.status_code != 200:
#     raise Exception('{} {}'.format(api_url, res.content))

#   for i in res.json():
#     print(i)

# api_test()
