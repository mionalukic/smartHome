from queue import Empty
from time import sleep, time

def publish(mqtt_publisher, device_id, color, value):
    if mqtt_publisher and mqtt_publisher.connected:
        payload = {
            "device_id": device_id,
            "actuator_type": "rgb_led",
            "simulated": True,
            "light_color": color,
            "timestamp": time()
        }

        topic = f"smarthome/{device_id}/actuators/rgb_led"
        mqtt_publisher.publish(topic, payload, use_batch=True)


def run_rgb_led_simulator(color_queue, print_fn=print, mqtt_publisher=None, device_id='pi'):
    last_color = None

    while True:
        try:
            current_color = color_queue.get(timeout=0.1)
            if current_color != last_color:
                print_fn(f"[RGB_SIM] LED color is now {current_color}")
                last_color = current_color
                publish(mqtt_publisher, device_id, current_color, 1)
        except Empty:
            continue
