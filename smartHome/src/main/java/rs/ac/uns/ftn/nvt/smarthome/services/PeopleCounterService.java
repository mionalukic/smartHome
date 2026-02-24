package rs.ac.uns.ftn.nvt.smarthome.services;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.Setter;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Getter
@Setter
public class PeopleCounterService {
    private int bedroomCounter = 0;
    private int kitchenCounter = 0;

    public int enter(String deviceId) {
        if (deviceId.startsWith("pi1")){
            bedroomCounter++;
            return bedroomCounter;
        }
        else if (deviceId.startsWith("pi2")) {
            kitchenCounter++;
            return kitchenCounter;
        }
        return -1;
    }

    public void exit(String deviceId){
        if (deviceId.startsWith("pi1"))
            bedroomCounter--;
        else if (deviceId.startsWith("pi2")) {
            kitchenCounter--;
        }
    }
}
