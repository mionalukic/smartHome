package rs.ac.uns.ftn.nvt.smarthome.rules;


import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;
import rs.ac.uns.ftn.nvt.smarthome.services.AlarmService;
import rs.ac.uns.ftn.nvt.smarthome.state.SystemStateStore;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

@Component
public class DoorAlarmRule {

    private static final long OPEN_TOO_LONG_MS = 5000;

    @Autowired private SystemStateStore stateStore;
    @Autowired private AlarmService alarmService;

    private final ScheduledExecutorService scheduler =
            Executors.newSingleThreadScheduledExecutor();


    public void onEvent(SensorEvent e) {

        if (!"door_sensor".equals(e.getSensor_type())) return;

        String c = e.getComponent();
        if (c == null) return;

        long nowMs = System.currentTimeMillis();
        String state = e.getState();

        if ("open".equalsIgnoreCase(state)) {
            stateStore.markDoorOpen(c, nowMs);

            Long since = stateStore.getDoorOpenSince(c);
            if (since != null && nowMs - since >= OPEN_TOO_LONG_MS) {
                alarmService.activate("Door open > 5s", c);
            }

        } else if ("closed".equalsIgnoreCase(state)) {
            stateStore.clearDoorOpen(c);

            // ako je alarm aktivan zbog vrata, gasi kad se zatvore
            alarmService.deactivate("Door closed");
        }
    }

    @PostConstruct
    public void startMonitoring() {

        scheduler.scheduleAtFixedRate(() -> {

            long now = System.currentTimeMillis();

            for (String component : new String[]{"DS1","DS2"}) {

                Long since = stateStore.getDoorOpenSince(component);

                if (since != null && now - since >= OPEN_TOO_LONG_MS) {

                    alarmService.activate("Door open > 5s", component);
                }
            }

        }, 1, 1, TimeUnit.SECONDS);
    }

}
