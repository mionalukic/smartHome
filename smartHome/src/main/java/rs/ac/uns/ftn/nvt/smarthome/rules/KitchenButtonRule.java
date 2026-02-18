package rs.ac.uns.ftn.nvt.smarthome.rules;

import org.springframework.stereotype.Component;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;
import rs.ac.uns.ftn.nvt.smarthome.interfaces.SensorRule;
import rs.ac.uns.ftn.nvt.smarthome.services.KitchenTimerService;

@Component
public class KitchenButtonRule implements SensorRule {

    private final KitchenTimerService timer;

    public KitchenButtonRule(KitchenTimerService timer) {
        this.timer = timer;
    }

    @Override
    public void onEvent(SensorEvent e) {
        if (!"kitchen_button".equals(e.getSensor_type())) return;
        if (!"BTN".equals(e.getComponent())) return;

        timer.onButtonPressed();
    }
}
