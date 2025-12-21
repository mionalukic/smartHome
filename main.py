import threading
import time
from settings import load_settings
from components.ds1 import run_ds1
from components.dus1 import run_dus1
from components.dl import run_dl


try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except:
    pass

#da li simulatori moraju da rade logicki zajedno ili je dovoljno logicki za sebe
if __name__ == "__main__":
    print("Starting PI1 app")

    settings = load_settings()
    threads = []
    stop_event = threading.Event()

    try:
        run_ds1(settings["DS1"], threads, stop_event)
        run_dus1(settings["DUS1"], threads, stop_event)
        run_dl(settings["DL"], threads, stop_event)
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping app")
        stop_event.set()
