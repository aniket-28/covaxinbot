from middleware import Middleware
from BotFactory import BotFactory
from database_handler import Database_Handler
import os
import dotenv
from pymongo import MongoClient


class DB_Listener:

    def __init__(self) -> None:
    
        dotenv.load_dotenv()
        self.MONGO_URL = os.getenv('MONGO_URL')
        self.middleware = Middleware()

        self.client = MongoClient( self.MONGO_URL, ssl=True, ssl_cert_reqs='CERT_NONE')
        self.bot_db = self.client['bot_db']
        self.user_db = self.client['user_db']
        self.processed_db = self.client['processed-db']


    def db_change_listener(self):
        print(f"Listening DB Changes !")
        pipeline = [{
                '$match': {
                'operationType': {'$in': ['insert', 'update']}
                    }
                    }]
        with self.processed_db.watch(pipeline, full_document='updateLookup') as stream:
            try:
                for change in stream:
                    print(change)
                    pincode = str(change["fullDocument"]["pincode"])
                    print(f"Pincode : {pincode}")
                    users = self.get_users_list(pincode)
                    print(f"Users : {users}")
                    self.broadcast_message(users, int(pincode))

            except Exception as e:
                print(e)

    def get_users_list(self, pincode):
        with Database_Handler() as db:
            return db.get_subscribed_users(pincode)
    

    def broadcast_message(self, users, pincode):
        bot = BotFactory().get_bot_instance()
        response = None

        with Database_Handler() as db:
            response = db.get_pincode_data(pincode)
            print(f'Response : {response}')
            response = self.middleware.format_cal_results(response)

        for user_id in users:
            try:
                if response != None:
                    bot.send_message(user_id, response)
            except Exception as e:
                print(e)

if __name__ == '__main__':
    db_listener = DB_Listener()
    db_listener.db_change_listener()