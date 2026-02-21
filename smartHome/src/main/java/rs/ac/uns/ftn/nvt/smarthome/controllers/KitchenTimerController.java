package rs.ac.uns.ftn.nvt.smarthome.controllers;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import rs.ac.uns.ftn.nvt.smarthome.services.KitchenTimerService;
import rs.ac.uns.ftn.nvt.smarthome.state.SystemStateStore;

import java.util.Map;

@RestController
@RequestMapping("/api/kitchen/timer")
public class KitchenTimerController {

    private final KitchenTimerService timer;
    private final SystemStateStore store;

    public KitchenTimerController(KitchenTimerService timer, SystemStateStore store) {
        this.timer = timer;
        this.store = store;
    }

    @PostMapping("/time")
    public ResponseEntity<?> setTime(@RequestBody Map<String,Integer> body) {
        Integer s = body.get("seconds");
        timer.setTime(s != null ? s : 0);
        return ResponseEntity.ok(Map.of("success", true));
    }

    @PostMapping("/addN")
    public ResponseEntity<?> setAddN(@RequestBody Map<String,Integer> body) {
        Integer n = body.get("n");
        timer.setAddN(n != null ? n : 1);
        return ResponseEntity.ok(Map.of("success", true));
    }

    @GetMapping("/status")
    public ResponseEntity<?> status() {
        return ResponseEntity.ok(Map.of(
                "seconds", store.getKitchenTimerSeconds(),
                "addN", store.getKitchenAddSecondsN(),
                "blinking", store.isKitchenBlinking()
        ));
    }
}
