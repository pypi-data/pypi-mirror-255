import logging

import click
import pkg_resources

from hdb import config as hdb_config, util
from hdb import init as init_setup, job, cluster
from hdb.config import DATABRICKS_IID, CLI_INSTALLER

RES_CONFIG: dict = hdb_config.read_resource_config('resource/config.yaml')


@click.group()
def cli():
    pass


@cli.command(help='Display version of the cli')
def version():
    util.pkg_version()


def setup_log(log_level):
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s : %(message)s', level=log_level)


def validate_mins(ctx, param, value):
    try:
        mins = int(value)
        if 10 <= mins <= 10000 or mins == 0:
            return mins
        else:
            raise click.BadParameter('The value must be either 0 (to explicitly disable automatic termination.) '
                                     'or between 10 and 10000 minutes')
    except ValueError:
        raise click.BadParameter('Only numeric integer is an acceptable parameter')


@cli.command()
@click.option('--config-file', '-c', default='habu_databricks_config.yaml',
              help='File name where config will get saved (default is habu_databricks_config.yaml in current directory)')
@click.option('--databricks-instance', '-i', prompt='Databricks instance id',
              help=' Databricks instance id (<instance-id>.cloud.databricks.com)')
@click.option('--login', '-u', prompt="Databricks user name",
              help='Databricks user name (me@example.com)')
@click.password_option('--token', '-t', prompt='Token', confirmation_prompt=False,
                       help='Enter the token generated from Databricks user settings')
@click.option('--log-level', '-l', type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                                                     case_sensitive=False), default='INFO',
              help='Select log level while running the commands, default level is set to INFO')
@click.option('--auto-termination-mins', '-m', default=10, type=click.UNPROCESSED, callback=validate_mins,
              help='Automatically terminate the cluster after it is inactive for this time in minutes.'
                   ' If not set, the cluster will not be automatically terminated.'
                   'The threshold must be between 10 and 10000 minutes. You can also set this value to 0 '
                   'to explicitly disable automatic termination.')
def config(config_file: str, databricks_instance: str, login: str, token: str, log_level: str,
           auto_termination_mins: int):
    """
    Command to generate the config for the habu databricks agent.
    The config is required to set up the habu databricks framework
    """
    setup_log(getattr(logging, log_level.upper()))
    config_params = hdb_config.create_config(config_file, databricks_instance, login, token, auto_termination_mins)
    if config_params is not None:
        logging.info('Config file created successfully')


@cli.command()
@click.option('--config-file', '-c', default='habu_databricks_config.yaml',
              help='File name from where config gets read (default is habu_databricks_config.yaml in current directory)')
@click.option('--log-level', '-l', type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                                                     case_sensitive=False), default='INFO',
              help='Select log level while running the commands, default level is set to INFO')
def list_nodes(config_file: str, log_level: str):
    """Command to list available node types to create cluster.
    The results are the valid values that can be passed as node-type in init command"""
    setup_log(getattr(logging, log_level.upper()))
    config_params = hdb_config.read_config(config_file)

    if config_params is not None:
        db_instance = config_params[DATABRICKS_IID]
        # token.setup_token(db_instance, config_file, config_params, RES_CONFIG)
        nodes = cluster.list_available_nodes(db_instance, config_params)
        for node in nodes:
            print(node)
    else:
        logging.error(f'Failed to read config from {config_file}, use config cmd to generate config')


@cli.command()
@click.option('--org-id', '-o', prompt="Organization id", help='Habu Org Id')
@click.option('--habu-sharing-id', '-s', prompt="Habu Sharing Id", help='Habu Sharing Id (aws:<region>:<id>)',
              default='aws:us-west-2:23eb138f-f773-4922-9805-53c286bbd24d')
@click.option('--orchestrator', '-oc', prompt="Orchestrator Name", help='Orchestrator name',
              default='habudbprodorchestrator_metastore')
@click.option('--config-file', '-c', default="./habu_databricks_config.yaml",
              help='Databricks Configuration file')
@click.option('--node-type', '-n', prompt='cluster node type',
              help='Choose cluster node type (case sensitive), '
                   'use list-nodes command to find acceptable node-type values')
@click.option('--log-level', '-l', type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                                                     case_sensitive=False), default='INFO',
              help='Select log level while running the commands, default level is set to INFO')
def init(org_id: str, habu_sharing_id: str, orchestrator: str, config_file: str, node_type: str, log_level: str):
    """Initialize Habu Databricks framework.
    This will create all the objects (Workspace, cluster and jobs)
    required to run the Habu Agent in the specified Databricks account.
    """

    setup_log(getattr(logging, log_level.upper()))
    config_params = hdb_config.read_config(config_file)
    version_info = pkg_resources.require("habu-databricks-cli")[0].version

    if config_params is not None:
        db_instance = config_params[DATABRICKS_IID]
        init_setup.setup_workspace(db_instance, config_params)
        cluster_id = cluster.setup_cluster(db_instance, config_file, config_params, node_type, RES_CONFIG)
        job.setup_jobs(db_instance, org_id, habu_sharing_id, orchestrator, cluster_id,
                       config_params)
        job.run_job_by_name(db_instance, CLI_INSTALLER, config_params,
                            job.get_cli_installer_job_config(org_id, habu_sharing_id, orchestrator, version_info))
    else:
        logging.error(f'Failed to read config from {config_file}, use config cmd to generate config')
