try:
    import orjson

    def read_json(filename :str):
        with open(filename, 'rb') as f:
            return orjson.loads(f.read())

    def save_json(filename :str, data :str):
        with open(filename, 'wb') as f:
            f.write(orjson.dumps(data))    
    
except ImportError:

    import json

    def read_json(filename :str):
        with open(filename, 'r') as f:
            return json.load(f)

    def save_json(filename :str, data :str):
        with open(filename, 'w') as f:
            json.dump(data, f)