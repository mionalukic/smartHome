import time
import random


def run_kitchen_gsg_simulator(stop_event,
                              print_fn=print,
                              mqtt_publisher=None,
                              device_id="pi",
                              component="GSG",
                              interval=0.5):

    print_fn("GSG simulator started")

    while not stop_event.is_set():
        # mala buka
        accel = [
            random.randint(-3000, 3000),
            random.randint(-3000, 3000),
            random.randint(15000, 17000)
        ]

        # povremeni "udar"
        movement = random.random() < 0.1
        if movement:
            accel[0] += random.randint(25000, 40000)

        gyro = [
            random.randint(-200, 200),
            random.randint(-200, 200),
            random.randint(-200, 200)
        ]

        ts = time.time()

        print_fn(
            f"GSG accel={accel} gyro={gyro} movement={movement}"
        )

        if mqtt_publisher and mqtt_publisher.connected:
            payload = {
                "device_id": device_id,
                "sensor_type": "gyroscope",
                "component": component,
                "accel_x": accel[0],
                "accel_y": accel[1],
                "accel_z": accel[2],
                "gyro_x": gyro[0],
                "gyro_y": gyro[1],
                "gyro_z": gyro[2],
                "movement": movement,
                "simulated": True,
                "timestamp": ts
            }

            topic = f"smarthome/{device_id}/sensors/{component.lower()}"
            mqtt_publisher.publish(topic, payload, use_batch=True)

        time.sleep(interval)

    print_fn("GSG simulator stopped")

    
def simulate_gsg_high_movement(mqtt_publisher,
                                device_id,
                                component="GSG"):

    import time

    accel = [50000, 50000, 50000]  # ekstremna vrednost
    gyro = [1000, 1000, 1000]

    payload = {
        "device_id": device_id,
        "sensor_type": "gyroscope",
        "component": component,
        "accel_x": accel[0],
        "accel_y": accel[1],
        "accel_z": accel[2],
        "gyro_x": gyro[0],
        "gyro_y": gyro[1],
        "gyro_z": gyro[2],
        "movement": True,
        "simulated": True,
        "timestamp": time.time()
    }

    topic = f"smarthome/{device_id}/sensors/{component.lower()}"

    if mqtt_publisher and mqtt_publisher.connected:
        mqtt_publisher.publish(topic, payload, use_batch=False)
