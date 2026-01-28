from simulators.door_light import run_dl_simulator
import threading
import time

def run_dl(settings, threads, stop_event, print_fn=print, mqtt_publisher=None, state=None):
   
    if settings.get('simulated', True):
        if state is not None:
            state_str = "ON" if state else "OFF"
            print_fn(f"Door light turned {state_str} (simulated)")

            if mqtt_publisher and mqtt_publisher.connected:
                data = {
                    "device_id": settings.get('device_id', 'pi1'),
                    "sensor_type": "door_light",
                    "component": "DL",
                    "state": state,
                    "simulated": True,
                    "timestamp": time.time()
                }

                topic = f"smarthome/{settings.get('device_id', 'pi1')}/sensors/dl"
                mqtt_publisher.publish(topic, data, use_batch=True)
        else:
            dl_thread = threading.Thread(
                target=run_dl_simulator,
                args=(stop_event, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'))
            )
            dl_thread.start()
            threads.append(dl_thread)
    else:
        from sensors.door_light import DL
        dl = DL(settings['pin'])
        dl.set_state(state, print_fn, mqtt_publisher, settings.get('device_id', 'pi1'))
