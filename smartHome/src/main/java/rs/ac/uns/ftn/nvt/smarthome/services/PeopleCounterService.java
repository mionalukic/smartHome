package rs.ac.uns.ftn.nvt.smarthome.services;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import rs.ac.uns.ftn.nvt.smarthome.state.AlarmReason;

import java.util.concurrent.atomic.AtomicInteger;

@Service
@RequiredArgsConstructor
public class PeopleCounterService {

    private final AtomicInteger peopleCounter = new AtomicInteger(0);
    private final SecurityStateService securityStateService;

    public void enter(String component) {
        int value = peopleCounter.incrementAndGet();

        if (value == 1) {
            securityStateService.triggerAlarm(
                    AlarmReason.UNEXPECTED_ENTRANCE,
                    component
            );
        }

        System.out.println("PEOPLE COUNTER: " + value);
    }

    public void exit() {
        while (true) {
            int current = peopleCounter.get();

            if (current == 0) {
                System.out.println("ERROR - Ghost exited the room");
                return;
            }

            if (peopleCounter.compareAndSet(current, current - 1)) {
                System.out.println("Person exited the room");
                System.out.println("PEOPLE COUNTER: " + (current - 1));
                return;
            }
        }
    }

    public void reset() {
        peopleCounter.set(0);
        System.out.println("PEOPLE COUNTER RESET TO 0");
    }

    public void detectMovement() {
        if (peopleCounter.get() == 0)
            securityStateService.triggerAlarm(
                    AlarmReason.UNEXPECTED_ENTRANCE,
                    "DPIR3"
            );
    }
}