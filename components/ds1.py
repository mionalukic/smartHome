import threading

from simulators.ds1_simulator import run_ds1_simulator
from sensors.ds1_button import run_ds1_button


def run_ds1(settings, threads, stop_event):
    if settings["simulated"]:
        target = lambda: run_ds1_simulator(stop_event)
    else:
        target = lambda: run_ds1_button(settings["pin"], stop_event)

    t = threading.Thread(target=target)
    t.start()
    threads.append(t)
