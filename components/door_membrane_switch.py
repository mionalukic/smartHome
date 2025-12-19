from simulators.door_motion_sensor import run_dms_simulator
import threading
import time

def run_dms(settings, threads, stop_event, print_fn=print):
    if settings['simulated']:
        dms_thread = threading.Thread(target=run_dms_simulator, args=(2, stop_event, print_fn))
        dms_thread.start()
        threads.append(dms_thread)
    else:
        from sensors.door_buzzer import run_dms_loop, dms
        print("Starting dms loop")
        dms = dms(settings['pin'])
        dms_thread = threading.Thread(target=run_dms_loop, args=(dms, stop_event, print_fn))
        dms_thread.start()
        threads.append(dms_thread)
        print("dms loop started")