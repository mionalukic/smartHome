from simulators.door_membrane_switch import run_dms_simulator
import threading
import time

def run_dms(settings, threads, stop_event, print_fn=print):
    if settings['simulated']:
        dms_thread = threading.Thread(target=run_dms_simulator, args=(stop_event, print_fn))
        dms_thread.start()
        threads.append(dms_thread)
    else:
        from sensors.door_membrane_switch import run_dms_loop, DMS
        print("Starting dms loop")
        dms = DMS(settings['pin'])
        dms_thread = threading.Thread(target=run_dms_loop, args=(dms, stop_event, print_fn))
        dms_thread.start()
        threads.append(dms_thread)
        print("dms loop started")