from queue import Empty
from time import sleep, time

def publish(mqtt_publisher, device_id, color, value):
    if mqtt_publisher and mqtt_publisher.connected:
        payload = {
            "device_id": device_id,
            "sensor_type": "rgb_led",
            "simulated": True,
            "value": color,
            "color_value": value,
            "component": "RGB_LED",
            "timestamp": time()
        }

        topic = f"smarthome/{device_id}/sensors/rgb_led"
        mqtt_publisher.publish(topic, payload, use_batch=True)

def getValue(color):
    color_values = {
        "off": 0,
        "red": 1,
        "green": 2,
        "blue": 3,
        "white": 4,
        "yellow": 5,
        "purple": 6,
        "light_blue": 7
    }
    return color_values.get(color, 0)

def run_rgb_led_simulator(color_queue, print_fn=print, mqtt_publisher=None, device_id='pi', stop_event=None):
    last_color = None
    while not stop_event.is_set():
        try:
            current_color = color_queue.get(timeout=0.1)
            if current_color != last_color:
                print_fn(f"Current color is now {current_color}")
                last_color = current_color
                value = getValue(current_color)
                publish(mqtt_publisher, device_id, current_color, value)
        except Empty:
            continue
        except Exception as e:
            print_fn(f"Error in simulator loop: {e}")
    print_fn(f"RGB LED simulator stopped for device {device_id}")
    
