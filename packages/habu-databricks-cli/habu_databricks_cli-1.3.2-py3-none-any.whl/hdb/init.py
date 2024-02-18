import json
import logging
import os

import pkg_resources
import requests

from hdb import util
from hdb.config import USER


def walk_resource_paths(root_dir):
    file_paths = []
    for name in pkg_resources.resource_listdir(__package__, root_dir):
        logging.info(f'Found resource {os.path.basename(name)}')
        path = root_dir + f'/{os.path.basename(name)}'
        if pkg_resources.resource_isdir(__package__, path):
            file_paths = file_paths + walk_resource_paths(path)
        else:
            file_paths.append(path)
    return file_paths


def list_dir(db_instance: str, dir_path: str, params):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer {}'.format(params['token'])
    }
    data = {
        'path': dir_path
    }
    dir_list = None
    response = requests.get('https://{}/api/2.0/workspace/list'.format(db_instance), headers=headers,
                            data=json.dumps(data))
    if response.ok:
        dir_list = response.json()
    else:
        util.log_response(response, 'Workspace path does not exist!', warn=True)
    response.close()
    return dir_list


def create_dir(db_instance, dir_path, params: dict):
    # habu_framework/commands/
    # habu_framework/installer/
    logging.info(f'Creating workspace dir : {dir_path}')
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(params['token']),
    }
    data = {
        'path': dir_path
    }
    response = requests.post('https://{}/api/2.0/workspace/mkdirs'.format(db_instance), headers=headers,
                             data=json.dumps(data))
    if not response.ok:
        util.log_response(response, 'unable to create directory!')
    response.close()


def upload_notebook(db_instance, file_path, dir_path, params):
    headers = {
        'Authorization': 'Bearer {}'.format(params['token'])
    }
    logging.info(f'Setting up {file_path}')
    with open(pkg_resources.resource_filename(__package__, file_path), 'rb') as nb:
        try:
            files = {
                'path': (None, dir_path + f'/{os.path.basename(file_path)}'),
                'language': (None, 'SQL'),
                'overwrite': (None, 'true'),
                'content': nb,
            }
            response = requests.post('https://{}/api/2.0/workspace/import'.format(db_instance), files=files,
                                     headers=headers)
            if not response.ok:
                util.log_response(response, 'Unable to upload file')
            response.close()
            nb.close()
        except (requests.RequestException, ConnectionError):
            logging.error(f'Failed to setup {file_path}', exc_info=True)


def setup_workspace(db_instance, config_params: dict):
    base_dir = '/Users/{}/habu_framework'.format(config_params[USER])

    commands_dir_path = '{}/commands'.format(base_dir)
    installer_dir_path = '{}/installer'.format(base_dir)

    dir_list = list_dir(db_instance, commands_dir_path, config_params)
    if dir_list is None:
        create_dir(db_instance, commands_dir_path, config_params)

    dir_list = list_dir(db_instance, installer_dir_path, config_params)
    if dir_list is None:
        create_dir(db_instance, installer_dir_path, config_params)

    file_path_list = walk_resource_paths('cli_installer')
    for file_path in file_path_list:
        upload_notebook(db_instance, file_path, installer_dir_path, config_params)

    file_path_list = walk_resource_paths('commands')
    for file_path in file_path_list:
        upload_notebook(db_instance, file_path, commands_dir_path, config_params)
