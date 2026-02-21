import RPi.GPIO as GPIO
import time
import sensors.LA_DHT as DHT

def loop(pin, mqtt_publisher, device_id, component, print_fn, interval):
    dht = DHT.DHT(pin)   #create a DHT class object
    sumCnt = 0              #number of reading times 
    while(True):
        sumCnt += 1         #counting number of reading times
        chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        print ("The sumCnt is : %d, \t chk    : %d"%(sumCnt,chk))
        if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            publish(mqtt_publisher, device_id, component, print_fn, dht.humidity, dht.temperature)
        elif(chk is dht.DHTLIB_ERROR_CHECKSUM): #data check has errors
            print("DHTLIB_ERROR_CHECKSUM!!")
        elif(chk is dht.DHTLIB_ERROR_TIMEOUT):  #reading DHT times out
            print("DHTLIB_ERROR_TIMEOUT!")
        else:               #other errors
            print("Other error!")
            
        print("Humidity : %.2f, \t Temperature : %.2f \n"%(dht.humidity,dht.temperature))
        time.sleep(2)       


def publish(mqtt_publisher, device_id, component, print_fn, humidity, temperature):
    print_fn(f"{component} TEMP={temperature:.1f}°C HUM={humidity:.1f}%")

    if mqtt_publisher and mqtt_publisher.connected:
        payload = {
            "device_id": device_id,
            "sensor_type": "dht",
            "component": component,
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": time.time()
        }

        topic = f"smarthome/{device_id}/sensors/{component.lower()}"
        mqtt_publisher.publish(topic, payload, use_batch=True)      


def run_dht(pin, stop_event, print_fn=print,
                    mqtt_publisher=None,
                    device_id="pi",
                    component="DHT3",
                    interval=2):
    try:
        while not stop_event.is_set():
            loop(pin, mqtt_publisher, device_id, component, print_fn, interval)
    except KeyboardInterrupt:
        GPIO.cleanup()
        exit()  
    finally:
        GPIO.cleanup(pin)
        print_fn(f"{component} stopped")
