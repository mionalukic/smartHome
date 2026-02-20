package rs.ac.uns.ftn.nvt.smarthome.state;

import lombok.Getter;
import lombok.Setter;
import org.springframework.stereotype.Component;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class SystemStateStore {

    @Getter @Setter
    private SecurityMode mode = SecurityMode.DISARMED;

    public boolean isArmed() { return mode == SecurityMode.ARMED; }
    public boolean isAlarm() { return mode == SecurityMode.ALARM; }
    public boolean isDisarmed() { return mode == SecurityMode.DISARMED; }


    @Getter @Setter private int kitchenTimerSeconds = 0;
    @Getter @Setter private int kitchenAddSecondsN = 10; // default
    @Getter @Setter private boolean kitchenBlinking = false;
    @Getter @Setter private long kitchenLastTickMs = System.currentTimeMillis();


    @Getter @Setter
    private int peopleCount = 0;

    private final Map<String, Long> doorOpenSinceMs = new ConcurrentHashMap<>();

    public void markDoorOpen(String component, long nowMs) {
        doorOpenSinceMs.putIfAbsent(component, nowMs);
    }

    public void clearDoorOpen(String component) {
        doorOpenSinceMs.remove(component);
    }

    public Long getDoorOpenSince(String component) {
        return doorOpenSinceMs.get(component);
    }


    @Getter
    private volatile boolean entryPending = false;
    @Getter
    private volatile String entryDoorComponent = null;
    @Getter
    private volatile long entryStartedAtMs = 0;

    public void startEntryDelay(String component) {
        this.entryPending = true;
        this.entryDoorComponent = component;
        this.entryStartedAtMs = System.currentTimeMillis();
    }

    public void cancelEntryDelay() {
        this.entryPending = false;
        this.entryDoorComponent = null;
        this.entryStartedAtMs = 0;
    }


    // Čuvamo ceo event po komponenti
    private final Map<String, SensorEvent> lastSensorEvents =
            new ConcurrentHashMap<>();

    public void incrementPeople() {
        this.peopleCount++;
    }

    public void decrementPeople() {
        if (this.peopleCount > 0) {
            this.peopleCount--;
        }
    }

    public void updateEvent(SensorEvent event) {

        if (event == null || event.getComponent() == null) {
            return;
        }

        lastSensorEvents.put(event.getComponent(), event);
    }

    public SensorEvent getLastEvent(String component) {
        return lastSensorEvents.get(component);
    }
}
