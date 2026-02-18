package rs.ac.uns.ftn.nvt.smarthome.rules;

import org.springframework.stereotype.Component;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;
import rs.ac.uns.ftn.nvt.smarthome.interfaces.SensorRule;
import rs.ac.uns.ftn.nvt.smarthome.services.PinService;
import rs.ac.uns.ftn.nvt.smarthome.services.SecurityStateService;
import rs.ac.uns.ftn.nvt.smarthome.state.AlarmReason;
import rs.ac.uns.ftn.nvt.smarthome.state.DisarmMethod;
import rs.ac.uns.ftn.nvt.smarthome.state.PinResult;

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

        PinResult r = pinService.pushKey(e.getKey());


        if (r ==PinResult.OK) {

            if (security.isDisarmed()) {
                security.armWithDelay(DisarmMethod.PIN_PAD);
            } else {
                security.disarm(DisarmMethod.PIN_PAD);
            }

        } else if (r == PinResult.LOCKED) {

            security.triggerAlarm(
                    AlarmReason.MANUAL_TRIGGER,
                    "PIN_PAD"
            );
        }

    }
}

