import json
import os

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(PACKAGE_DIR, 'config.json')


def create_config():
    print(CONFIG_FILE)
    with open(CONFIG_FILE, 'w+') as f:
        json.dump({
            "ASCII_CHARS": " .:=+*#%@",
            "MAP_PIXELS_RANGE_WIDTH": 30,
            "IMAGE_WIDTH": 500,
            "NEGATIVE": False
        }, f)


def read_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        create_config()
        return read_config()


def update_config(key, value):
    config = read_config()
    config[key] = value
    with open('config.json', 'w') as f:
        json.dump(config, f)


def get_config(key):
    config = read_config()
    return config.get(key)
