from time import sleep, time

def publish(mqtt_publisher, device_id, color, value):
    if mqtt_publisher and mqtt_publisher.connected:
        payload = {
            "device_id": device_id,
            "actuator_type": "rgb_led",
            "simulated": True,
            "light_color": color,
            "value": value,
            "timestamp": time()
        }

        topic = f"smarthome/{device_id}/actuators/rgb_led"
        mqtt_publisher.publish(topic, payload, use_batch=True)


def run_rgb_led_simulator(color_state, print_fn=print, mqtt_publisher=None, device_id='pi'):
    command = color_state["value"]
    if command == "white":
        publish(mqtt_publisher, device_id, "white", 1)
    elif command == "red":
        publish(mqtt_publisher, device_id, "red", 2)
    elif command == "green":
        publish(mqtt_publisher, device_id, "green", 3)
    elif command == "blue":
        publish(mqtt_publisher, device_id, "blue", 4)
    elif command == "yellow":
        publish(mqtt_publisher, device_id, "yellow", 5)
    elif command == "purple":
        publish(mqtt_publisher, device_id, "purple", 6)
    elif command == "light_blue":
        publish(mqtt_publisher, device_id, "light_blue", 7)
    else:
        publish(mqtt_publisher, device_id, "off", 0)
    print_fn(f"RGB LED set to {command}")

