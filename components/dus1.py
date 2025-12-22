import threading
from simulators.dus1_simulator import run_dus1_simulator
from sensors.dus1_ultrasonic import run_dus1_ultrasonic


def run_dus1(settings, threads, stop_event):
    if settings["simulated"]:
        target = lambda: run_dus1_simulator(stop_event)
    else:
        target = lambda: run_dus1_ultrasonic(
            settings["trig"],
            settings["echo"],
            stop_event
        )

    t = threading.Thread(target=target)
    t.start()
    threads.append(t)
