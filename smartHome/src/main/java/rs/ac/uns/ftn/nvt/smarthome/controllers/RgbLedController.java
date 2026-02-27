package rs.ac.uns.ftn.nvt.smarthome.controllers;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import rs.ac.uns.ftn.nvt.smarthome.services.RgbColorService;

@RestController
@RequestMapping("/api/rgb")
public class RgbLedController {

    private final RgbColorService rgbColorService;
    public RgbLedController(RgbColorService rgbColorService) {
        this.rgbColorService = rgbColorService;
    }

    @PostMapping("/{color}")
    public ResponseEntity<?> changeColor(@PathVariable String color) {
        System.out.println("color: " + color);
        this.rgbColorService.changeColor(color);
        return ResponseEntity.ok("Color changed");
    }
}
