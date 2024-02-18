import logging

import requests
import json

from hdb import util, config

CLUSTERS: str = 'clusters'
CLUSTER_ID: str = 'cluster_id'
CLUSTER_CONFIG: str = 'cluster_config'


def contains_cluster(cluster_id: str, cluster_list):
    logging.info(f'Checking if cluster {cluster_id} exists')
    if cluster_list is not None and cluster_id is not None:
        for cluster in cluster_list:
            if cluster[CLUSTER_ID] == cluster_id:
                return True
    return False


def list_cluster(db_instance: str, params: dict):
    headers = {
        'Authorization': 'Bearer {}'.format(params['token']),
    }
    logging.info('Fetching list of available clusters')
    response = requests.get('https://{}/api/2.0/clusters/list'.format(db_instance), headers=headers)
    cluster_list = None
    if response.ok:
        cluster_list = response.json()
        return cluster_list.get(CLUSTERS)
    else:
        util.log_response(response, 'unable to fetch list of clusters!')
    response.close()
    return cluster_list


def list_node_types(db_instance: str, params: dict):
    node_types = None
    headers = {
        'Authorization': 'Bearer {}'.format(params['token']),
    }
    response = requests.get(f'https://{db_instance}/api/2.0/clusters/list-node-types', headers=headers)
    if response.ok:
        node_types = response.json()
    else:
        util.log_response(response, 'unable to list node types!!')
    response.close()
    return node_types


def filter_node_types(node_types: dict):
    node_list = node_types.get('node_types')
    filtered_nodes = []
    for node in node_list or filtered_nodes:
        if not node['is_deprecated'] and \
                node['category'] == 'General Purpose' and \
                node['support_ebs_volumes'] and \
                node['support_cluster_tags'] and \
                node['is_io_cache_enabled'] and \
                node['photon_worker_capable'] and \
                node['photon_driver_capable'] and \
                not node['is_graviton']:
            filtered_nodes.append(node['node_type_id'])

    logging.debug(f'num node types : {len(node_list or filtered_nodes)}')
    logging.debug(f'num filtered : {len(filtered_nodes)}')
    if len(node_list) <= 0:
        logging.warning('Could not fetch list of supported nodes, '
                        'please make sure that the user or service principal has appropriate permissions!!')
    return filtered_nodes


def list_available_nodes(db_instance: str, params):
    return filter_node_types(list_node_types(db_instance, params))


def create_cluster(db_instance: str, cluster_config: dict, params):
    logging.info('Creating cluster')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer {}'.format(params['token']),
    }
    response = requests.post('https://{}/api/2.0/clusters/create'.format(db_instance), headers=headers,
                             data=json.dumps(cluster_config))
    cluster_id: str = ''
    if response.ok:
        cluster_id = response.json().get(CLUSTER_ID)
        logging.info(f'Cluster created, cluster_id: {cluster_id}')
    else:
        util.log_response(response, 'unable to create cluster!!')
    response.close()
    return cluster_id


def terminate_cluster(db_instance: str, cluster_id: str, params: dict):
    logging.info(f'Terminating(Stopping) cluster : {cluster_id}')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer {}'.format(params['token']),
    }
    data = {
        CLUSTER_ID: cluster_id
    }
    response = requests.post('https://{}/api/2.0/clusters/delete'.format(db_instance), headers=headers,
                             data=json.dumps(data))
    if not response.ok:
        util.log_response(response, 'Unable to terminate cluster!')
    response.close()


def validate_node_type(db_instance: str, node_type_id: str, params: dict):
    available_nodes = list_available_nodes(db_instance, params)
    if node_type_id in available_nodes:
        return True
    if len(available_nodes) > 0:
        logging.error(f'node type {node_type_id} not found!!')
        logging.info(f'Please choose from one of the following nodes : \n {available_nodes}')
    return False


def setup_cluster(db_instance: str, config_file: str, config_params: dict, node_type_id: str,
                  res_config: dict):
    cluster_id: str = ''
    auto_termination_mins = 10

    if config_params is not None:
        if node_type_id in config_params:
            cluster_id = config_params[node_type_id].get(CLUSTER_ID)
        if config.AUTO_TERMINATION_MINS in config_params:
            auto_termination_mins = config_params[config.AUTO_TERMINATION_MINS]

    if validate_node_type(db_instance, node_type_id, config_params):
        cluster_list = list_cluster(db_instance, config_params)
        if contains_cluster(cluster_id, cluster_list):
            return cluster_id
        else:
            logging.info('Required cluster not found')

            cluster_config = res_config[CLUSTER_CONFIG].copy()
            cluster_config[config.NODE_TYPE_ID] = node_type_id
            cluster_config[config.DRIVER_NODE_TYPE_ID] = node_type_id
            cluster_config[config.AUTO_TERMINATION_MINS] = auto_termination_mins

            cluster_id = create_cluster(db_instance, cluster_config, config_params)
            cluster_info = {CLUSTER_ID: cluster_id}
            config.update_config(config_file, node_type_id, cluster_info)
            terminate_cluster(db_instance, cluster_id, config_params)

    return cluster_id
