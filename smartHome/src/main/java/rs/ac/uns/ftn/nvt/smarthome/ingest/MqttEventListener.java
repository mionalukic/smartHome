package rs.ac.uns.ftn.nvt.smarthome.ingest;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.integration.annotation.ServiceActivator;
import org.springframework.stereotype.Service;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;
import rs.ac.uns.ftn.nvt.smarthome.rules.DoorAlarmRule;
import rs.ac.uns.ftn.nvt.smarthome.services.InfluxWriter;
import rs.ac.uns.ftn.nvt.smarthome.state.SystemStateStore;

@Service
public class MqttEventListener {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Autowired
    private InfluxWriter influxWriter;

    @Autowired
    private SystemStateStore stateStore;

    @Autowired
    private DoorAlarmRule doorAlarmRule;


    @ServiceActivator(inputChannel = "mqttInputChannel")
    public void handleMessage(String payload) {

        try {
            System.out.println("RAW PAYLOAD -> " + payload);

            SensorEvent event =
                    objectMapper.readValue(payload, SensorEvent.class);

            System.out.println("RECEIVED EVENT -> " + event);

            influxWriter.writeEvent(event);

            stateStore.updateEvent(event);

            doorAlarmRule.onEvent(event);


        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
