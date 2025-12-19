import threading
import time
import sys

from settings import load_settings
from components.door_buzzer import run_db
from components.door_motion_sensor import run_dpir
from components.door_membrane_switch import run_dms

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO_AVAILABLE = True
except Exception:
    GPIO_AVAILABLE = False

_console_lock = threading.Lock()

COMPONENT_COLORS = {
    "SYSTEM": "\033[38;5;15m",   # white
    "DB":     "\033[38;5;208m",  # orange
    "DPIR1":  "\033[38;5;39m",   # blue
    "DMS":    "\033[38;5;118m",  # green
}
RESET = "\033[0m"

def safe_print(message, *, component="SYSTEM", end="\n"):
    color = COMPONENT_COLORS.get(component, "")
    with _console_lock:
        print(f"{color}[{component}] {message}{RESET}", end=end, flush=True)

def command_loop(stop_event, control_registry):
    safe_print("Console ready. Type 'help' for commands.", component="SYSTEM")
    while not stop_event.is_set():
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            safe_print("Exiting by user request.", component="SYSTEM")
            stop_event.set()
            break

        if not cmd:
            continue

        parts = cmd.split()
        op = parts[0].lower()

        if op in ("quit", "exit", "q"):
            stop_event.set()
            safe_print("Stopping application...", component="SYSTEM")
            break

        elif op == "help":
            safe_print(
                "Commands:\n"
                "  help                      - show this help\n"
                "  status                    - list running components\n"
                "  all                       - turn everything on\n"
                "  buzz on                   - turn buzzer ON \n"
                "  buzz off                  - turn buzzer OFF\n"
                "  door motion sensor on     - turn dpir1 on\n"
                "  door motion sensor off    - turn dpir1 off\n"
                "  door membrane switch on   - turn dms on\n"
                "  door membrane switch off  - turn dms off\n"
                "  quit                 - stop and exit\n",
                component="SYSTEM"
            )

        elif op == "status":
            names = ", ".join(sorted(control_registry.keys()))
            safe_print(f"Components: {names}", component="SYSTEM")

        elif op == "buzz":
            if "DB" not in control_registry:
                safe_print("Door buzzer (DB) not available.", component="SYSTEM")
                continue

            sub = parts[1].lower() if len(parts) > 1 else ""
            if sub == "on":
                freq = float(parts[2]) if len(parts) > 2 else 440.0
                dur = float(parts[3]) if len(parts) > 3 else 0.0  # 0.0 means continuous
                fn = control_registry["DB"].get("on")
                if fn:
                    fn(freq=freq, duration=dur)
                else:
                    safe_print("DB 'on' control not wired.", component="SYSTEM")

            elif sub == "off":
                fn = control_registry["DB"].get("off")
                if fn:
                    fn()
                else:
                    safe_print("DB 'off' control not wired.", component="SYSTEM")

            elif sub == "beep":
                freq = float(parts[2]) if len(parts) > 2 else 440.0
                dur = float(parts[3]) if len(parts) > 3 else 0.2
                fn = control_registry["DB"].get("beep")
                if fn:
                    fn(freq=freq, duration=dur)
                else:
                    safe_print("DB 'beep' control not wired.", component="SYSTEM")
            else:
                safe_print("Usage: buzz on [freq dur] | buzz off | buzz beep [freq dur]", component="SYSTEM")

        else:
            safe_print(f"Unknown command: {cmd}", component="SYSTEM")

def main():
    safe_print("Starting app", component="SYSTEM")

    settings = load_settings() 
    threads = []
    stop_event = threading.Event()

    control_registry = {}

    def effective_cfg(name, cfg):
        sim = cfg.get("simulated", True)
        if not GPIO_AVAILABLE and not sim:
            safe_print(f"GPIO not available; forcing simulation for {name}", component="SYSTEM")
            cfg = dict(cfg)
            cfg["simulated"] = True
        return cfg

    try:
        for name, cfg in settings.items():
            cfg = effective_cfg(name, cfg)
            if name == "DB":
                safe_print(f"{name} {cfg}", component="DB")
                controls = run_db(cfg, threads, stop_event, print_fn=lambda m: safe_print(m, component="DB"))
                control_registry["DB"] = controls

            elif name == "DPIR1":
                safe_print(f"{name} {cfg}", component="DPIR1")
                run_dpir(cfg, threads, stop_event, print_fn=lambda m: safe_print(m, component="DPIR1"))

            elif name == "DMS":
                safe_print(f"{name} {cfg}", component="DMS")
                run_dms(cfg, threads, stop_event, print_fn=lambda m: safe_print(m, component="DMS"))

        command_loop(stop_event, control_registry)

    except KeyboardInterrupt:
        safe_print("Stopping app (KeyboardInterrupt)", component="SYSTEM")
        stop_event.set()
    finally:
        for t in threads:
            try:
                t.join(timeout=2.0)
            except Exception:
                pass

        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
            except Exception:
                pass

        safe_print("App stopped cleanly", component="SYSTEM")

if __name__ == "__main__":
    main()