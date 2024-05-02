import yaml

def load_yaml(file):
    return yaml.load(open(file, "r"), Loader=yaml.FullLoader)


