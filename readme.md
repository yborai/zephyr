# zephyr

```
$ zephyr
usage: zephyr (sub-commands ...) [options ...] {arguments ...}

The zephyr reporting toolkit

commands:

  data
    Generate single table reports for an account.

  etl
    Generate single table reports for an account.

  meta
    Gather client meta information.

  report
    Generate advanced reports.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -o {json,default,csv} output handler
  --line_width LINE_WIDTH
```

## installation 

1. clone the repository. 

```
$ git clone ssh://git@code.logicworks.net:44322/zephyr/zephyr.git
```

2. Create a virtualenv.

3. Change directory into the repository.

4. Activate the virtualenv.

5. Install Zephyr with the following command:
```
$pip install --editable . 
```

## data subcommand

Command Name                 | Description
-----------------------------|-----------------------------------------------
billing-monthly              | Provides a monthly itemized billing summary. 
billing-line-items           | Provides a line items billing summary.
billing-line-item-aggregates | Provides an aggregate line items billing summary.
compute-av                   | Shows which instances have the anti-virus agent installed.
compute-details              | Get the detailed instance meta information.
compute-migration            | Recommends which insatnces should be updated.
compute-ri                   | Recommends which instances be transfered to reserved instances based on usage data.
compute-underutilized        | List instances which have low CPU utilization.
db-details                   | Get the detailed rds meta information.
db-idle                      | List idle database instances.
domains                      | List route-53 domains.
iam-users                    | List IAM users.
lb-idle                      | List idle load balancers.
ri-pricings                  | Outlines pricing information for reserved instances.
service-requests             | List the open service requests assoicated to an account.
storage-detached             | List detached storage volumes.

## etl subcommand

Command Name   | Description
---------------|-----------------------------------------------
dbr-ri         | Filter the DBR for only reserved instances.

## meta subcommand

Command Name   | Description
---------------|-------------------------------------------------------
meta           | Gather client information.
## report subcommand

Command Name     | Description
-----------------|-------------------------------------------------------
account-review   | Returns a comprehensive report of a specified account. Includes information about each data subcommand.
sr               | Generate the Service Requests worksheet for a specified account. 
