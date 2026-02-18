package rs.ac.uns.ftn.nvt.smarthome.rules;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;
import rs.ac.uns.ftn.nvt.smarthome.interfaces.SensorRule;
import rs.ac.uns.ftn.nvt.smarthome.services.SecurityStateService;
import rs.ac.uns.ftn.nvt.smarthome.state.AlarmReason;
import rs.ac.uns.ftn.nvt.smarthome.state.SystemStateStore;

@Component
public class GsgAlarmRule implements SensorRule {

    @Autowired
    private SecurityStateService security;

    @Autowired
    private SystemStateStore stateStore;

    @Override
    public void onEvent(SensorEvent e) {

        if (!"gyroscope".equals(e.getSensor_type())) return;
        if (!"GSG".equals(e.getComponent())) return;

        Boolean movement = e.getMovement();

        if (movement == null) return;

        if (movement) {
            System.out.println("Trigerovan gsg");
            security.triggerAlarm(
                    AlarmReason.MANUAL_TRIGGER,
                    "GSG"
            );
        }
    }
}
