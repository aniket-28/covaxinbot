import os
import dotenv
from database_handler import Database_Handler


class Middleware:

    def __init__(self) -> None:
        dotenv.load_dotenv()
        self.district_start_id = int(os.getenv('district_start_id'))
        self.district_end_id = int(os.getenv('district_end_id'))

    def format_cal_results(self, cal_vaccine_slots_json):
        vac_data = ''
        center_data = ''
        for center in cal_vaccine_slots_json['centers']:
            center_data = ''
            
            center_data += f"\n\n*{center['name']}, {center['district_name']}*\n\n"
            center_data += f"Pincode : *{center['pincode']}*\n"
            center_data += f"Charges :  *{center['fee_type']}*\n"

            count = 0
            for session in center['sessions']:
                temp = ''
                temp += f"\nDate : *{session['date']}*\n"
                temp += f"Vaccine : *{session['vaccine']}*\n"
                temp += f"Age : *{session['min_age_limit']}+*\n"
                vc = session['available_capacity']
                temp += f"Available : *{vc}*\n"
                
                if vc > 0:
                    count += 1
                    center_data += temp
            center_data += '---'*20
            if count > 0:
                vac_data += center_data
        if vac_data == '':
            vac_data = 'No Slot!'
        return vac_data

    def format_results(self, vaccine_slots_json):
        vac_data = ''
        for session in vaccine_slots_json['sessions']:
            vac_data += '---'*20
            vac_data += f"\n\n*{session['name']}, {session['district_name']}*\n\n"
            vac_data += f"{'Pincode : '}*{session['pincode']}*\n"
            vac_data += f"{'Vaccine : '} *{session['vaccine']}*\n"
            vac_data += f"{'Charges : '} {session['fee_type']} \n"
            vac_data += f"{'Age : '} *{session['min_age_limit']}+*\n"
            vac_data += f"{'Date : '} *{session['date']}*\n"
            vac_data += f"{'Available : '} *{session['available_capacity']}*\n"
            vac_data += f"{'Address : '} {session['address']}\n"
        
        return vac_data

    
    def find_vaccine_by_district(self, district_id):
        with Database_Handler() as db_handler:
            return db_handler.get_district_data(district_id)

    def find_vaccine_by_pincode(self, pincode):
        with Database_Handler() as db_handler:
            return db_handler.get_pincode_data(pincode)



    def refresh_api_data(self):
        print("Data Refresh Invoked")
        with Database_Handler() as db_handler:
            try:
                for district_id in range(self.district_start_id, self.district_end_id + 1):
                    print(f"Running for : {district_id}")
                    db_handler.upload_district_api_data(district_id)
            except Exception as e:
                print(e)

    def register_user(message):
        with Database_Handler() as db:
            db.register_user(message.from_user)
