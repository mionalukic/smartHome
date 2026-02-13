package rs.ac.uns.ftn.nvt.smarthome.services;

import com.influxdb.client.InfluxDBClient;
import com.influxdb.client.WriteApiBlocking;
import com.influxdb.client.domain.WritePrecision;
import com.influxdb.client.write.Point;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;

import java.time.Instant;

@Service
public class InfluxWriter {

    @Autowired
    private InfluxDBClient influxDBClient;

    @Value("${influx.bucket}")
    private String bucket;

    @Value("${influx.org}")
    private String org;

    public void writeEvent(SensorEvent event) {

        WriteApiBlocking writeApi = influxDBClient.getWriteApiBlocking();

        String measurement = event.getSensor_type() != null
                ? event.getSensor_type()
                : "unknown";

        Point point = Point
                .measurement(measurement)
                .addTag("device_id", safe(event.getDevice_id()))
                .addTag("component", safe(event.getComponent()))
                .addTag("simulated", String.valueOf(event.getSimulated()))
                .time(Instant.now(), WritePrecision.NS);

        switch (measurement) {

            case "door_sensor":
            case "door_motion_sensor":
            case "door_light":
            case "kitchen_button":
            case "seven_segment":

                if (event.getValue() instanceof Number) {
                    point.addField("value",
                            ((Number) event.getValue()).doubleValue());
                }
                break;

            case "ultrasonic_sensor":

                if (event.getDistance_cm() != null) {
                    point.addField("distance",
                            event.getDistance_cm());
                }
                break;

            case "door_membrane_switch":

                if (event.getKey() != null) {
                    point.addField("key",
                            event.getKey());
                }
                break;

            case "kitchen_dht":

                if (event.getTemperature() != null) {
                    point.addField("temperature",
                            event.getTemperature());
                }

                if (event.getHumidity() != null) {
                    point.addField("humidity",
                            event.getHumidity());
                }
                break;

            case "gyroscope":

                if (event.getGyro_x() != null)
                    point.addField("gyro_x", event.getGyro_x());

                if (event.getGyro_y() != null)
                    point.addField("gyro_y", event.getGyro_y());

                if (event.getGyro_z() != null)
                    point.addField("gyro_z", event.getGyro_z());

                break;

            case "door_buzzer":

                int active =
                        (event.getPitch() != null ||
                                event.getDuration() != null) ? 1 : 0;

                point.addField("value", active);
                break;

            default:

                if (event.getValue() instanceof Number) {
                    point.addField("value",
                            ((Number) event.getValue()).doubleValue());
                }
        }

        writeApi.writePoint(bucket, org, point);

        System.out.println("Written structured event: " + event);
    }

    private String safe(String value) {
        return value != null ? value : "unknown";
    }

}

