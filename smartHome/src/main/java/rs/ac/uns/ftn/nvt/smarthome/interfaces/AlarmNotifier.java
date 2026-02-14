package rs.ac.uns.ftn.nvt.smarthome.interfaces;

import rs.ac.uns.ftn.nvt.smarthome.state.AlarmReason;
import rs.ac.uns.ftn.nvt.smarthome.state.DisarmMethod;
import rs.ac.uns.ftn.nvt.smarthome.state.SecurityMode;

public interface AlarmNotifier {
    void notifyAlarmOn(AlarmReason reason, String source);
    void notifyAlarmOff(DisarmMethod method);
    void notifyModeChanged(SecurityMode mode);
}
