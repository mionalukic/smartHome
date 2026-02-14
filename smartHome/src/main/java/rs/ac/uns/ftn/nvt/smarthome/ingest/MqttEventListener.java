package rs.ac.uns.ftn.nvt.smarthome.ingest;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.integration.annotation.ServiceActivator;
import org.springframework.stereotype.Service;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;
import rs.ac.uns.ftn.nvt.smarthome.interfaces.SensorRule;
import rs.ac.uns.ftn.nvt.smarthome.rules.DoorAlarmRule;
import rs.ac.uns.ftn.nvt.smarthome.services.InfluxWriter;
import rs.ac.uns.ftn.nvt.smarthome.state.SystemStateStore;

import java.util.List;

@Service
public class MqttEventListener {

    private final ObjectMapper objectMapper = new ObjectMapper();


    private final InfluxWriter influxWriter;
    private final SystemStateStore stateStore;
    private final List<SensorRule> rules;

    @Autowired
    public MqttEventListener(
            InfluxWriter influxWriter,
            SystemStateStore stateStore,
            List<SensorRule> rules) {

        this.influxWriter = influxWriter;
        this.stateStore = stateStore;
        this.rules = rules;
    }


    @ServiceActivator(inputChannel = "mqttInputChannel")
    public void handleMessage(String payload) {

        try {

            System.out.println("RAW PAYLOAD -> " + payload);
            SensorEvent event =
                    objectMapper.readValue(payload, SensorEvent.class);
            System.out.println("RECEIVED EVENT -> " + event);
            // 1. raw log
            influxWriter.writeEvent(event);

            // 2. update last known state
            stateStore.updateEvent(event);

            // 3. dispatch rules
            for (SensorRule rule : rules) {
                rule.onEvent(event);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
