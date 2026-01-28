import paho.mqtt.client as mqtt
import json
import logging
import threading
import queue
import time
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MQTTPublisher:
    
    def __init__(self, broker: str, port: int, keepalive: int = 60, 
                 batch_size: int = 10, batch_interval: int = 5):
        self.broker = broker
        self.port = port
        self.keepalive = keepalive
        self.batch_size = batch_size
        self.batch_interval = batch_interval
        
        self.client = None
        self.connected = False
        self.running = False
        
        # Thread-safe queues per topic
        self.queues: Dict[str, queue.Queue] = {}
        self.lock = threading.Lock()
        
        self._setup_client()
    
    def _setup_client(self):
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
        else:
            self.connected = False
            logger.error(f"Failed to connect, code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnect, code: {rc}")
    
    def _on_publish(self, client, userdata, mid):
        logger.debug(f"Message {mid} published")
    
    def connect(self) -> bool:
        try:
            self.client.connect(self.broker, self.port, self.keepalive)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        self.running = False
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
    
    def register_topic(self, topic: str, max_queue_size: int = 100):
        if topic not in self.queues:
            self.queues[topic] = queue.Queue(maxsize=max_queue_size)
            logger.info(f"Registered topic: {topic}")
    
    def publish(self, topic: str, data: Dict[str, Any], use_batch: bool = True) -> bool:

        if not self.connected:
            logger.warning("Not connected, cannot publish")
            return False
        
        # Add timestamp
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        if use_batch:
            # Queue for batch publishing
            if topic not in self.queues:
                self.register_topic(topic)
            
            try:
                self.queues[topic].put_nowait(data)
                return True
            except queue.Full:
                logger.warning(f"Queue full for {topic}, dropping oldest")
                try:
                    self.queues[topic].get_nowait()
                    self.queues[topic].put_nowait(data)
                    return True
                except:
                    return False
        else:
            # Publish immediately
            return self._publish_now(topic, data)
    
    def _publish_now(self, topic: str, data: Dict[str, Any]) -> bool:
        try:
            payload = json.dumps(data)
            with self.lock:
                result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {topic}")
                return True
            else:
                logger.error(f"Publish failed: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Publish error: {e}")
            return False
    
    def start_batch_publisher(self):
        self.running = True
        self.batch_thread = threading.Thread(
            target=self._batch_publisher_loop,
            daemon=True,
            name="MQTTBatchPublisher"
        )
        self.batch_thread.start()
        logger.info("Batch publisher thread started")
    
    def _batch_publisher_loop(self):
        while self.running:
            for topic, q in self.queues.items():
                batch = []
                
                try:
                    while len(batch) < self.batch_size:
                        data = q.get_nowait()
                        batch.append(data)
                except queue.Empty:
                    pass
                
                if batch:
                    success = 0
                    for data in batch:
                        if self._publish_now(topic, data):
                            success += 1
                    
                    logger.info(f"Published {success}/{len(batch)} to {topic}")
            
            time.sleep(self.batch_interval)