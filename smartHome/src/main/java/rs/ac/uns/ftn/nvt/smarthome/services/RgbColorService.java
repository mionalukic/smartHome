package rs.ac.uns.ftn.nvt.smarthome.services;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class RgbColorService {
    @Autowired
    private ActuatorCommandService actuatorCommandService;

    public void changeColor(String color) {
        actuatorCommandService.send("smarthome/pi3_bedroom_001/actuators/rgb", "{\"value\":\"%s\"}".formatted(color));
    }
}
