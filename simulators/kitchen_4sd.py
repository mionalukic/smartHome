import time

def run_4sd_simulator(
    stop_event,
    print_fn=print,
    start_seconds=30,
    blink_seconds=5
):
    """
    4SD simulator:
    - broji unazad od start_seconds
    - na 0 treperi blink_seconds
    - restartuje brojač
    """

    print_fn(f"4SD simulator started ({start_seconds}s)")
    remaining = start_seconds
    blink = False
    blink_count = 0

    while not stop_event.is_set():

        if remaining > 0:
            mm = remaining // 60
            ss = remaining % 60
            print_fn(f"4SD DISPLAY: {mm:02d}{ss:02d}")
            remaining -= 1
            time.sleep(1)

        else:
            # BLINK STATE
            if blink_count < blink_seconds:
                blink = not blink
                if blink:
                    print_fn("4SD DISPLAY: 0000")
                else:
                    print_fn("4SD DISPLAY:    ")
                blink_count += 1
                time.sleep(0.5)
            else:
                # RESET
                print_fn("4SD RESET")
                remaining = start_seconds
                blink_count = 0
                blink = False

    print_fn("4SD simulator stopped")
