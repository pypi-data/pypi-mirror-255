import logging
import os
import pkg_resources
from tinynetrc import Netrc

from ruamel.yaml.main import \
    round_trip_load as yaml_load, \
    round_trip_dump as yaml_dump

DATABRICKS_IID: str = 'databricks_instance_id'
USER: str = 'user'
NODE_TYPE_LIST: str = 'node_type_list'
NODE_TYPE_ID: str = 'node_type_id'
DRIVER_NODE_TYPE_ID: str = 'driver_node_type_id'
AUTO_TERMINATION_MINS: str = 'autotermination_minutes'
TOKEN: str = 'token'
CLI_INSTALLER: str = 'cli-installer'

def open_netrc():
    # create netrc if it doesn't exist
    file = os.path.join(os.path.expanduser('~'), '.netrc')
    if not os.path.exists(file):
        open(file, 'w').close()
    netrc = Netrc()
    return netrc


def create_config(conf_file_name: str, databricks_instance: str, login: str, token: str, auto_termination_mins: int):
    # Add a new entry

    config = None
    habu_config = {
        DATABRICKS_IID: databricks_instance,
        AUTO_TERMINATION_MINS: auto_termination_mins,
        TOKEN: token,
        USER: login,
    }
    try:
        with open(conf_file_name, 'w') as hdb_config:
            try:
                hdb_config.write(yaml_dump(habu_config, indent=4))
                hdb_config.close()
                config = habu_config
            except (IOError, OSError):
                logging.error('Failed to create config!', exc_info=True)
    except (FileNotFoundError, PermissionError, OSError):
        logging.error('Failed to open conf file for writing!', exc_info=True)
    return config


def validate_critical_params(config_params: dict):
    params = [USER, DATABRICKS_IID, AUTO_TERMINATION_MINS, TOKEN]
    for param in params:
        if config_params.get(param) is None:
            raise ValueError(f'Param {param} missing in config file, please run the config command to create config!!')


def read_config(config_file, validate=True):
    config_params = None
    try:
        with open(config_file, 'r') as db_config:
            try:
                config_params = yaml_load(db_config, preserve_quotes=True)
                db_config.close()
                if validate:
                    validate_critical_params(config_params)
            except (IOError, OSError):
                logging.error('Failed to read config', exc_info=True)
    except (FileNotFoundError, PermissionError, OSError):
        logging.error('Failed to read config!', exc_info=True)
    return config_params


def read_resource_config(config_file):
    config_params = None
    with open(pkg_resources.resource_filename(__package__, config_file), 'r') as db_config:
        try:
            config_params = yaml_load(db_config.read(), preserve_quotes=True)
            db_config.close()
        except (IOError, OSError):
            logging.critical('Failed to read resource config!', exc_info=True)
    return config_params


def update_config(config_file, key: str, value):
    config_params: dict = read_config(config_file, validate=False)
    if len(key) > 0:
        config_params[key] = value
        try:
            with open(config_file, "w") as hdb_config:
                try:
                    hdb_config.write(yaml_dump(config_params, indent=4))
                    hdb_config.close()
                    return True
                except (IOError, OSError):
                    logging.error('Failed to update config!', exc_info=True)
        except (FileNotFoundError, PermissionError, OSError):
            logging.error('Failed to update config!', exc_info=True)
    return False
