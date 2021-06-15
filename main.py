from scheduler import Scheduler
from db_listeners import DB_Listener                                                                   
from multiprocessing import Process                             
import bot         
import concurrent.futures                                                                       


# processes = ('bot.py', 'db_listeners.py', 'scheduler.py')                                    
                                                  
def MultiProcessBot():
    scheduler = Scheduler()
    db_listner = DB_Listener()
    bot_process = Process(target= bot.bot_main)
    db_listner_process = Process(target=db_listner.db_change_listener)
    scheduler_process = Process(target=scheduler.run_scheduler)

    print("Starting Bot Process")
    bot_process.start()
    print("Starting Scheduler Process")
    scheduler_process.start()
    print("Starting Listener Process")
    db_listner_process.start()


def MultiThreadedBot():
    scheduler = Scheduler()
    db_listner = DB_Listener()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(bot.bot_main)
        executor.submit(scheduler.run_scheduler)
        executor.submit(db_listner.db_change_listener)

if __name__ == '__main__':
    # MultiProcessBot()
    MultiThreadedBot()