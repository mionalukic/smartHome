package rs.ac.uns.ftn.nvt.smarthome.services;

import org.springframework.stereotype.Service;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;
import rs.ac.uns.ftn.nvt.smarthome.interfaces.AlarmNotifier;
import rs.ac.uns.ftn.nvt.smarthome.state.*;

@Service
public class SecurityStateService {

    private final SystemStateStore stateStore;
    private final InfluxWriter influxWriter;
    private final ActuatorCommandService actuator;
    private final AlarmNotifier alarmNotifier; // web obaveštenje (stub za sada)

    public SecurityStateService(SystemStateStore stateStore,
                                InfluxWriter influxWriter,
                                ActuatorCommandService actuator,
                                AlarmNotifier alarmNotifier) {
        this.stateStore = stateStore;
        this.influxWriter = influxWriter;
        this.actuator = actuator;
        this.alarmNotifier = alarmNotifier;
    }

    public synchronized void arm(DisarmMethod method) {
        if (stateStore.getMode() == SecurityMode.ARMED) return;
        if (stateStore.getMode() == SecurityMode.ALARM) return; // ne armuj dok alarm traje

        stateStore.setMode(SecurityMode.ARMED);
        writeSecurityEvent("armed", method.name(), null);

        alarmNotifier.notifyModeChanged(SecurityMode.ARMED);
    }

    public synchronized void triggerAlarm(AlarmReason reason, String sourceComponent) {
        if (!stateStore.isArmed()) return;           // ALARM samo iz ARMED
        if (stateStore.isAlarm()) return;

        stateStore.setMode(SecurityMode.ALARM);
        writeSecurityEvent("alarm_on", reason.name(), sourceComponent);
        stateStore.clearDoorOpen(sourceComponent);

        // DB + BB obavezno
        actuator.send("smarthome/pi1_door_001/actuators/DB", "{\"command\":\"on\"}");
        actuator.send("smarthome/pi1_door_001/actuators/BB", "{\"command\":\"on\"}");

        actuator.send("smarthome/pi1_door_001/actuators/door_buzzer", "{\"command\":\"on\"}");
        actuator.send("smarthome/pi1_door_001/actuators/door_light", "{\"command\":\"on\"}");

        alarmNotifier.notifyAlarmOn(reason, sourceComponent);
    }

    public synchronized void deactivateAlarm(DisarmMethod method) {
        if (!stateStore.isAlarm()) return;

        stateStore.setMode(SecurityMode.ARMED);
        writeSecurityEvent("alarm_off", method.name(), null);

        actuator.send("smarthome/pi1_door_001/actuators/DB", "{\"command\":\"off\"}");
        actuator.send("smarthome/pi1_door_001/actuators/BB", "{\"command\":\"off\"}");
        actuator.send("smarthome/pi1_door_001/actuators/door_buzzer", "{\"command\":\"off\"}");
        actuator.send("smarthome/pi1_door_001/actuators/door_light", "{\"command\":\"off\"}");

        alarmNotifier.notifyAlarmOff(method);
    }

    public synchronized void disarm(DisarmMethod method) {
        if (stateStore.isAlarm()) {
            deactivateAlarm(method);
        }
        stateStore.setMode(SecurityMode.DISARMED);
        writeSecurityEvent("disarmed", method.name(), null);

        alarmNotifier.notifyModeChanged(SecurityMode.DISARMED);
    }

    private void writeSecurityEvent(String state, String detail, String component) {
        SensorEvent e = new SensorEvent();
        e.setSensor_type("security_event");
        e.setDevice_id("server");
        e.setComponent(component != null ? component : "SECURITY");
        e.setState(state);
        e.setValue(detail);
        e.setSimulated(true);
        e.setTimestamp(System.currentTimeMillis() / 1000.0);
        influxWriter.writeEvent(e);
    }
}
