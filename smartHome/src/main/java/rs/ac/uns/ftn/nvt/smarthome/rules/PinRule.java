package rs.ac.uns.ftn.nvt.smarthome.rules;

import org.springframework.stereotype.Component;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;
import rs.ac.uns.ftn.nvt.smarthome.interfaces.SensorRule;
import rs.ac.uns.ftn.nvt.smarthome.services.PinService;
import rs.ac.uns.ftn.nvt.smarthome.services.SecurityStateService;
import rs.ac.uns.ftn.nvt.smarthome.state.DisarmMethod;

@Component
public class PinRule implements SensorRule {

    private final PinService pinService;
    private final SecurityStateService security;

    public PinRule(PinService pinService, SecurityStateService security) {
        this.pinService = pinService;
        this.security = security;
    }

    public void onEvent(SensorEvent e) {

        if (!"door_membrane_switch".equals(e.getSensor_type())) return;
        if (e.getKey() == null) return;

        System.out.println("PIN RULE TRIGGERED: " + e.getKey());

        PinService.PinResult r = pinService.pushKey(e.getKey());

        if (r == PinService.PinResult.OK) {
            security.deactivateAlarm(DisarmMethod.PIN_PAD);
        }
    }
}

