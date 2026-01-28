import threading
from simulators.door_ulatresonic_sensor1 import run_dus1_simulator


def run_dus1(settings, threads, stop_event, print_fn=print, mqtt_publisher=None):

    if settings["simulated"]:
        t = threading.Thread(
            target=run_dus1_simulator,
            args=(stop_event, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'))
        )
    else:
        from sensors.door_ultrasonic_sensor1 import run_dus1_ultrasonic
        t = threading.Thread(
            target=run_dus1_ultrasonic,
            args=(
                settings["trig"],
                settings["echo"],
                stop_event,
                print_fn,
                mqtt_publisher,
                settings.get('device_id', 'pi1')
            )
        )

    t.start()
    threads.append(t)