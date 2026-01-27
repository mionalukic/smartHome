


import logging
import threading
import time
import sys

from settings import load_settings
from components.door_buzzer import run_db
from components.door_motion_sensor import run_dpir
from components.door_membrane_switch import run_dms
from components.door_sensor1 import run_ds1
from components.door_ultrasonic_sensor1 import run_dus1
from components.door_light import run_dl
from mqtt.publisher import MQTTPublisher
from mqtt.config import MQTTConfig


try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO_AVAILABLE = True
except Exception:
    GPIO_AVAILABLE = False

_console_lock = threading.Lock()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

COMPONENT_COLORS = {
    "SYSTEM": "\033[38;5;15m",   # white
    "MQTT":   "\033[38;5;45m",   # cyan
    "DB":     "\033[38;5;208m",  # orange
    "DPIR1":  "\033[38;5;39m",   # blue
    "DMS":    "\033[38;5;118m",  # green
    "DUS1":   "\033[38;5;141m",  # purple,
    "DS1":    "\033[38;5;214m",  # yellow/orange
    "DL":     "\033[38;5;220m",  # yellow
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
        "  mqtt status                - show MQTT connection status\n"
        "  all                        - turn all actuators on\n"
        "  buzz on                    - turn buzzer on\n"
        "  buzz off                   - turn buzzer off\n"
        "  led on                     - turn led on\n"
        "  led off                    - turn led off\n"
        "  quit | exit | q            - stop and exit\n"
    )

def command_loop(stop_event, actuator_registry, pi1_settings, threads, mqtt_publisher=None):
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

        elif op == "mqtt":
            sub = parts[1].lower() if len(parts) > 1 else ""
            if sub == "status":
                if mqtt_publisher:
                    status = "Connected" if mqtt_publisher.connected else "Disconnected"
                    safe_print(f"MQTT Status: {status}", component="MQTT")
                    if mqtt_publisher.connected:
                        safe_print(f"Broker: {mqtt_publisher.broker}:{mqtt_publisher.port}", component="MQTT")
                        safe_print(f"Batch size: {mqtt_publisher.batch_size}", component="MQTT")
                        safe_print(f"Batch interval: {mqtt_publisher.batch_interval}s", component="MQTT")
                else:
                    safe_print("MQTT not configured", component="SYSTEM")
            else:
                safe_print("Usage: mqtt status", component="SYSTEM")

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


        elif op == "led":
            sub = parts[1].lower() if len(parts) > 1 else ""
            dl_settings = pi1_settings.get("DL", {})

            if sub == "on":
                run_dl(True, dl_settings, threads, stop_event,
                    print_fn=lambda m: safe_print(m, component="DL")
                )

            elif sub == "off":
                run_dl(False, dl_settings, threads, stop_event,
                    print_fn=lambda m: safe_print(m, component="DL")
                )

            else:
                safe_print("Usage: led on | led off", component="SYSTEM")

        else:
            safe_print(f"Unknown command: {cmd}", component="SYSTEM")

def setup_mqtt(settings):
    """Setup MQTT publisher if enabled"""
    mqtt_config = MQTTConfig()
    
    safe_print("Setting up MQTT...", component="MQTT")
    
    mqtt_publisher = MQTTPublisher(
        broker=mqtt_config.broker,
        port=mqtt_config.port,
        keepalive=mqtt_config.keepalive,
        batch_size=mqtt_config.batch_size,
        batch_interval=mqtt_config.batch_interval
    )
    
    # Register topics
    for topic in mqtt_config.topics.values():
        mqtt_publisher.register_topic(topic)
    
    # Try to connect
    if mqtt_publisher.connect():
        time.sleep(1)  # Wait for connection to establish
        if mqtt_publisher.connected:
            safe_print("✓ MQTT connected", component="MQTT")
            mqtt_publisher.start_batch_publisher()
            return mqtt_publisher
        else:
            safe_print("⚠ MQTT connection failed", component="MQTT")
    else:
        safe_print("⚠ Could not connect to MQTT broker", component="MQTT")
    
    return None

def main(args):
    safe_print("=" * 60, component="SYSTEM")
    safe_print("Starting Smart Home System - PI1", component="SYSTEM")
    safe_print("=" * 60, component="SYSTEM")

    settings = load_settings()
    pi1_settings = settings.get("PI1", {})
    threads = []
    stop_event = threading.Event()
    mqtt_publisher = None

    actuator_registry = set()

    try:
        # Setup MQTT
        mqtt_publisher = setup_mqtt(settings)
        
        # Start sensors if requested
        if "--sensors" in args:
            for name, cfg in pi1_settings.items():
                cfg = effective_cfg(name, cfg)

                if name == "DPIR1":
                    safe_print(f"{name} {cfg}", component=name)
                    run_dpir(cfg, threads, stop_event,
                             print_fn=lambda m: safe_print(m, component="DPIR1"),
                             mqtt_publisher=mqtt_publisher)

                elif name == "DMS":
                    safe_print(f"{name} {cfg}", component=name)
                    run_dms(cfg, threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="DMS"),
                            mqtt_publisher=mqtt_publisher)
                
                elif name == "DUS1":
                    safe_print(f"{name} {cfg}", component=name)
                    # run_dus1(cfg, threads, stop_event,
                    #     print_fn=lambda m: safe_print(m, component="DUS1"),
                    #     mqtt_publisher=mqtt_publisher
                    # )
                
                elif name == "DS1":
                    safe_print(f"{name} {cfg}", component=name)
                    run_ds1(cfg, threads, stop_event,
                        print_fn=lambda m: safe_print(m, component="DS1"),
                        mqtt_publisher=mqtt_publisher
                    )

        safe_print("=" * 60, component="SYSTEM")
        safe_print("✓ System running. Press Ctrl+C to stop.", component="SYSTEM")
        safe_print("=" * 60, component="SYSTEM")

        command_loop(stop_event, actuator_registry, pi1_settings, threads, mqtt_publisher)

    except KeyboardInterrupt:
        safe_print("Stopping app (KeyboardInterrupt)", component="SYSTEM")
        stop_event.set()
    finally:
        # Stop MQTT
        if mqtt_publisher:
            safe_print("Disconnecting MQTT...", component="MQTT")
            mqtt_publisher.disconnect()
        
        # Join threads
        for t in threads:
            try:
                t.join(timeout=2.0)
            except Exception:
                pass

        # Cleanup GPIO
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
            except Exception:
                pass

        safe_print("App stopped cleanly", component="SYSTEM")

if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)