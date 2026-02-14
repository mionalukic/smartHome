package rs.ac.uns.ftn.nvt.smarthome.controllers;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import rs.ac.uns.ftn.nvt.smarthome.services.SecurityStateService;
import rs.ac.uns.ftn.nvt.smarthome.state.DisarmMethod;
import rs.ac.uns.ftn.nvt.smarthome.state.SecurityMode;
import rs.ac.uns.ftn.nvt.smarthome.state.SystemStateStore;

@RestController
@RequestMapping("/api/security")
public class SecurityController {

    private final SecurityStateService security;
    private final SystemStateStore stateStore;

    public SecurityController(SecurityStateService security,
                              SystemStateStore stateStore) {
        this.security = security;
        this.stateStore = stateStore;
    }

    @PostMapping("/arm")
    public ResponseEntity<?> arm() {
        security.arm(DisarmMethod.WEB);
        return ResponseEntity.ok("System armed");
    }

    @PostMapping("/disarm")
    public ResponseEntity<?> disarm() {
        security.disarm(DisarmMethod.WEB);
        return ResponseEntity.ok("System disarmed");
    }

    @PostMapping("/alarm/off")
    public ResponseEntity<?> deactivateAlarm() {
        security.deactivateAlarm(DisarmMethod.WEB);
        return ResponseEntity.ok("Alarm deactivated");
    }

    @GetMapping("/status")
    public ResponseEntity<SecurityMode> status() {
        return ResponseEntity.ok(stateStore.getMode());
    }
}
