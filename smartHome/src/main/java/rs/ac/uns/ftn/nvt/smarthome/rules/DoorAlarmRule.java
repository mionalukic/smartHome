package rs.ac.uns.ftn.nvt.smarthome.rules;


import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;
import rs.ac.uns.ftn.nvt.smarthome.interfaces.SensorRule;
import rs.ac.uns.ftn.nvt.smarthome.services.SecurityStateService;
import rs.ac.uns.ftn.nvt.smarthome.state.AlarmReason;
import rs.ac.uns.ftn.nvt.smarthome.state.DisarmMethod;
import rs.ac.uns.ftn.nvt.smarthome.state.SystemStateStore;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

@Component
public class DoorAlarmRule implements SensorRule {

    private static final long OPEN_TOO_LONG_MS = 5000;

    @Autowired private SystemStateStore stateStore;
    @Autowired private SecurityStateService securityStateService;

    private final ScheduledExecutorService scheduler =
            Executors.newSingleThreadScheduledExecutor();


    public void onEvent(SensorEvent e) {

        if (!"door_sensor".equals(e.getSensor_type())) return;

        String c = e.getComponent();
        if (c == null) return;

        long nowMs = System.currentTimeMillis();
        String state = e.getState();

        if ("open".equalsIgnoreCase(state)) {

            if (!stateStore.isArmed()) return;

            if (!stateStore.isEntryPending()) {
                stateStore.startEntryDelay(c);
                System.out.println("ENTRY DELAY STARTED for " + c);
            }

        } else if ("closed".equalsIgnoreCase(state)) {
            stateStore.clearDoorOpen(c);

            if (stateStore.isAlarm()) {
                securityStateService.deactivateAlarm(DisarmMethod.WEB);
            }
        }
    }

    @PostConstruct
    public void startMonitoring() {

        scheduler.scheduleAtFixedRate(() -> {

            if (!stateStore.isArmed()) return;
            if (stateStore.isAlarm()) return;


            for (String component : new String[]{"DS1","DS2"}) {

                Long since = stateStore.getDoorOpenSince(component);
                if (stateStore.isEntryPending()) {

                    long now = System.currentTimeMillis();
                    long diff = now - stateStore.getEntryStartedAtMs();

                    if (diff >= OPEN_TOO_LONG_MS) {

                        securityStateService.triggerAlarm(
                                AlarmReason.DOOR_OPEN_TOO_LONG,
                                stateStore.getEntryDoorComponent()
                        );

                        stateStore.cancelEntryDelay();
                    }
                }
            }

        }, 1, 1, TimeUnit.SECONDS);
    }

}
