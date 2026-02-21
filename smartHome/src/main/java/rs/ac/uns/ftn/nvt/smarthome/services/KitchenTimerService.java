package rs.ac.uns.ftn.nvt.smarthome.services;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import rs.ac.uns.ftn.nvt.smarthome.state.SystemStateStore;

@Service
public class KitchenTimerService {

    private final SystemStateStore store;
    private final ActuatorCommandService actuator;

    public KitchenTimerService(SystemStateStore store, ActuatorCommandService actuator) {
        this.store = store;
        this.actuator = actuator;
    }

    public synchronized void setTime(int seconds) {
        store.setKitchenTimerSeconds(Math.max(0, seconds));
        store.setKitchenBlinking(false);
        pushDisplay(false);
    }

    public synchronized void setAddN(int n) {
        store.setKitchenAddSecondsN(Math.max(1, n));
    }

    public synchronized void onButtonPressed() {
        if (store.isKitchenBlinking()) {
            // stop treperenje
            store.setKitchenBlinking(false);
            pushDisplay(false); // ostaje 00:00
            return;
        }
        // dodaj N sekundi
        store.setKitchenTimerSeconds(store.getKitchenTimerSeconds() + store.getKitchenAddSecondsN());
        pushDisplay(false);
    }

    @Scheduled(fixedRate = 1000)
    public synchronized void tick() {
        if (store.isKitchenBlinking()) return;

        int remaining = store.getKitchenTimerSeconds();
        if (remaining <= 0) return;

        remaining -= 1;
        store.setKitchenTimerSeconds(remaining);

        if (remaining == 0) {
            store.setKitchenBlinking(true);
            pushDisplay(true); // blink 00:00
        } else {
            pushDisplay(false);
        }
    }

    private void pushDisplay(boolean blink) {
        String mmss = toMmss(store.getKitchenTimerSeconds());
        System.out.println(mmss);
        String payload = String.format("{\"command\":\"display\",\"mmss\":\"%s\",\"blink\":%s}", mmss, blink);
        actuator.send("smarthome/pi2_kitchen_001/actuators/4sd", payload);

    }

    private String toMmss(int totalSeconds) {
        int mm = totalSeconds / 60;
        int ss = totalSeconds % 60;
        return String.format("%02d%02d", mm, ss);
    }
}

