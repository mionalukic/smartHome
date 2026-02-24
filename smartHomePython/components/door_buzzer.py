from simulators.door_buzzer import run_db_simulator
import threading

DB_STATE = None
def get_DB_state():
    return DB_STATE

def buzz_on():
    global DB_STATE
    DB_STATE = True

def buzz_off():
    global DB_STATE
    DB_STATE = False

def run_db(settings, threads, stop_event, print_fn=print, mqtt_publisher=None):
    if settings.get('simulated', True):
        db_thread = threading.Thread(
            target=run_db_simulator,
            args=(stop_event, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'), get_DB_state)
        )
        db_thread.start()
        threads.append(db_thread)
    else:
        from sensors.door_buzzer import run_db_loop, DB
        print_fn("Starting DB buzzing")
        db = DB(settings['pin'])
        db_thread = threading.Thread(
            target=run_db_loop,
            args=(db, stop_event, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'), get_DB_state)
        )
        db_thread.start()
        threads.append(db_thread)