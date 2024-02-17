import yaml
from yaml.loader import SafeLoader

# Open the file and load the file

def read_config(config_file):
    with open(config_file) as f:
    config = yaml.load(f, Loader=SafeLoader)
    return config

