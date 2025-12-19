
import threading
from settings import load_settings
from components.door_buzzer import run_db
import time

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO_AVAILABLE = True
except:
    GPIO_AVAILABLE = False


def main():
    print('Starting app')
    settings = load_settings()
    threads = []
    stop_event = threading.Event()
    try:
        for name, cfg in settings.items():
            if name == 'DB':
                print(name, cfg)
                run_db(cfg, threads, stop_event)
        while not stop_event.wait(1.0):
            pass

    except KeyboardInterrupt:
        print('Stopping app (KeyboardInterrupt)')
        stop_event.set()
        for t in threads:
            t.join(timeout=2.0)
    finally:
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
            except Exception:
                pass
        print("App stopped cleanly")

if __name__ == "__main__":
    main()