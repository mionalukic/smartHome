import json
import threading
from components.door_buzzer import buzz_off, buzz_on
from components.rgb_led import change_color
import paho.mqtt.client as mqtt

from components.kitchen_4sd import handle_4sd_command

def start_actuator_listener(device_id, pi_settings, threads, stop_event,
                            run_db, run_dl, safe_print,
                            run_kitchen_4sd):

    def on_connect(client, userdata, flags, rc):
        topic = f"smarthome/{device_id}/actuators/#"
        safe_print(f"Subscribed to {topic}", component="MQTT")
        client.subscribe(topic)

    def on_message(client, userdata, msg):
        
        if "lcd_display" in msg.topic:
            return
        # safe_print(f"Received MQTT message on topic {msg.topic}", component="MQTT")
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic

            safe_print(f"ACTUATOR COMMAND -> {topic} | {payload}", component="MQTT")

            if "door_buzzer" in topic:
                if payload.get("command") == "on": buzz_on() 
                else: buzz_off()

            elif "door_light" in topic:
                state = payload.get("command") == "on"
                run_dl(
                    pi_settings.get("DL", {}),
                    threads,
                    stop_event,
                    print_fn=lambda m: safe_print(m, component="DL"),
                    state=state
                )

            elif topic.endswith("/actuators/4sd"):
                safe_print(f"4SD COMMAND RECEIVED: {payload}", component="4SD")
                handle_4sd_command(payload, print_fn=lambda m: safe_print(m, component="4SD"))

            elif "rgb" in msg.topic:
                change_color(payload.get("value"))
                    
        except Exception as e:
            safe_print(f"Actuator error: {e}", component="SYSTEM")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)

    thread = threading.Thread(target=client.loop_forever, daemon=True)
    thread.start()
