from simulators.door_membrane_switch import run_dms_simulator
import threading
import time

def run_dms(settings, threads, stop_event, print_fn=print, mqtt_publisher=None):
   
    if settings['simulated']:
        dms_thread = threading.Thread(
            target=run_dms_simulator, 
            args=(stop_event, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'))
        )
        dms_thread.start()
        threads.append(dms_thread)
    else:
        from sensors.door_membrane_switch import run_dms_loop, DMS
        print_fn("Starting DMS loop")
        dms = DMS(settings['button_pin'], settings['row_pin'])
        dms_thread = threading.Thread(
            target=run_dms_loop, 
            args=(dms, stop_event, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'))
        )
        dms_thread.start()
        threads.append(dms_thread)
        print_fn("DMS loop started")