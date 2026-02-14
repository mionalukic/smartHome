package rs.ac.uns.ftn.nvt.smarthome.services;

import org.springframework.stereotype.Service;
import rs.ac.uns.ftn.nvt.smarthome.interfaces.AlarmNotifier;
import rs.ac.uns.ftn.nvt.smarthome.state.AlarmReason;
import rs.ac.uns.ftn.nvt.smarthome.state.DisarmMethod;
import rs.ac.uns.ftn.nvt.smarthome.state.SecurityMode;

@Service
public class LogAlarmNotifier implements AlarmNotifier {
    public void notifyAlarmOn(AlarmReason reason, String source) {
        System.out.println("Notify WEB: ALARM ON " + reason + " " + source);
    }

    public void notifyAlarmOff(DisarmMethod method) {
        System.out.println("Notify WEB: ALARM OFF " + method);
    }

    public void notifyModeChanged(SecurityMode mode) {
        System.out.println("Notify WEB: MODE " + mode);
    }
}