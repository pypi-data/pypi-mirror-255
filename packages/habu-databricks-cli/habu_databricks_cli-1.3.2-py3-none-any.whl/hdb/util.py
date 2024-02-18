import logging

import pkg_resources


def log_response(response, message='API Error : ', warn: bool = False):
    if warn:
        logging.warning(f'\n{message}')
    else:
        logging.error(f'\n{message}')
    logging.debug('Request Info:')
    logging.debug(response.request.headers)
    logging.debug(response.request.body)
    logging.debug('Response Info:')
    logging.info(f'status code : {response.status_code}')
    logging.info(f'reason : {response.reason}')
    if response.status_code == 403:
        logging.info('Unauthorized!, please rerun the config command, or contact admin!')
    logging.debug(f'response content : {response.content}')
    logging.info(f'response : {response.json()}')


def pkg_version():
    version = pkg_resources.require("habu-databricks-cli")[0].version
    print("habu-databricks-cli version: " + version)
