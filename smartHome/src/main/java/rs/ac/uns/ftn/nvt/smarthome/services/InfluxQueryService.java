package rs.ac.uns.ftn.nvt.smarthome.services;

import com.influxdb.client.InfluxDBClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import rs.ac.uns.ftn.nvt.smarthome.domain.DeviceStateDTO;

import java.util.ArrayList;
import java.util.List;

@Service
public class InfluxQueryService {

    @Autowired
    private InfluxDBClient influxDBClient;

    @Value("${influx.bucket}")
    private String bucket;

    public List<DeviceStateDTO> getLatestStates() {

        String flux = """
            import "influxdata/influxdb/schema"

            schema.measurements(bucket: "%s")
        """.formatted(bucket);

        List<String> measurements =
                influxDBClient.getQueryApi()
                        .query(flux)
                        .stream()
                        .flatMap(table -> table.getRecords().stream())
                        .map(r -> r.getValue().toString())
                        .toList();

        List<DeviceStateDTO> result = new ArrayList<>();

        for (String m : measurements) {

            String query = """
                from(bucket: "%s")
                  |> range(start: -10m)
                  |> filter(fn: (r) => r["_measurement"] == "%s")
                  |> last()
            """.formatted(bucket, m);

            var tables = influxDBClient.getQueryApi().query(query);

            tables.forEach(table ->
                    table.getRecords().forEach(record -> {
                        DeviceStateDTO dto = new DeviceStateDTO();
                        dto.setMeasurement(m);
                        dto.setDeviceId((String) record.getValueByKey("device_id"));
                        dto.setField(record.getField());
                        dto.setValue(record.getValue());
                        result.add(dto);
                    })
            );
        }

        return result;
    }
}