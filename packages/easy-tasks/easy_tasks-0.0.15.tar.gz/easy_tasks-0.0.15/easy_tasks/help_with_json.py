import json


def dump_as_json(data, path):
    with open(path, "w") as f: json.dump(json.dumps(data), f)
    
def get_from_json(path):
    with open(path) as f: data = json.load(f)
    info = json.loads(data)
    return info