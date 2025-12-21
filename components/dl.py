import threading

from simulators.dl_simulator import run_dl_simulator
from sensors.dl_led import run_dl_led


def run_dl(settings, threads, stop_event):
    if settings["simulated"]:
        target = lambda: run_dl_simulator(stop_event)
    else:
        target = lambda: run_dl_led(settings["pin"], settings["interval"],stop_event)

    t = threading.Thread(target=target)
    t.start()
    threads.append(t)
