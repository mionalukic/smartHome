import sys
import json
import time
import signal
from datetime import datetime
import paho.mqtt.client as mqtt

COLORS = {
    "SUBSCRIBER": "\033[38;5;51m",   # bright cyan
    "DMS": "\033[38;5;118m",          # green
    "DPIR1": "\033[38;5;39m",         # blue
    "DS1": "\033[38;5;214m",          # yellow/orange
    "DUS1": "\033[38;5;141m",         # purple
    "DB": "\033[38;5;208m",           # orange
    "DL": "\033[38;5;220m",           # yellow
    "ERROR": "\033[38;5;196m",        # red
    "SUCCESS": "\033[38;5;46m",       # bright green
}
RESET = "\033[0m"

def colored_print(message, color_key="SUBSCRIBER"):
    color = COLORS.get(color_key, "")
    print(f"{color}[{color_key}] {message}{RESET}", flush=True)

def format_timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def get_component_from_topic(topic):
    parts = topic.split('/')
    if len(parts) >= 4:
        component = parts[3].upper()
        return component
    return "UNKNOWN"

def format_payload(payload_str):
    try:
        data = json.loads(payload_str)
        
        component = data.get('component', 'UNKNOWN')
        sensor_type = data.get('sensor_type', '')
        
        if sensor_type == 'door_membrane_switch':
            key = data.get('key', '')
            event = data.get('event', '')
            simulated = data.get('simulated', False)
            sim_tag = " [SIM]" if simulated else ""
            return f"Key {event}: '{key}'{sim_tag}", component
        
        elif sensor_type == 'door_motion_sensor':
            state = data.get('state', '')
            value = data.get('value', '')
            simulated = data.get('simulated', False)
            sim_tag = " [SIM]" if simulated else ""
            return f"Motion: {state} (value={value}){sim_tag}", component
        
        elif sensor_type == 'door_sensor':
            state = data.get('state', '')
            simulated = data.get('simulated', False)
            sim_tag = " [SIM]" if simulated else ""
            return f"Door: {state}{sim_tag}", component
        
        elif sensor_type == 'door_ultrasonic':
            distance = data.get('distance', 0)
            unit = data.get('unit', 'cm')
            simulated = data.get('simulated', False)
            sim_tag = " [SIM]" if simulated else ""
            return f"Distance: {distance}{unit}{sim_tag}", component
        
        else:
            return json.dumps(data, indent=2), component
    
    except json.JSONDecodeError:
        return payload_str, "UNKNOWN"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        colored_print("Connected to MQTT Broker", "SUCCESS")
        colored_print("Subscribing to: smarthome/#", "SUBSCRIBER")
        client.subscribe("smarthome/#")
        print("=" * 80)
    else:
        colored_print(f"Connection failed with code {rc}", "ERROR")
        sys.exit(1)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        colored_print(f"Unexpected disconnection (code {rc})", "ERROR")

def on_message(client, userdata, msg):
    timestamp = format_timestamp()
    topic = msg.topic
    payload = msg.payload.decode()
    
    formatted_payload, component = format_payload(payload)
    
    color_key = component if component in COLORS else "SUBSCRIBER"
    
    print(f"{COLORS.get(color_key, '')}[{component}] {timestamp} | {topic}{RESET}")
    print(f"{COLORS.get(color_key, '')}    └─ {formatted_payload}{RESET}")
    print()

def main():
    broker = "192.168.107.197"
    port = 1883
    
    if len(sys.argv) > 1:
        broker = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    print("=" * 80)
    colored_print("MQTT Subscriber Starting", "SUBSCRIBER")
    colored_print(f"Broker: {broker}:{port}", "SUBSCRIBER")
    print("=" * 80)
    
    client = mqtt.Client(client_id="smarthome_subscriber")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    def signal_handler(sig, frame):
        print("\n")
        colored_print("Stopping subscriber...", "SUBSCRIBER")
        client.disconnect()
        print("=" * 80)
        colored_print("Subscriber stopped", "SUCCESS")
        print("=" * 80)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        client.connect(broker, port, 60)
        client.loop_forever()
    except Exception as e:
        colored_print(f"Error: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()