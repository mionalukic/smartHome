from simulators.door_light import run_dl_simulator
import threading
import time

DL_STATE = None
DL_SHOULD_CHANGE = None
def get_dl_state():
    return DL_STATE, DL_SHOULD_CHANGE

def turn_on():
    global DL_STATE, DL_SHOULD_CHANGE
    DL_STATE = True
    DL_SHOULD_CHANGE = True

def do_change():
    global DL_SHOULD_CHANGE
    DL_SHOULD_CHANGE = False

def turn_off():
    global DL_STATE
    DL_STATE = False

def run_dl(settings, threads, stop_event, print_fn=print, mqtt_publisher=None):

    if settings.get('simulated', True):
        dl_thread = threading.Thread(
            target=run_dl_simulator,
            args=(stop_event, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'), get_dl_state, turn_off, do_change)
        )
        dl_thread.start()
        threads.append(dl_thread)
    else:
        from sensors.door_light import DL
        from sensors.door_light import run_dl_loop
        
        dl = DL(settings['pin'])
        dl_thread = threading.Thread(
            target=run_dl_loop,
            args=(dl, stop_event, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'), get_dl_state, turn_off, do_change)
        )
        dl_thread.start()
        threads.append(dl_thread)
