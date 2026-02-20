import time
import traceback
import MPU6050

def run_kitchen_gsg(stop_event,
                    print_fn=print,
                    mqtt_publisher=None,
                    device_id="pi",
                    component="GSG",
                    interval=0.5,
                    threshold=20000):


    mpu = MPU6050()
    mpu.dmp_initialize()

    print_fn("GSG REAL started")

    while not stop_event.is_set():
        try:
            accel = mpu.get_acceleration()
            gyro = mpu.get_rotation()

            accel_g = [
                accel[0] / 16384.0,
                accel[1] / 16384.0,
                accel[2] / 16384.0
            ]

            gyro_dps = [
                gyro[0] / 131.0,
                gyro[1] / 131.0,
                gyro[2] / 131.0
            ]
            print_fn(
                "a/g:%d\t%d\t%d\t%d\t%d\t%d" %
                (accel[0], accel[1], accel[2],
                gyro[0], gyro[1], gyro[2])
            )

            print_fn(
                "a/g:%.2f g\t%.2f g\t%.2f g\t%.2f d/s\t%.2f d/s\t%.2f d/s" %
                (accel_g[0], accel_g[1], accel_g[2],
                gyro_dps[0], gyro_dps[1], gyro_dps[2])
            )

            if mqtt_publisher and mqtt_publisher.connected:
                payload = {
                    "device_id": device_id,
                    "sensor_type": "gyroscope",
                    "component": component,

                    "accel_x": accel_g[0],
                    "accel_y": accel_g[1],
                    "accel_z": accel_g[2],

                    "gyro_x": gyro_dps[0],
                    "gyro_y": gyro_dps[1],
                    "gyro_z": gyro_dps[2],

                    "simulated": False,
                    "timestamp": time.time()
                }

                topic = f"smarthome/{device_id}/sensors/{component.lower()}"
                mqtt_publisher.publish(topic, payload, use_batch=True)
        except Exception as e:
            print_fn(f"GSG read error: {e}")
            traceback.print_exc()
        time.sleep(interval)

    print_fn("GSG stopped")
