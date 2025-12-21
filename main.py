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

def effective_cfg(name, cfg):
    sim = cfg.get("simulated", True)
    if not GPIO_AVAILABLE and not sim:
        safe_print(f"GPIO not available; forcing simulation for {name}", component="SYSTEM")
        cfg = dict(cfg)
        cfg["simulated"] = True
    return cfg

def format_help():
    return (
        "Commands:\n"
        "  help                       - show help\n"
        "  status                     - list running actuators\n"
        "  all                        - turn all actuators on\n"
        "  buzz on                    - turn buzzer on\n"
        "  buzz off                   - turn buzzer off\n"
        "  quit | exit | q            - stop and exit\n"
    )

def command_loop(stop_event, actuator_registry, pi1_settings, threads):
    safe_print("Console ready. Type 'help' for commands.", component="SYSTEM")

    db_settings = pi1_settings.get("DB", {})

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
            safe_print(format_help(), component="SYSTEM")

        elif op == "status":
            names = sorted(actuator_registry)
            label = ", ".join(names) if names else "(none)"
            safe_print(f"Components: {label}", component="SYSTEM")

        elif op == "all":
            if "DB" not in actuator_registry:
                run_db(
                    True, db_settings, threads, stop_event,
                    print_fn=lambda m: safe_print(m, component="DB")
                )
                actuator_registry.add("DB")

        elif op == "buzz":
            sub = parts[1].lower() if len(parts) > 1 else ""

            if sub == "on":
                if "DB" in actuator_registry:
                    safe_print("DB is already turned on", component="SYSTEM")
                else:
                    # freq = float(parts[2]) if len(parts) > 2 else 440.0
                    # dur = float(parts[3]) if len(parts) > 3 else 0.0
                    run_db(
                        True, db_settings, threads, stop_event,
                        print_fn=lambda m: safe_print(m, component="DB")
                    )
                    actuator_registry.add("DB")

            elif sub == "off":
                if "DB" in actuator_registry:
                    run_db(
                        False, db_settings, threads, stop_event,
                        print_fn=lambda m: safe_print(m, component="DB")
                    )
                    actuator_registry.discard("DB")
                else:
                    safe_print("DB is already turned off", component="SYSTEM")

            else:
                safe_print("Usage: buzz on | buzz off", component="SYSTEM")

        else:
            safe_print(f"Unknown command: {cmd}", component="SYSTEM")

def main(args):
    safe_print("Starting app", component="SYSTEM")

    settings = load_settings()
    pi1_settings = settings.get("PI1", {})
    threads = []
    stop_event = threading.Event()

    actuator_registry = set()

    try:
        if "--sensors" in args:
            for name, cfg in pi1_settings.items():
                cfg = effective_cfg(name, cfg)

                if name == "DPIR1":
                    safe_print(f"{name} {cfg}", component=name)
                    run_dpir(cfg, threads, stop_event,
                             print_fn=lambda m: safe_print(m, component="DPIR1"))

                elif name == "DMS":
                    safe_print(f"{name} {cfg}", component=name)
                    run_dms(cfg, threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="DMS"))

        command_loop(stop_event, actuator_registry, pi1_settings, threads)

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
    args = sys.argv[1:]
    main(args)