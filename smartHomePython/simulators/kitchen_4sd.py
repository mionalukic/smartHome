import time
import threading


def run_4sd_simulator(stop_event, print_fn, state):

    print_fn("4SD simulator started")

    visible = True

    while not stop_event.wait(0.5):

        value, blink = state.get()

        if blink:
            visible = not visible
        else:
            visible = True

        if visible:
            print_fn(f"4SD DISPLAY: {value}")
        else:
            print_fn("4SD DISPLAY:    ")
            
class Kitchen4SDSimulator:

    def __init__(self, print_fn=print):
        self.print_fn = print_fn
        self.value = "0000"
        self.blink = False

    def handle_command(self, payload):
        if payload.get("command") == "display":
            self.value = payload.get("mmss", "0000")
            self.blink = payload.get("blink", False)

    def run(self, stop_event):
        while not stop_event.is_set():

            if self.blink:
                self.print_fn("4SD DISPLAY: 0000")
                time.sleep(0.5)
                self.print_fn("4SD DISPLAY:    ")
                time.sleep(0.5)
            else:
                self.print_fn(f"4SD DISPLAY: {self.value}")
                time.sleep(1)
