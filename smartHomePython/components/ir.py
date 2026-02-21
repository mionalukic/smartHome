import threading
from simulators.ir import run_ir_sensor_simulator


def run_ir(settings, threads, stop_event,
           print_fn=print, mqtt_publisher=None, device_id="unknown"):

    device_id = device_id if device_id else settings.get("device_id", "pi3_bedroom_001")

    if settings.get("simulated", True):
        t = threading.Thread(
            target=run_ir_sensor_simulator,
            args=(stop_event, print_fn, mqtt_publisher, device_id)
        )
    else:
        from sensors.ir import IRSensor, run_ir_loop
        ir = IRSensor(settings.get("pin", 17))
        ir.setUp(print_fn, mqtt_publisher, device_id)

        t = threading.Thread(
            target=run_ir_loop,
            args=(ir, stop_event, print_fn, mqtt_publisher, device_id)
        )

    t.start()
    threads.append(t)
