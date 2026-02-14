package rs.ac.uns.ftn.nvt.smarthome.interfaces;

import rs.ac.uns.ftn.nvt.smarthome.domain.SensorEvent;

public interface SensorRule {
    void onEvent(SensorEvent event);
}
