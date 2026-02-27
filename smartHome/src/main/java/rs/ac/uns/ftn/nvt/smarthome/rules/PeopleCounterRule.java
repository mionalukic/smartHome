package rs.ac.uns.ftn.nvt.smarthome.rules;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;
import rs.ac.uns.ftn.nvt.smarthome.interfaces.SensorRule;
import rs.ac.uns.ftn.nvt.smarthome.services.PeopleCounterService;
import rs.ac.uns.ftn.nvt.smarthome.services.SecurityStateService;
import rs.ac.uns.ftn.nvt.smarthome.state.AlarmReason;
import rs.ac.uns.ftn.nvt.smarthome.state.SystemStateStore;

@Component
public class PeopleCounterRule implements SensorRule {

    @Autowired
    private PeopleCounterService service;

    @Override
    public void onEvent(SensorEvent e) {

        if (!e.getComponent().startsWith("DPIR")) return;
        if (e.getComponent().equals("DPIR3")) {
            service.detectMovement();
            return;
        }
        Boolean isEntering = e.getIs_entering();
        if (isEntering == null) return;
        if (isEntering) {
            System.out.println("Person entered the room");
            service.enter(e.getComponent());
        } else {
            service.exit();
        }
    }
}
