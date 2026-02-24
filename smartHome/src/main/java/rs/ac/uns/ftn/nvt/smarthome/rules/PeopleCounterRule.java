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
    @Autowired
    private SystemStateStore systemStateStore;
    @Autowired
    private SecurityStateService securityStateService;

    @Override
    public void onEvent(SensorEvent e) {

        if (!e.getComponent().startsWith("DPIR")) return;

        Boolean isEntering = e.getIs_entering();
        if (isEntering == null) return;
        if (isEntering) {
            System.out.println("Person entered the room");
            int personCounter = service.enter(e.getDevice_id());
            if (personCounter == -1) return;
            if(personCounter == 1) securityStateService.triggerAlarm(AlarmReason.UNEXPECTED_ENTRANCE, e.getComponent());
        } else {
            int currentState = e.getComponent().equals("DPIR1") ? service.getBedroomCounter() : service.getKitchenCounter();
            if (currentState == 0) {
                System.out.println("ERROR - Ghost exited the room");
                return;
            }
            service.exit(e.getDevice_id());
            System.out.println("Person exited the room");
        }
        System.out.println("PEOPLE COUNTER: " + service.getBedroomCounter());
    }
}
