# Function to update the credentials file
import configparser
import os

configuration_path = os.path.join(os.path.expanduser('~'), '.qprom', 'configuration.ini')


def update_configuration(setting: str, value: str):
    # Ensure the directory exists, if not create it
    os.makedirs(os.path.dirname(configuration_path), exist_ok=True)

    config = configparser.ConfigParser()
    config.read(configuration_path)

    if 'default' not in config.sections():
        config.add_section('default')
    config.set('default', setting, value)
    with open(configuration_path, 'w') as configfile:
        config.write(configfile)


def get_configuration(setting: str) -> str:
    # Create a config parser
    config = configparser.ConfigParser()

    config.read(configuration_path)

    if config.has_option('default', setting):
        return config.get('default', setting)
    else:
        return ""

