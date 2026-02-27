package rs.ac.uns.ftn.nvt.smarthome.domain;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class DeviceStateDTO {

    private String measurement;
    private String deviceId;
    private String field;
    private Object value;
}
