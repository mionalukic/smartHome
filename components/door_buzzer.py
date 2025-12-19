from simulators.door_buzzer import run_db_simulator
import threading
import time

def run_db(settings, threads, stop_event, print_fn=print):
    if settings['simulated']:
        db_thread = threading.Thread(target=run_db_simulator, args=(1, stop_event, print_fn))
        db_thread.start()
        threads.append(db_thread)
    else:
        from sensors.door_buzzer import run_db_loop, DB
        print("Starting db loop")
        db = DB(settings['pin'])
        db_thread = threading.Thread(target=run_db_loop, args=(db, 440, 0.1, stop_event, print_fn))
        db_thread.start()
        threads.append(db_thread)
        print("db loop started")