package rs.ac.uns.ftn.nvt.smarthome.services;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import rs.ac.uns.ftn.nvt.smarthome.state.PinResult;

@Service
public class PinService {

    @Value("${security.pin}")
    private String correctPin;

    @Value("${security.pin.length:4}")
    private int pinLength;

    @Value("${security.pin.timeoutMs:8000}")
    private long timeoutMs;

    @Value("${security.pin.maxAttempts}")
    private int maxAttempts;

    private int failedAttempts = 0;

    private final StringBuilder buffer = new StringBuilder();
    private long lastKeyTime = 0;

    public synchronized PinResult pushKey(String key) {

        long now = System.currentTimeMillis();

        if (now - lastKeyTime > timeoutMs) {
            buffer.setLength(0);
        }
        lastKeyTime = now;

        if (key == null || key.isBlank()) return PinResult.IGNORED;

        if ("*".equals(key)) {
            buffer.setLength(0);
            return PinResult.CLEARED;
        }

        buffer.append(key);

        if (buffer.length() < pinLength) return PinResult.IN_PROGRESS;

        String entered = buffer.substring(0, pinLength);
        buffer.setLength(0);

        if (entered.equals(correctPin)) {
            failedAttempts = 0;
            return PinResult.OK;
        } else {
            failedAttempts++;
            System.out.println(failedAttempts);
            if (failedAttempts >= maxAttempts) {
                failedAttempts = 0;
                return PinResult.LOCKED;
            }
            return PinResult.INVALID;
        }

    }
}

