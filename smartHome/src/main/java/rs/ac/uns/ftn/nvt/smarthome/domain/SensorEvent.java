package rs.ac.uns.ftn.nvt.smarthome.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
@JsonIgnoreProperties(ignoreUnknown = true)
public class SensorEvent {

    private String device_id;
    private String sensor_type;
    private String component;
    private String state;
    private Object value;
    private Boolean simulated;
    private Double timestamp;
    private Double distance_cm;
    private String unit;

    private String key;

    private Double temperature;
    private Double humidity;

    private Double gyro_x;
    private Double gyro_y;
    private Double gyro_z;

    private Double pitch;
    private Double duration;

    public SensorEvent() {}

    @Override
    public String toString() {
        return "SensorEvent{" +
                "device_id='" + device_id + '\'' +
                ", sensor_type='" + sensor_type + '\'' +
                ", component='" + component + '\'' +
                ", state='" + state + '\'' +
                ", value=" + value +
                ", simulated=" + simulated +
                ", timestamp=" + timestamp +
                '}';
    }
}
