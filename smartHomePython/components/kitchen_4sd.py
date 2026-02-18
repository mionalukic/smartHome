from sensors.kitchen_4sd import Kitchen4SD

display_instance = None

def run_kitchen_4sd(settings, threads, stop_event,
                    print_fn=print, mqtt_publisher=None, device_id="unknown"):

    global display_instance

    if settings.get("simulated", True):
        from simulators.kitchen_4sd import Kitchen4SDSimulator
        display_instance = Kitchen4SDSimulator(print_fn)
        t = threading.Thread(
            target=display_instance.run,
            args=(stop_event,)
        )
    else:
        display_instance = Kitchen4SD(
            settings["segments"],
            settings["digits"],
            settings.get("refresh_ms", 1)
        )
        t = threading.Thread(
            target=display_instance.run,
            args=(stop_event,)
        )

    t.start()
    threads.append(t)
