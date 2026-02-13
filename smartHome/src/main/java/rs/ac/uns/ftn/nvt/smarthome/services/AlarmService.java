package rs.ac.uns.ftn.nvt.smarthome.services;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;
import rs.ac.uns.ftn.nvt.smarthome.state.SystemStateStore;

@Service
public class AlarmService {

    @Autowired private SystemStateStore stateStore;
    @Autowired private InfluxWriter influxWriter;
    @Autowired private ActuatorCommandService actuatorCommandService;

    public void activate(String reason, String sourceComponent) {
        if (stateStore.isAlarmActive()) return;

        stateStore.setAlarmActive(true);
        System.out.println("ALARM ON: " + reason + " (" + sourceComponent + ")");

        // log event u Influx (poseban measurement)
        SensorEvent e = new SensorEvent();
        e.setSensor_type("alarm_event");
        e.setComponent(sourceComponent);
        e.setState("on");
        e.setDevice_id("server");
        e.setSimulated(true);
        e.setValue(1);
        e.setTimestamp(System.currentTimeMillis() / 1000.0);
        influxWriter.writeEvent(e);

        actuatorCommandService.send(
                "smarthome/pi1_door_001/actuators/door_buzzer",
                "{\"command\":\"on\"}"
        );

        actuatorCommandService.send(
                "smarthome/pi1_door_001/actuators/door_light",
                "{\"command\":\"on\"}"
        );

        // TODO kasnije: publish komande za DB/BB aktuator
    }

    public void deactivate(String reason) {
        if (!stateStore.isAlarmActive()) return;

        stateStore.setAlarmActive(false);
        System.out.println("ALARM OFF: " + reason);

        SensorEvent e = new SensorEvent();
        e.setSensor_type("alarm_event");
        e.setComponent("ALARM");
        e.setState("off");
        e.setDevice_id("server");
        e.setSimulated(true);
        e.setValue(0);
        e.setTimestamp(System.currentTimeMillis() / 1000.0);
        influxWriter.writeEvent(e);

        actuatorCommandService.send(
                "smarthome/pi1_door_001/actuators/door_buzzer",
                "{\"command\":\"off\"}"
        );

        actuatorCommandService.send(
                "smarthome/pi1_door_001/actuators/door_light",
                "{\"command\":\"off\"}"
        );

    }
}

