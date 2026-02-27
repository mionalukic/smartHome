package rs.ac.uns.ftn.nvt.smarthome.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import rs.ac.uns.ftn.nvt.smarthome.domain.DeviceStateDTO;
import rs.ac.uns.ftn.nvt.smarthome.services.InfluxQueryService;

import java.util.List;

@RestController
@RequestMapping("/api/state")
@CrossOrigin
public class DeviceStateController {

    @Autowired
    private InfluxQueryService influxQueryService;

    @GetMapping
    public List<DeviceStateDTO> getCurrentState() {
        return influxQueryService.getLatestStates();
    }
}