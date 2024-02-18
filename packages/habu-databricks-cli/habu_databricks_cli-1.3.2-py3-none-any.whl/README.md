# Habu Databricks Cli

```
Usage: hdb-cli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  config      Command to generate the config for the habu databricks agent.
  init        Initialize Habu Databricks framework.
  list-nodes  Command to list available node types to create cluster.
  version     Display version of the cli
```

## Command to generate config file (must be run the first time)

```
Usage: hdb-cli config [OPTIONS]

  Command to generate the config for the habu databricks agent. The config
  is required to set up the habu databricks framework

Options:
  -c, --config-file TEXT          File name where config will get saved
                                  (default is habu_databricks_config.yaml in
                                  current directory)

  -i, --databricks-instance TEXT  Databricks instance id (<instance-
                                  id>.cloud.databricks.com)

  -u, --login TEXT                Databricks user name (me@example.com)
  -p, --password TEXT             Enter the password
  -l, --log-level [CRITICAL|ERROR|WARNING|INFO|DEBUG]
                                  Select log level while running the commands,
                                  default level is set to INFO

  -m, --auto-termination-mins TEXT
                                  Automatically terminate the cluster after it
                                  is inactive for this time in minutes. If not
                                  set, the cluster will not be automatically
                                  terminated.The threshold must be between 10
                                  and 10000 minutes. You can also set this
                                  value to 0 to explicitly disable automatic
                                  termination.

  --help                          Show this message and exit.
```

## list-nodes command (lists supported node type ids to create cluster)

```
Usage: hdb-cli list-nodes [OPTIONS]

  Command to list available node types to create cluster. The results are
  the valid values that can be passed as node-type in init command

Options:
  -c, --config-file TEXT          File name from where config gets read
                                  (default is habu_databricks_config.yaml in
                                  current directory)

  -l, --log-level [CRITICAL|ERROR|WARNING|INFO|DEBUG]
                                  Select log level while running the commands,
                                  default level is set to INFO

  --help                          Show this message and exit.
```

## Init command (sets up workspace, cluster and jobs)

```
Usage: hdb-cli init [OPTIONS]

  Initialize Habu Databricks framework. This will create all the objects
  (Workspace, cluster and jobs) required to run the Habu Agent in the
  specified Databricks account.

Options:
  -o, --org-id TEXT               Habu Org Id
  -s, --habu-sharing-id TEXT      Habu Sharing Id (aws:<region>:<id>)
  -oc, --orchestrator TEXT        Orchestrator name
  -c, --config-file TEXT          Databricks Configuration file
  -node-type, -n TEXT             Choose cluster node type (case sensitive),
                                  use list-nodes command to find acceptable
                                  node-type values

  -l, --log-level [CRITICAL|ERROR|WARNING|INFO|DEBUG]
                                  Select log level while running the commands,
                                  default level is set to INFO

  --help                          Show this message and exit.
```

## version command (display the version of the cli)
```
Usage: hdb-cli version [OPTIONS]

  Display version of the cli

Options:
  --help  Show this message and exit.
```

