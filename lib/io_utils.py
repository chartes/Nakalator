import yaml


def load_yaml(file):
    return yaml.load(open(file, "r"), Loader=yaml.FullLoader)


def create_file_cur(image):
    file_open = open(image, "rb")
    return {"file": file_open}