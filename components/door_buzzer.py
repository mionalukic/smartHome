import time
from simulators.door_buzzer import run_db_simulator
import threading

def run_db(settings, threads, stop_event, print_fn=print, mqtt_publisher=None, state=None):
    print_fn(state)
    print_fn(f"DB state: {state}")
    print(settings.get('simulated', True))
    if settings.get('simulated', True):
        if state is not None:
            state_str = "on" if state else "off"
            print_fn(f"Buzzer turned {state_str} (simulated)")

            if mqtt_publisher and mqtt_publisher.connected:
                data = {
                    "device_id": settings.get('device_id', 'pi1'),
                    "sensor_type": "door_buzzer",
                    "component": "DB",
                    "value": 1 if state else 0,  
                    "simulated": True,
                    "timestamp": time.time()
                }

                topic = f"smarthome/{settings.get('device_id', 'pi1')}/actuators/db"
                mqtt_publisher.publish(topic, data, use_batch=True)
        else:
            db_thread = threading.Thread(
                target=run_db_simulator,
                args=(stop_event, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'))
            )
            db_thread.start()
            threads.append(db_thread)
    else:
        print_fn(state)
        print_fn(f"DB state: {state}")
        if state:
            from sensors.door_buzzer import run_db_loop, DB
            print_fn("Starting DB buzzing")
            db = DB(settings['pin'])
            db_thread = threading.Thread(
                target=run_db_loop,
                args=(db, stop_event, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'))
            )
            db_thread.start()
            threads.append(db_thread)
            print_fn("DB buzzing started")
        else:
            print_fn("DB turned off")