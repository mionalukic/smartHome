from simulators.door_motion_sensor import run_dpir_simulator
import threading
import time

def run_dpir(settings, threads, stop_event, print_fn=print, mqtt_publisher=None):

    if settings['simulated']:
        dpir_thread = threading.Thread(
            target=run_dpir_simulator, 
            args=(stop_event, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'))
        )
        dpir_thread.start()
        threads.append(dpir_thread)
    else:
        from sensors.door_motion_sensor import run_dpir_loop, DPIR
        print_fn("Starting DPIR loop")
        dpir = DPIR(settings['pin'])
        dpir_thread = threading.Thread(
            target=run_dpir_loop, 
            args=(dpir, stop_event, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'))
        )
        dpir_thread.start()
        threads.append(dpir_thread)
        print_fn("DPIR loop started")