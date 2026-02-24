package rs.ac.uns.ftn.nvt.smarthome.controllers;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import rs.ac.uns.ftn.nvt.smarthome.services.PeopleCounterService;
import rs.ac.uns.ftn.nvt.smarthome.services.SecurityStateService;
import rs.ac.uns.ftn.nvt.smarthome.state.DisarmMethod;
import rs.ac.uns.ftn.nvt.smarthome.state.PinResult;
import rs.ac.uns.ftn.nvt.smarthome.state.SystemStateStore;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

@RestController
@RequestMapping("/api/people")
public class PeopleCounterController {

    private final PeopleCounterService peopleCounterService;

    public PeopleCounterController(PeopleCounterService peopleCounterService) {
        this.peopleCounterService = peopleCounterService;
    }

    @GetMapping("/{room}/exit-all")
    public ResponseEntity<?> exitAll(@PathVariable String room) {
        if (Objects.equals(room, "bedroom"))
            peopleCounterService.setBedroomCounter(0);
        else
            peopleCounterService.setKitchenCounter(0);

        return ResponseEntity.ok("Room emptied");
    }
}
