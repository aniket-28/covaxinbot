import requests
from fake_useragent import UserAgent
from datetime import date

 

class COWIN_API:
    def __init__(self):
        self.BASE_URL = 'https://cdn-api.co-vin.in/api'
        # self.BASE_URL = 'https://5f5c38f7-6548-4c29-a0ce-fba0461312b5.mock.pstmn.io'
        self.AGENT = UserAgent()
        self.current_date = self.get_current_date()
        self.HEADER =  {'User-Agent': self.AGENT.random}

    def get_current_date(self):
        today = date.today()
        d = today.strftime("%d-%m-%Y")
        return d

    def getStatesApi(self):
        api_url = self.BASE_URL+"/v2/admin/location/states"
        # agent = UserAgent()
        # header = {'User-Agent': agent.random}
        res = requests.get(api_url, headers=self.HEADER)
        text = 'COWIN API not responding'
        if res.status_code != 200:
            raise Exception('{} {}'.format(api_url, res.content))

        states = {}

        for i in res.json()['states']:
            states[i['state_id']] = i['state_name']

        return states

    def get_districts(self, state_id):
        api_url = self.BASE_URL+ f"/v2/admin/location/districts/{state_id}"
        # agent = UserAgent()
        # header = {'User-Agent': agent.random}
        res = requests.get(api_url, headers=self.HEADER)
        # print(res.json())
        text = 'COWIN API not responding'
        if res.status_code != 200:
            raise Exception('{} {}'.format(api_url, res.content))

        districts = {}

        for i in res.json()['districts']:
            districts[i['district_id']] = i['district_name']

        return districts

    def get_vaccine_by_pincode_api(self, pincode):
        api_url = self.BASE_URL + "/v2/appointment/sessions/public/findByPin"

        params = {"pincode": pincode,
                  "date": self.get_current_date()}

        res = requests.get(api_url, params=params, headers=self.HEADER)

        try:
            data = res.json()
            # print(f"Response : {data}")
            return data
        except Exception as e:
            print(e)

        return "COWIN - API not responding!"

        # return res.json()

    def get_vaccine_by_district_api(self, district_id):
        api_url = self.BASE_URL + "/v2/appointment/sessions/public/findByDistrict"

        params = {
            "district_id": district_id,
            "date": self.get_current_date()
        }

        res = requests.get(api_url, params=params, headers=self.HEADER)

        try:
            data = res.json()
            # print(f"Response : {data}")
            return data
        except Exception as e:
            print(e)

        return "COWIN - API not responding!"

    def get_vaccine_by_pincode_cal_api(self, pincode, date=date.today().strftime("%d-%m-%Y")):
        # agent = UserAgent()
        # header = {'User-Agent': agent.random}
        api_url = self.BASE_URL + "/v2/appointment/sessions/public/calendarByPin"

        params = {"pincode": pincode,
                  "date": date}

        res = requests.get(api_url, params=params, headers=self.HEADER)
    
        try:
            data = res.json()
            # print(f"Response : {data}")
            return data
        except Exception as e:
            print(e)

        return "COWIN - API not responding!"

    def get_vaccine_by_district_cal_api(self, district_id, date=date.today().strftime("%d-%m-%Y")):
        # agent = UserAgent()
        # header = {'User-Agent': agent.random}
        print("Hitting Core Api")

        api_url = self.BASE_URL + "/v2/appointment/sessions/public/calendarByDistrict"

        params = {"district_id": district_id,
                  "date": date}

        res = requests.get(api_url, params=params, headers=self.HEADER)

        try:
            data = res.json()
            # print(f"Response fom API: {data}")
            return data
        except Exception as e:
            print(e)

        return "COWIN - API not responding!"

    def get_geo_data(self):
        states = self.getStatesApi()
        data = {}
        for state_id , state_name in states.items():
            districts = self.get_districts(state_id)
            data.update({state_id : { "state_name":state_name, "districts" : districts} })

        # print(data)
        return data

# /v2/appointment/sessions/public/calendarByPin

# call = COWIN_API()

# results = []

# states =  {1: 'Andaman and Nicobar Islands', 2: 'Andhra Pradesh', 3: 'Arunachal Pradesh', 4: 'Assam', 5: 'Bihar', 6: 'Chandigarh', 7: 'Chhattisgarh', 8: 'Dadra and Nagar Haveli', 37: 'Daman and Diu', 9: 'Delhi', 10: 'Goa', 11: 'Gujarat', 12: 'Haryana', 13: 'Himachal Pradesh', 14: 'Jammu and Kashmir',
        #    15: 'Jharkhand', 16: 'Karnataka', 17: 'Kerala', 18: 'Ladakh', 19: 'Lakshadweep', 20: 'Madhya Pradesh', 21: 'Maharashtra', 22: 'Manipur', 23: 'Meghalaya', 24: 'Mizoram', 25: 'Nagaland', 26: 'Odisha', 27: 'Puducherry', 28: 'Punjab', 29: 'Rajasthan', 30: 'Sikkim', 31: 'Tamil Nadu', 32: 'Telangana', 33: 'Tripura', 34: 'Uttar Pradesh', 35: 'Uttarakhand', 36: 'West Bengal'}

# districts = {}
# data = {}
# results = {}
# for state_id , state_name in states.items():
#     print(f"{state_id} : {state_name}")
#     districts = call.get_districts(state_id)
#     print(districts)

#     results.update({state_id : {
#         'state_id': str(state_id),
#         'state_name': state_name,
#         'districts' : districts
#     }})

# print("\n\n\n"+ "---"*30)
# pprint.pprint(results)


# print(call.get_districts(21))
# print(call.getStatesApi())
# print("\n\n")
# call.get_vaccine_by_pincode_api(400001)
# print("\n\n")
# call.get_vaccine_by_district_api(1100)
# print("\n\n")
# call.get_vaccine_by_pincode_cal_api(400001, call.get_current_date())
# print("\n\n")
# call.get_vaccine_by_district_cal_api(1100, call.get_current_date())

# states =  {1: 'Andaman and Nicobar Islands', 2: 'Andhra Pradesh', 3: 'Arunachal Pradesh', 4: 'Assam', 5: 'Bihar', 6: 'Chandigarh', 7: 'Chhattisgarh', 8: 'Dadra and Nagar Haveli', 37: 'Daman and Diu', 9: 'Delhi', 10: 'Goa', 11: 'Gujarat', 12: 'Haryana', 13: 'Himachal Pradesh', 14: 'Jammu and Kashmir',
#            15: 'Jharkhand', 16: 'Karnataka', 17: 'Kerala', 18: 'Ladakh', 19: 'Lakshadweep', 20: 'Madhya Pradesh', 21: 'Maharashtra', 22: 'Manipur', 23: 'Meghalaya', 24: 'Mizoram', 25: 'Nagaland', 26: 'Odisha', 27: 'Puducherry', 28: 'Punjab', 29: 'Rajasthan', 30: 'Sikkim', 31: 'Tamil Nadu', 32: 'Telangana', 33: 'Tripura', 34: 'Uttar Pradesh', 35: 'Uttarakhand', 36: 'West Bengal'}


# for state_id, name in states.items():
#     print(f"{state_id}. {name}")
