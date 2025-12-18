import json

def load_settings(filePath='settings.json'):
    with open(filePath, 'r') as f:
        data = json.load(f)
        print(data)
        for name, obj in data.items():
            data[name] = obj
            print(name, obj)
    return data