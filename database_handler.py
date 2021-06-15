
from vaccine_api import COWIN_API
from pymongo import MongoClient
import os
import dotenv
import pprint as pp


class Database_Handler:

    def __init__(self) -> None:
        dotenv.load_dotenv()
        self.MONGO_URL = os.getenv('MONGO_URL')

    def __enter__(self):
        self.client = MongoClient(
            self.MONGO_URL, ssl=True, ssl_cert_reqs='CERT_NONE')
        self.bot_db = self.client['bot_db']
        self.user_db = self.client['user_db']
        self.processed_db = self.client['processed-db']
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
        return False

    def upload_district_api_data(self, district_id , data=None):
        if data == None:
            api = COWIN_API()
            print("DBHandler upload district api_data")
            data = api.get_vaccine_by_district_cal_api(district_id)
        # print("--"*30)
        # print(f"API_DATA District {district_id}: {data}")
        search = {'district_id': district_id}
        update_value = {"district_id": district_id, "data": data}

        api_data = self.bot_db["api_data"]

        if data == {'centers' : []}:
            return

        result = api_data.find_one_and_update(search,
                                              {"$set": update_value},
                                              upsert=True)

        # print(result)

        # print(result['data'])

        return result


    def get_district_data(self, district_id):
        api_data = self.bot_db["api_data"]


        search = {'district_id': district_id} 
        print(f"Searching DB {search}  district_id : {type(district_id)}")
        cur = api_data.find(search)

        result = None
        for i in cur:
            result = i["data"]

        return result


    def get_pincode_data(self, pincode):
        api_data = self.bot_db["api_data"]
        pincode = int(pincode)
        print(f"Get Pincode Data for : {pincode} {type(pincode)}")
        search = [
            {"$unwind": '$data.centers'},
            {"$match": {'data.centers.pincode': pincode,
                        'data.centers.sessions.available_capacity': {'$gt': 0}
                        }}
        ]
        cur = api_data.aggregate(search)

        temp = []
        result = None
        for i in cur:
            temp.append(i["data"]["centers"])

        if len(temp) > 0:        
            result = {'centers': temp}
        
        # print(f'\n\nResult {result}')
        return result

    def register_user(self, user):

        print(user)
        users_collection = self.user_db["users"]
        print(f"Registering User : {user.id}")
        search = {"user_id": user.id}
        result = users_collection.find_one(search)
        print(f"Result : {result}")
        if result != None:
            return

        update_value = {
            'user_id': user.id,
            'user_name': user.username,
            'alert': False,
            'pincode': []
        }

        users_collection.find_one_and_update(search,
                                             {"$set": update_value},
                                             upsert=True)

 
    def aggregate_data(self, district_id):
        api = COWIN_API()
        api_data = api.get_vaccine_by_district_cal_api(district_id)
        # print(api_data)
        print("Back to Aggregate Data")

        self.upload_district_api_data(district_id, api_data)
        api_dict = {}
        for center in api_data['centers']:
            api_dict.update({'center_id': center['center_id'],
                             'center_name': center['name'], 
                             'district_name': center['district_name'],
                             'pincode': center['pincode'],
                             'district_id': district_id
                             })
            vc = 0
            for session in center['sessions']:
                vc += session["available_capacity"]
            api_dict.update({"available_capacity": vc})

        print(f"Api Data : {api_dict}")

        db_dict = {}

        db_data = [i for i in self.get_district_data_db(district_id)]

        if len(db_data) > 0:
            # print(f"Db Data : {db_data[0]}")
            db_dict = dict(db_data[0])
            print(f"Db Data : {db_dict}")

        if db_dict.get("available_capacity", -1) != api_dict.get("available_capacity", 0):
            print("Data MisMatch")
            if api_dict != {}:
                result = self.processed_db["agreegate"].find_one_and_update({'district_id': district_id},
                                                               {"$set": api_dict},
                                                               upsert=True)

                print(f"Updated Record : {result}")

    def get_district_data_db(self, district_id):
        search = {'district_id': district_id}
        return self.processed_db["agreegate"].find(search)


    def subscribe_alerts_to_user(self, user, pincode):
        print(f"Suscribing User Alert for Pincode {pincode} \n User : {user}")
        try:
            users_collection = self.user_db["users"]
            users_collection.find_one_and_update({'user_id': user.id},
                                                 {"$push": {'pincode': pincode}})
                                                #   {'$set': {'alert': True}})
        except Exception as e:
            print(e)


    def get_subscribed_users(self, pincode):
        data = self.user_db['users'].find( {'pincode': pincode} )
        print(f'\n\nData : {data}')
        users = []
        for user in data :
            users.append(user['user_id'])
        print(f"Users : {users}")
        return users

if __name__ == '__main__':
    with Database_Handler() as db:
        try:
            # users = db.get_subscribed_users('410203')
            db.aggregate_data("5")
            # db.get_subscribed_users('744205')
            # print(users)
        except Exception as e:
            print(e)
