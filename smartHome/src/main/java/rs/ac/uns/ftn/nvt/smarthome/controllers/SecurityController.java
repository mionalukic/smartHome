package rs.ac.uns.ftn.nvt.smarthome.controllers;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import rs.ac.uns.ftn.nvt.smarthome.services.SecurityStateService;
import rs.ac.uns.ftn.nvt.smarthome.state.DisarmMethod;
import rs.ac.uns.ftn.nvt.smarthome.state.PinResult;
import rs.ac.uns.ftn.nvt.smarthome.state.SecurityMode;
import rs.ac.uns.ftn.nvt.smarthome.state.SystemStateStore;

import java.util.HashMap;
import java.util.Map;

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
    public ResponseEntity<?> status() {

        Map<String, Object> response = new HashMap<>();

        response.put("mode", stateStore.getMode());
        response.put("reason", stateStore.getLastAlarmReason());
        response.put("source", stateStore.getLastAlarmSource());

        return ResponseEntity.ok(response);
    }

    @PostMapping("/pin")
    public ResponseEntity<?> enterPin(@RequestBody Map<String,String> body) {

        String key = body.get("key");

        PinResult result = security.processPinForModeChange(key);

        Map<String, Object> response = new HashMap<>();
        response.put("result", result.name());
        response.put("mode", stateStore.getMode());
        response.put("reason", stateStore.getLastAlarmReason());
        response.put("source", stateStore.getLastAlarmSource());

        return ResponseEntity.ok(response);
    }
}
