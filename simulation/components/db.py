from simulators.db import run_db_simulator
import threading
import time

def db_callback():
    return

def run_db(settings, threads, stop_event):
    if settings['simulated']:
        db_thread = threading.Thread(target=run_db_simulator, args=())
        db_thread.start()
        threads.append(db_thread)
    else:
        return