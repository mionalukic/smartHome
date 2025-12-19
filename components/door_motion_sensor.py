from simulators.door_motion_sensor import run_dpir_simulator
import threading
import time

def run_dpir(settings, threads, stop_event):
    if settings['simulated']:
        dpir_thread = threading.Thread(target=run_dpir_simulator, args=(2, stop_event))
        dpir_thread.start()
        threads.append(dpir_thread)
    else:
        from sensors.door_buzzer import run_dpir_loop, dpir
        print("Starting dpir loop")
        dpir = dpir(settings['pin'])
        dpir_thread = threading.Thread(target=run_dpir_loop, args=(dpir, stop_event))
        dpir_thread.start()
        threads.append(dpir_thread)
        print("dpir loop started")