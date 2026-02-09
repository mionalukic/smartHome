"""MQTT Configuration"""
import json
from typing import Dict, Any

class MQTTConfig:
    
    def __init__(self, settings_file: str = "settings.json"):
        with open(settings_file, 'r') as f:
            self.settings = json.load(f)
    
    @property
    def broker(self) -> str:
        return self.settings.get('mqtt', {}).get('broker', '192.168.107.197')
    
    @property
    def port(self) -> int:
        return self.settings.get('mqtt', {}).get('port', 1883)
    
    @property
    def keepalive(self) -> int:
        return self.settings.get('mqtt', {}).get('keepalive', 60)
    
    @property
    def topics(self) -> Dict[str, str]:
        return self.settings.get('mqtt', {}).get('topics', {})
    
    @property
    def batch_size(self) -> int:
        return self.settings.get('batch', {}).get('size', 10)
    
    @property
    def batch_interval(self) -> int:
        return self.settings.get('batch', {}).get('interval_seconds', 5)
    
    @property
    def device_id(self) -> str:
        return self.settings.get('device', {}).get('device_id', 'unknown')
    
    def get_sensor_topic(self, sensor_name: str) -> str:
        return self.settings.get('sensors', {}).get(sensor_name, {}).get('topic', f'sensors/{sensor_name}')