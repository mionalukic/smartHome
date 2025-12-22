from simulators.door_light import run_dl_simulator


def run_dl(state, settings, threads, stop_event, print_fn=print):
    if settings["simulated"]:
        run_dl_simulator(state, print_fn)
    else:
        from sensors.door_light import run_dl_led
        run_dl_led(state, settings["pin"], print_fn)
