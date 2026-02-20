import json
import threading
import paho.mqtt.client as mqtt


def start_actuator_listener(device_id, pi_settings, threads, stop_event,
                            run_db, run_dl, safe_print,
                            display_instance=None):

    def on_connect(client, userdata, flags, rc):
        topic = f"smarthome/{device_id}/actuators/#"
        safe_print(f"Subscribed to {topic}", component="MQTT")
        client.subscribe(topic)

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic

            safe_print(f"ACTUATOR COMMAND -> {topic} | {payload}", component="MQTT")

            if "door_buzzer" in topic:
                state = payload.get("command") == "on"
                run_db(
                    pi_settings.get("DB", {}),
                    threads,
                    stop_event,
                    print_fn=lambda m: safe_print(m, component="DB"),
                    state=state
                )

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
                payload = json.loads(msg.payload.decode())
                safe_print(f"4SD COMMAND RECEIVED: {payload}", component="4SD")
                if display_instance:
                    display_instance.handle_command(payload)

        except Exception as e:
            safe_print(f"Actuator error: {e}", component="SYSTEM")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)

    thread = threading.Thread(target=client.loop_forever, daemon=True)
    thread.start()
