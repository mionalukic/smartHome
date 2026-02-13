import time
import traceback
try:
    from . import MPU6050
except ImportError as e:
    print("❌ ImportError while importing MPU6050:")
    print(str(e))
    traceback.print_exc()
    MPU6050 = None
except Exception as e:
    print("❌ Unexpected error while importing MPU6050:")
    print(str(e))
    traceback.print_exc()
    MPU6050 = None


def run_kitchen_gsg(stop_event,
                    print_fn=print,
                    mqtt_publisher=None,
                    device_id="pi",
                    component="GSG",
                    interval=0.5,
                    threshold=20000):

    if MPU6050 is None:

        print_fn("MPU6050 library not available")
        return

    mpu = MPU6050.MPU6050()
    mpu.dmp_initialize()

    print_fn("GSG (REAL) started")

    while not stop_event.is_set():
        accel = mpu.get_acceleration()   # [x, y, z]
        gyro = mpu.get_rotation()        # [x, y, z]
        ts = time.time()

        movement = (
            abs(accel[0]) > threshold or
            abs(accel[1]) > threshold or
            abs(accel[2]) > threshold
        )

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
                "timestamp": ts
            }

            topic = f"smarthome/{device_id}/sensors/{component.lower()}"
            mqtt_publisher.publish(topic, payload, use_batch=True)

        time.sleep(interval)

    print_fn("GSG stopped")
