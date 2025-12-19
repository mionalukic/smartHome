import json

def load_settings(filePath='settings.json'):
    with open(filePath, 'r') as f:
        data = json.load(f)
        for name, obj in data.items():
            data[name] = obj
    return data