import logging
import threading
import time
import sys

from settings import load_settings
from components.door_buzzer import run_db
from components.door_motion_sensor import run_dpir
from components.door_membrane_switch import run_dms
from components.door_sensor1 import run_ds1
from components.door_light import run_dl
from mqtt.publisher import MQTTPublisher
from mqtt.config import MQTTConfig
from components.door_sensor2 import run_ds2
from components.door_ultrasonic_sensor import run_dus
from components.kitchen_button import run_kitchen_button
from components.kitchen_4sd import run_kitchen_4sd
from components.kitchen_dht import run_kitchen_dht
from components.kitchen_gsg import run_kitchen_gsg



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
    "DS2":    "\033[38;5;214m",
    "DPIR2":  "\033[38;5;39m",
    "DUS2":   "\033[38;5;141m",
    "BTN":    "\033[38;5;82m", 
    "4SD":    "\033[38;5;203m",
    "DHT3":   "\033[38;5;44m",  # tirkiz
    "GSG":    "\033[38;5;199m",  # ljubičasta / alarm


}
RESET = "\033[0m"

def parse_arg(args, key, default=None):
    if key in args:
        i = args.index(key)
        if i + 1 < len(args):
            return args[i + 1]
    return default

def get_pi_context(settings, args):
    pi_name = parse_arg(args, "--pi", settings.get("device", {}).get("pi_name", "PI1"))
    device = dict(settings.get("device", {}))
    device["pi_name"] = pi_name
    # opcionalno: device_id možeš da razlikuješ po PI
    # device["device_id"] = device.get("device_id", "pi_unknown").replace("pi1", pi_name.lower())
    pi_settings = settings.get(pi_name, {})
    return pi_name, device, pi_settings


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
    safe_print(db_settings, component="SYSTEM")

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
                run_db(db_settings, threads, stop_event,
                        print_fn=lambda m: safe_print(m, component="DB"),
                        mqtt_publisher=mqtt_publisher, state='on'
                    )
                actuator_registry.add("DB")

        elif op == "buzz":
            sub = parts[1].lower() if len(parts) > 1 else ""
            safe_print(f"Buzz command: {sub}", component="SYSTEM")
            if sub == "on":
                if "DB" in actuator_registry:
                    safe_print("DB is already turned on", component="SYSTEM")
                else:
                    safe_print("ovde sam")
                    run_db(db_settings, threads, stop_event,
                        print_fn=lambda m: safe_print(m, component="DB"),
                        mqtt_publisher=mqtt_publisher, state=True
                    )
                    actuator_registry.add("DB")

            elif sub == "off":
                if "DB" in actuator_registry:
                    safe_print("DB turned off", component="DB")
                    actuator_registry.discard("DB")
                else:
                    safe_print("DB is already turned off", component="SYSTEM")

            else:
                safe_print("Usage: buzz on | buzz off", component="SYSTEM")


        elif op == "led":
            sub = parts[1].lower() if len(parts) > 1 else ""
            dl_settings = pi1_settings.get("DL", {})

            if sub == "on":
                run_dl(dl_settings, threads, stop_event,
                    print_fn=lambda m: safe_print(m, component="DL"),
                    mqtt_publisher=mqtt_publisher,
                    state=True
                )

            elif sub == "off":
                run_dl(dl_settings, threads, stop_event,
                    print_fn=lambda m: safe_print(m, component="DL"),
                    mqtt_publisher=mqtt_publisher,
                    state=False
                )

            else:
                safe_print("Usage: led on | led off", component="SYSTEM")

        else:
            safe_print(f"Unknown command: {cmd}", component="SYSTEM")

def setup_mqtt(settings):
    mqtt_config = MQTTConfig()
    
    safe_print("Setting up MQTT...", component="MQTT")
    
    mqtt_publisher = MQTTPublisher(
        broker=mqtt_config.broker,
        port=mqtt_config.port,
        keepalive=mqtt_config.keepalive,
        batch_size=mqtt_config.batch_size,
        batch_interval=mqtt_config.batch_interval
    )
    
    for topic in mqtt_config.topics.values():
        mqtt_publisher.register_topic(topic)
    
    if mqtt_publisher.connect():
        time.sleep(1)  
        if mqtt_publisher.connected:
            safe_print("MQTT connected", component="MQTT")
            mqtt_publisher.start_batch_publisher()
            return mqtt_publisher
        else:
            safe_print("MQTT connection failed", component="MQTT")
    else:
        safe_print("Could not connect to MQTT broker", component="MQTT")
    
    return None

def main(args):
    

    settings = load_settings()
    pi_name, device, pi_settings = get_pi_context(settings, args)
    threads = []
    stop_event = threading.Event()
    mqtt_publisher = None
    
    safe_print("=" * 60, component="SYSTEM")
    safe_print(f"Starting Smart Home System - {pi_name}", component="SYSTEM")
    safe_print("=" * 60, component="SYSTEM")
    
    actuator_registry = set()

    try:
        mqtt_publisher = setup_mqtt(settings)
        
        if "--sensors" in args:
            for name, cfg in pi_settings.items():
                cfg = effective_cfg(name, cfg)
                

                if name.startswith("DPIR"):
                    safe_print(f"{name} {cfg}", component=name if name in COMPONENT_COLORS else "SYSTEM")
                    run_dpir(cfg, threads, stop_event,
                            print_fn=lambda m, n=name: safe_print(m, component=n),
                            mqtt_publisher=mqtt_publisher)
                    
                elif name == "DMS":
                    safe_print(f"{name} {cfg}", component="DMS")
                    run_dms(cfg, threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="DMS"),
                            mqtt_publisher=mqtt_publisher)

                elif name.startswith("DUS"):
                    safe_print(f"{name} {cfg}", component=name if name in COMPONENT_COLORS else "SYSTEM")
                    run_dus(cfg, threads, stop_event,
                            print_fn=lambda m, n=name: safe_print(m, component=n),
                            mqtt_publisher=mqtt_publisher)


                elif name == "DS1":
                    safe_print(f"{name} {cfg}", component="DS1")
                    run_ds1(cfg, threads, stop_event,  
                            print_fn=lambda m, n=name: safe_print(m, component="DS1"),
                            mqtt_publisher=mqtt_publisher)
                    
                elif name == "DS2":
                    safe_print(f"{name} {cfg}", component="DS2")
                    run_ds2(cfg, threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="DS2"),
                            mqtt_publisher=mqtt_publisher)
                    
                elif name == "BTN":
                    safe_print(f"{name} {cfg}", component="BTN")
                    run_kitchen_button(cfg, threads, stop_event,
                                    print_fn=lambda m: safe_print(m, component="BTN"),
                                    mqtt_publisher=mqtt_publisher)
                elif name == "4SD":
                    safe_print(f"{name} {cfg}", component="4SD")
                    run_kitchen_4sd(cfg, threads, stop_event,
                                    print_fn=lambda m: safe_print(m, component="4SD"))
                    
                elif name == "DHT3":
                    safe_print(f"{name} {cfg}", component="DHT3")
                    run_kitchen_dht(cfg, threads, stop_event,
                                    print_fn=lambda m: safe_print(m, component="DHT3"),
                                    mqtt_publisher=mqtt_publisher)
                    
                elif name == "GSG":
                    safe_print(f"{name} {cfg}", component="GSG")
                    run_kitchen_gsg(cfg, threads, stop_event,
                                    print_fn=lambda m: safe_print(m, component="GSG"),
                                    mqtt_publisher=mqtt_publisher)




        safe_print("=" * 60, component="SYSTEM")
        safe_print("System running. Press Ctrl+C to stop.", component="SYSTEM")
        safe_print("=" * 60, component="SYSTEM")

        command_loop(stop_event, actuator_registry, pi_settings, threads, mqtt_publisher)

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