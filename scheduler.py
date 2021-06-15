from database_handler import Database_Handler
from middleware import Middleware
import schedule
import time
import os
import dotenv


class Scheduler:
    def aggregate_data(self):
        dotenv.load_dotenv()
        start = int(os.getenv('district_start_id'))
        end = int(os.getenv('district_end_id'))
        with Database_Handler() as db:
            for district_id in range(start, end+1):
                db.aggregate_data(str(district_id))


    def refresh_data(self):
        print("Job Invoked")
        Middleware().refresh_api_data()


    # schedule.every(1).minutes.do(refresh_data)
    def run_scheduler(self):
        print("Scheduler Initiated !")
        schedule.every(5).minutes.do(self.aggregate_data)
        while True:
            try:
                schedule.run_pending()
                time.sleep(10)
            except Exception as e:
                print(e)

if __name__ == '__main__':
    sch = Scheduler()
    sch.run_scheduler()
    