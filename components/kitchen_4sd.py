import threading
from simulators.kitchen_4sd import run_4sd_simulator


def run_kitchen_4sd(settings, threads, stop_event, print_fn=print):

    if settings.get("simulated", True):
        t = threading.Thread(
            target=run_4sd_simulator,
            args=(stop_event, print_fn)
        )
    else:
        from sensors.kitchen_4sd import Kitchen4SD
        display = Kitchen4SD(
            settings["segments"],
            settings["digits"],
            settings.get("refresh_ms", 1)
        )
        t = threading.Thread(
            target=display.run,
            args=(stop_event,)
        )

    t.start()
    threads.append(t)
