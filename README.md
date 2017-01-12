`zephyr`
======

This project automates several reports which quantify Logicworks' value
proposition to its clients. It standardizes the design of these reports which
makes it easier to see what information clients use for decision making. This
reduces the ad-hoc nature of report construction and archival. Additionally,
the `zephyr` command archives each report in S3 for posterity making our
reporting more easily auditable.


```
$ zephyr
usage: zephyr (sub-commands ...) [options ...] {arguments ...}

The zephyr reporting toolkit

commands:

  configure
    Gather configuration values.

  data
    Generate single table reports for an account.

  etl
    Perform Extract-Transform-Load operations on data.

  meta
    Gather client meta information.

  report
    Generate advanced reports.

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output
  -o {json,default,csv} output handler
```

## Installation ##

1. Clone the repository.
```
$ git clone ssh://git@code.logicworks.net:44322/zephyr/zephyr.git
```

2. Create and activate a Python 3 virtualenv.

3. Change directory into the repository.

4. Install `zephyr` via `pip`:
```
$ pip install --editable .
```

## Configuration ##

Configuration can be managed by environment variables or a configuration file.
The `zephyr configure` command prompts the user for values for all valid
configuration parameters. Use the `--first-run` to initialize a configuration
file with empty values. Running with `--no-prompt` will show the available
parameters and their current values.

## Available Commands ##

The primary subcommands are `configure`, `data`, `etl`, `meta` and `report`.

The `zephyr meta` command initalizes the local database with client data from
AWS, Logicops and Salesforce including projects and unique identifiers.

Command                      | Description
-----------------------------|-----------------------------------------------
**`zephyr data`**            |
billing-line-items           | Provides a line items billing summary.
billing-line-item-aggregates | Provides an aggregate line items billing summary.
compute-av                   | Shows which instances have the anti-virus agent installed.
compute-details              | Get the detailed instance meta information.
compute-migration            | Recommends which insatnces should be updated.
compute-ri                   | List RI purchase recommendations.
compute-underutilized        | List instances which have low CPU utilization.
db-details                   | Get the detailed rds meta information.
db-idle                      | List idle database instances.
domains                      | List route-53 domains.
iam-users                    | List IAM users.
lb-idle                      | List idle load balancers.
ri-pricings                  | Outlines pricing information for reserved instances.
service-requests             | List the open service requests assoicated to an account.
storage-detached             | List detached storage volumes.
                             |
**`zephyr etl`**             |
dbr-ri                       | Filter the DBR leaving only reserved instance line items.
                             |
**`zephyr report`**          |
account-review               | Generate a report quantifing Logicworks' value proposition.
billing                      | Generate a Billing worksheet of the Account Review.
ec2                          | Generate a EC2 Details worksheet of the Account Review.
migration                    | Generate a EC2 migration recommendations worksheet.
rds                          | Generate a RDS Details worksheet.
ri-recs                      | Generate a RI recommendations worksheet.
sr                           | Generate a Service Requests worksheet.
underutilized                | Generate a EC2 underutilized instances worksheet.
