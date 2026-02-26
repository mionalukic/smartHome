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

    @PostMapping("/exit-all")
    public ResponseEntity<?> exitAll() {
        peopleCounterService.reset();
        return ResponseEntity.ok("Room emptied");
    }
}
