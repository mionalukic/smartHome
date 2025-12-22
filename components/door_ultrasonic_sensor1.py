import threading
from simulators.door_ulatresonic_sensor1 import run_dus1_simulator


def run_dus1(settings, threads, stop_event, print_fn=print):
    if settings["simulated"]:
        t = threading.Thread(
            target=run_dus1_simulator,
            args=(stop_event, print_fn)
        )
    else:
        from sensors.door_ultrasonic_sensor1 import run_dus1_ultrasonic
        t = threading.Thread(
            target=run_dus1_ultrasonic,
            args=(
                settings["trig"],
                settings["echo"],
                stop_event,
                print_fn
            )
        )

    t.start()
    threads.append(t)
