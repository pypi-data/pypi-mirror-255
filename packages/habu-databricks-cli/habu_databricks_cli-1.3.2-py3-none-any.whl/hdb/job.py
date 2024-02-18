import json
import logging

import requests

from hdb import util
from hdb.config import USER


def get_job_config(org_id: str, habu_sharing_id: str, orchestrator: str, cluster_id: str, user: str,
                   job_name: str, task_key: str, notebook: str, schedule_config: dict = None):
    job_config = {
        'name': job_name,
        'email_notifications': {
            "no_alert_for_skipped_runs": False
        },
        'webhook_notifications': {},
        'timeout_seconds': 0,
        'max_concurrent_runs': 1,
        'tasks': [
            {
                'task_key': task_key,
                'notebook_task': {
                    'notebook_path': "/Users/{}/habu_framework/{}".format(user, notebook),
                    'base_parameters': {
                        'org_id': org_id,
                        'habu_sharing_id': habu_sharing_id,
                        'orchestrator_name': orchestrator,
                        'org_id_sanitized': org_id.replace("-", "")
                    },
                    'source': 'WORKSPACE'
                },
                'existing_cluster_id': cluster_id,
                'timeout_seconds': 0,
                'email_notifications': {}
            }
        ],
        'format': 'MULTI_TASK'
    }

    if schedule_config is not None:
        job_config['schedule'] = schedule_config

    return job_config


def create_job(db_instance: str, job_config: dict, job_name: str, params: dict):
    logging.info(f'Creating job : {job_name}')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer {}'.format(params['token']),
    }
    response = requests.post('https://{}/api/2.1/jobs/create'.format(db_instance),
                             headers=headers, data=json.dumps(job_config))
    job = None
    if response.ok:
        job = response.json()
    else:
        util.log_response(response, f'Failed to create job : {job_name}')
    response.close()
    return job


def update_job(db_instance: str, job_config: dict, job_id: str, job_name: str, params: dict):
    logging.info(f'Updating job : {job_name}')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer {}'.format(params['token']),
    }
    update_config = {
        'job_id': job_id,
        'new_settings': job_config
    }
    response = requests.post('https://{}/api/2.1/jobs/update'.format(db_instance),
                             headers=headers, data=json.dumps(update_config))
    if not response.ok:
        util.log_response(response, f'Failed to update job: {job_name}')
    response.close()


def job_exists(jobs: dict, user: str, job_name: str):
    job_list = jobs.get('jobs')
    if job_list is not None:
        for job in job_list:
            if job['creator_user_name'] == user and job['settings']['name'] == job_name:
                return job['job_id']
    return None


def list_jobs(db_instance: str, params: dict):
    logging.info('fetching existing jobs')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer {}'.format(params['token']),
    }
    job_list = None
    response = requests.get('https://{}/api/2.1/jobs/list'.format(db_instance),
                            headers=headers)
    if response.ok:
        job_list = response.json()
    else:
        util.log_response(response, 'unable to fetch list of jobs!')
    response.close()
    return job_list


def setup_jobs(db_instance: str, org_id: str, habu_sharing_id: str, orchestrator_name: str,
               cluster_id: str, config_params: dict):
    user = config_params[USER]
    if len(cluster_id) <= 0:
        logging.error(f'Failed to create job, cluster is not setup cluster_id: {cluster_id}')
        return False

    cli_installer = 'cli-installer'
    cleanroom_request = 'cleanroom-request'

    cli_job_config = get_job_config(org_id, habu_sharing_id, orchestrator_name, cluster_id, user,
                                    cli_installer, cli_installer, 'installer/cli-installer.sql')

    cron_config = {
        'quartz_cron_expression': '0 * * * * ?',
        'timezone_id': 'America/Los_Angeles',
        'pause_status': 'PAUSED'
    }

    cr_request_config = get_job_config(org_id, habu_sharing_id, orchestrator_name, cluster_id, user,
                                       cleanroom_request, cleanroom_request, 'commands/cleanroom-request.sql',
                                       cron_config)

    job_list = list_jobs(db_instance, config_params)
    if job_list is not None:
        job_id = job_exists(job_list, user, cli_installer)
        if job_id is not None:
            update_job(db_instance, cli_job_config, job_id, cli_installer, config_params)
        else:
            create_job(db_instance, cli_job_config, cli_installer, config_params)

        job_id = job_exists(job_list, user, cleanroom_request)
        if job_id is not None:
            update_job(db_instance, cr_request_config, job_id, cleanroom_request, config_params)
        else:
            create_job(db_instance, cr_request_config, cleanroom_request, config_params)
    else:
        create_job(db_instance, cli_job_config, cli_installer, config_params)
        create_job(db_instance, cr_request_config, cleanroom_request, config_params)


def run_job(db_instance: str, job_id: str, params: dict, job_params: dict):
    logging.info(f'Running job {job_id}')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer {}'.format(params['token']),
    }
    job_config = {
        'job_id': job_id,
        'job_parameters': job_params
    }
    response = requests.post('https://{}/api/2.1/jobs/run-now'.format(db_instance),
                             headers=headers, data=json.dumps(job_config))
    if not response.ok:
        util.log_response(response, f'Failed to run job: {job_id}')
    response.close()


def run_job_by_name(db_instance: str, job_name: str, config_params: dict, job_params: dict):
    user = config_params[USER]
    job_list = list_jobs(db_instance, config_params)
    if job_list is not None:
        job_id = job_exists(job_list, user, job_name)
        if job_id is not None:
            run_job(db_instance, job_id, config_params, job_params)
        else:
            util.log_response(f'Job not found for {job_name}')
    else:
        util.log_response(f'No jobs found')


def get_cli_installer_job_config(org_id: str, habu_sharing_id: str, orchestrator: str, version: str):
    job_config = {
        'habu_sharing_id': habu_sharing_id,
        'orchestrator_name': orchestrator,
        'org_id_sanitized': org_id.replace("-", ""),
        'version_info': version
    }

    return job_config
