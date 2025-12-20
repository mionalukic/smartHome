# from simulators.door_buzzer import run_db_simulator
import threading
import time
import random

def run_db(state, settings, threads, stop_event, print_fn=print):
    if settings['simulated']:
        # db_thread = threading.Thread(target=run_db_simulator, args=(status, print_fn))
        # db_thread.start()
        # threads.append(db_thread)
        # run_db_simulator(state, print_fn)
        print_fn(f"{time.ctime()} DOOR BUZZER {"ON" if state else "OFF"}")
    else:
        from sensors.door_buzzer import run_db_loop, DB
        print("Starting db loop")
        db = DB(settings['pin'])
        db_thread = threading.Thread(target=run_db_loop, args=(db, 440, 0.1, stop_event, print_fn))
        db_thread.start()
        threads.append(db_thread)
        print("db loop started")