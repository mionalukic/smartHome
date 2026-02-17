from functools import partial
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
from components.dht import run_dht
from components.kitchen_gsg import run_kitchen_gsg
from mqtt.actuator_listener import start_actuator_listener
from components.lcd_display import on_dht_message, run_lcd
import paho.mqtt.client as mqtt
from mqtt.subscriber import on_disconnect
from components.rgb_led import on_command_message, run_rgb
from components.ir import run_ir

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
    "DPIR3":  "\033[38;5;160m",   # red
    "DHT1":   "\033[38;5;129m",   # orchid / magenta
    "DHT2":   "\033[38;5;190m",   # chartreuse (žuto-zelena)
    "LCD":    "\033[38;5;51m",   # bright cyan
    "RGB_LED":"\033[38;5;180m", 
    "IR":     "\033[38;5;70m",
}
RESET = "\033[0m"

def get_pi_context(args):
    if "--pi" in args:
        i = args.index("--pi")
        if i + 1 < len(args):
            return args[i + 1]
    return "PI1"

def safe_print(message, *, component="SYSTEM", end="\n"):
    color = COMPONENT_COLORS.get(component, "")
    with _console_lock:
        print(f"{color}[{component}] {message}{RESET}", end=end, flush=True)

def simulate_door(mqtt_publisher, device_id, state):
    payload = {
        "device_id": device_id,
        "sensor_type": "door_sensor",
        "component": "DS1",
        "state": state,
        "simulated": True,
        "timestamp": time.time()
    }
    topic = f"smarthome/{device_id}/sensors/door"
    mqtt_publisher.publish(topic, payload)
    safe_print(f"Door simulated: {state}", component="DS1")

def simulate_rgb_color_change(mqtt_publisher, color, device_id="pi3_bedroom_001"):
    payload = {
        "device_id": device_id,
        "actuator_type": "rgb_led",
        "component": "RGB_LED",
        "command": color,
        "simulated": True,
        "timestamp": time.time()
    }
    topic = f"smarthome/{device_id}/actuators/rgb_led"
    mqtt_publisher.publish(topic, payload)
    safe_print(f"RGB LED command simulated: {color}", component="RGB_LED")


def simulate_pin(mqtt_publisher, device_id, pin):

    topic = f"smarthome/{device_id}/sensors/dms"

    for digit in pin:
        payload = {
            "device_id": device_id,
            "sensor_type": "door_membrane_switch",
            "component": "DMS",
            "key": digit,
            "simulated": True,
            "timestamp": time.time()
        }

        mqtt_publisher.publish(topic, payload)
        safe_print(f"PIN digit sent: {digit}", component="DMS")
        time.sleep(0.4)


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
        "  door open                  - simulate door open\n"
        "  door close                 - simulate door close\n"
        "  pin <code>                 - send PIN sequence\n"
        "  lcd on                     - turn LCD on\n"
        "  lcd off                    - turn LCD off\n"
        "  rgb on <color>             - turn RGB LED on with specified color\n"
        "  rgb <color>                - change RGB LED color\n"
        "  rgb off                    - turn RGB LED off\n"
        "  quit | exit | q            - stop and exit\n"
    )

def command_loop(stop_event, actuator_registry, pi_settings, threads, mqtt_publisher=None, device_id=None, settings=None):
    safe_print("Console ready. Type 'help' for commands.", component="SYSTEM")

    db_settings = pi_settings.get("DB", {})

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
        try:
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
                if pi_settings.get("device").get("device_id") == "pi1_door_001":
                    if "DB" not in actuator_registry:
                        run_db(pi_settings.get("DB"), threads, stop_event,
                                print_fn=lambda m: safe_print(m, component="DB"),
                                mqtt_publisher=mqtt_publisher, state='on'
                            )
                        actuator_registry.add("DB")
                    if "DL" not in actuator_registry:
                        run_dl(pi_settings.get("DL", {}), threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="DL"),
                            mqtt_publisher=mqtt_publisher, state='on'
                        )
                        actuator_registry.add("DL")
                if pi_settings.get("device").get("device_id") == "pi3_bedroom_001":
                    if "LCD" not in actuator_registry:
                        run_lcd(pi_settings.get("LCD", {}), threads, stop_event,
                                print_fn=lambda m: safe_print(m, component="LCD"),
                                mqtt_publisher=mqtt_publisher,
                                state=True)
                        actuator_registry.add("LCD")
                if "RGB_LED" not in actuator_registry:
                    run_rgb(pi_settings.get("RGB_LED", {}), threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="RGB_LED"),
                            mqtt_publisher=mqtt_publisher, device_id=device_id)
                    actuator_registry.add("RGB_LED")
                    safe_print(f"All actuators turned on for device {device_id}, {pi_settings.get('RGB_LED')}", component="SYSTEM")

            elif op == "buzz":
                sub = parts[1].lower() if len(parts) > 1 else ""
                safe_print(f"Buzz command: {sub}", component="SYSTEM")
                if sub == "on":
                    if "DB" in actuator_registry:
                        safe_print("DB is already turned on", component="SYSTEM")
                    else:
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
                dl_settings = pi_settings.get("DL", {})

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

            elif op == "door":
                sub = parts[1].lower() if len(parts) > 1 else ""

                if sub == "open":
                    simulate_door(mqtt_publisher, device_id, "open")

                elif sub == "close":
                    simulate_door(mqtt_publisher, device_id, "closed")

                else:
                    safe_print("Usage: door open | door close", component="SYSTEM")


            elif op == "pin":
                if len(parts) > 1:
                    simulate_pin(mqtt_publisher, device_id, parts[1])
                else:
                    safe_print("Usage: pin <code>", component="SYSTEM")
            elif op == "lcd":
                sub = parts[1].lower() if len(parts) > 1 else ""
                lcd_settings = settings.get("PI3").get("LCD", {})
                if not lcd_settings:
                    safe_print(f"LCD not configured for {pi_settings.get('device_id', 'unknown')}", component="SYSTEM")
                    continue
                safe_print(f"lcd settings: {lcd_settings}", component="LCD")
                if sub == "on":
                    run_lcd(lcd_settings, threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="LCD"),
                            mqtt_publisher=mqtt_publisher,
                            state=True)

                    actuator_registry.add("LCD")

                elif sub == "off":
                    run_lcd(lcd_settings, threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="LCD"),
                            mqtt_publisher=mqtt_publisher,
                            state=False)

                    actuator_registry.discard("LCD")
          
                else:
                    safe_print("Usage: lcd on | lcd off", component="SYSTEM")
            elif op == "rgb":
                sub = parts[1].lower() if len(parts) > 1 else ""
                rgb_settings = settings.get("PI3").get("RGB_LED", {})
                if not rgb_settings:
                    safe_print(f"RGB LED not configured for {pi_settings.get('device_id', 'unknown')}", component="SYSTEM")
                    continue
                safe_print(f"RGB LED settings: {rgb_settings}", component="RGB_LED")
                if sub == "on":
                    run_rgb(rgb_settings, threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="RGB_LED"),
                            mqtt_publisher=mqtt_publisher, device_id=device_id)

                    actuator_registry.add("RGB_LED")
                elif sub == "off":
                    run_rgb(rgb_settings, threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="RGB_LED"),
                            mqtt_publisher=mqtt_publisher, device_id=device_id)

                    actuator_registry.discard("RGB_LED")
                elif sub in ("white", "red", "green", "blue", "yellow", "purple", "light_blue"):
                    simulate_rgb_color_change(mqtt_publisher, sub, device_id)
            else:
                safe_print(f"Unknown command: {cmd}", component="SYSTEM")

        except Exception as e:
            safe_print(f"Error processing command '{cmd}': {e}", component="SYSTEM")

def setup_mqtt(settings, device_id):
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
            safe_print(f"MQTT connected - {mqtt_publisher.client}", component="MQTT")
            mqtt_publisher.start_batch_publisher()
            if device_id == "pi3_bedroom_001":
                create_mqtt_client(device_id, "LCD")
                create_mqtt_client(device_id, "RGB_LED")
            return mqtt_publisher
        else:
            safe_print("MQTT connection failed", component="MQTT")
    else:
        safe_print("Could not connect to MQTT broker", component="MQTT")
    
    return None
    
def create_mqtt_client(device_id, component, broker="localhost", port=1883):
    safe_print(f"Creating MQTT client for {component} subscription...", component="MQTT")
    client_id = f"smarthome_{device_id}_{component}"
    client = mqtt.Client(client_id=client_id)
    client.on_connect = partial(on_connect, component=component)
    
    client.on_disconnect = on_disconnect
    client.on_message = on_dht_message if component == "LCD" else on_command_message

    client.connect(broker, port, 60)
    client.loop_start()

    return client

def on_connect(client, userdata, flags, rc, component=None):
    if rc == 0:
        if component == "LCD":
            safe_print("Connected to MQTT Broker for LCD", component="MQTT")

            client.subscribe("smarthome/pi3_bedroom_001/sensors/dht1")
            client.subscribe("smarthome/pi3_bedroom_001/sensors/dht2")
            client.subscribe("smarthome/pi2_kitchen_001/sensors/dht3")
        elif component == "RGB_LED":
            safe_print("Connected to MQTT Broker for RGB LED", component="MQTT")
            client.subscribe("smarthome/pi3_bedroom_001/sensors/ir")

    else:
        safe_print(f"Failed to connect, return code {rc}", component="MQTT")


def run_pi_instance(pi_name, settings, args): 

    pi_settings = settings.get(pi_name, {})
    device = pi_settings.get("device", {})
    safe_print(f"Starting instance for {pi_name} with device ID {device.get('device_id')}", component="SYSTEM")
    safe_print(f"Device config: {device}", component="SYSTEM")
    threads = []
    stop_event = threading.Event()
    mqtt_publisher = None
    
    safe_print("=" * 60, component="SYSTEM")
    safe_print(f"Starting Smart Home System - {pi_name}", component="SYSTEM")
    safe_print("=" * 60, component="SYSTEM")
    
    actuator_registry = set()
    device_id = device.get("device_id")

    try:
        mqtt_publisher = setup_mqtt(settings, device_id)
        start_actuator_listener(
            device_id,
            pi_settings,
            threads,
            stop_event,
            run_db,
            run_dl,
            safe_print
        )
        
        if "--sensors" in args:
            for name, cfg in pi_settings.items():
                cfg = effective_cfg(name, cfg)

                if name.startswith("DPIR"):
                    safe_print(f"{name} {cfg}", component=name if name in COMPONENT_COLORS else "SYSTEM")
                    run_dpir(cfg, threads, stop_event,
                            print_fn=lambda m, n=name: safe_print(m, component=n),
                            mqtt_publisher=mqtt_publisher, device_id=device_id)
                    
                elif name == "DMS":
                    safe_print(f"{name} {cfg}", component="DMS")
                    run_dms(cfg, threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="DMS"),
                            mqtt_publisher=mqtt_publisher,device_id=device_id)

                elif name.startswith("DUS"):
                    safe_print(f"{name} {cfg}", component=name if name in COMPONENT_COLORS else "SYSTEM")
                    run_dus(cfg, threads, stop_event,
                            print_fn=lambda m, n=name: safe_print(m, component=n),
                            mqtt_publisher=mqtt_publisher,device_id=device_id)
                    
                elif name.startswith("DHT"):
                    safe_print(f"{name} {cfg}", component=name if name in COMPONENT_COLORS else "SYSTEM")

                    run_dht(cfg, threads, stop_event,
                                    print_fn=lambda m, n=name: safe_print(m, component=n),
                                    mqtt_publisher=mqtt_publisher,device_id=device_id)
                    
                elif name == "DS1":
                    safe_print(f"{name} {cfg}", component="DS1")
                    run_ds1(cfg, threads, stop_event,  
                            print_fn=lambda m, n=name: safe_print(m, component="DS1"),
                            mqtt_publisher=mqtt_publisher, device_id=device_id)
                    
                elif name == "DS2":
                    safe_print(f"{name} {cfg}", component="DS2")
                    run_ds2(cfg, threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="DS2"),
                            mqtt_publisher=mqtt_publisher, device_id=device_id)
                    
                elif name == "BTN":
                    safe_print(f"{name} {cfg}", component="BTN")
                    run_kitchen_button(cfg, threads, stop_event,
                                    print_fn=lambda m: safe_print(m, component="BTN"),
                                    mqtt_publisher=mqtt_publisher, device_id=device_id)
                    
                elif name == "4SD":
                    safe_print(f"{name} {cfg}", component="4SD")
                    run_kitchen_4sd(cfg, threads, stop_event,
                                    print_fn=lambda m: safe_print(m, component="4SD"), device_id=device_id)
                    
                elif name == "GSG":
                    safe_print(f"{name} {cfg}", component="GSG")
                    run_kitchen_gsg(cfg, threads, stop_event,
                                    print_fn=lambda m: safe_print(m, component="GSG"),
                                    mqtt_publisher=mqtt_publisher,device_id=device_id)
                elif name == "IR":
                    safe_print(f"{name} {cfg}", component="IR")
                    run_ir(cfg, threads, stop_event,
                            print_fn=lambda m: safe_print(m, component="IR"),
                            mqtt_publisher=mqtt_publisher, device_id=device_id)

        safe_print("=" * 60, component="SYSTEM")
        safe_print("System running. Press Ctrl+C to stop.", component="SYSTEM")
        safe_print("=" * 60, component="SYSTEM")

        command_loop(stop_event, actuator_registry, pi_settings, threads, mqtt_publisher,device_id, settings)

    except KeyboardInterrupt:
        safe_print("Stopping app (KeyboardInterrupt)", component="SYSTEM")
        stop_event.set()
    except Exception as e:
        safe_print(f"Error in main loop: {e}", component="SYSTEM")
        stop_event.set()
    finally:
        if mqtt_publisher:
            safe_print("Disconnecting MQTT...", component="MQTT")
            mqtt_publisher.disconnect()
        
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

def main(args):
    settings = load_settings()
    pi_name = get_pi_context(args)

    threads = []

    safe_print("=" * 60, component="SYSTEM")
    safe_print(f"Starting Smart Home System for: {pi_name}", component="SYSTEM")
    safe_print("=" * 60, component="SYSTEM")

    # for pi_name in pi_names:
    t = threading.Thread(
        target=run_pi_instance,
        args=(pi_name, settings, args),
        daemon=True
    )
    t.start()
    threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        safe_print("Stopping all instances...", component="SYSTEM")
    except Exception as e:
        safe_print(f"Error in main thread: {e}", component="SYSTEM")


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)