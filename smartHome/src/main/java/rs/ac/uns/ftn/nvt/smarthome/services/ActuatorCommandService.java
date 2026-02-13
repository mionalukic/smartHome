package rs.ac.uns.ftn.nvt.smarthome.services;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.integration.mqtt.support.MqttHeaders;
import org.springframework.integration.support.MessageBuilder;
import org.springframework.messaging.Message;
import org.springframework.messaging.MessageChannel;
import org.springframework.stereotype.Service;

@Service
public class ActuatorCommandService {

    @Autowired
    private MessageChannel mqttOutboundChannel;

    public void send(String topic, String payload) {

        Message<String> message = MessageBuilder
                .withPayload(payload)
                .setHeader(MqttHeaders.TOPIC, topic)
                .build();

        mqttOutboundChannel.send(message);
    }
}

