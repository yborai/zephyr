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

  etl
    Perform Extract-Transform-Load operations on data.

  meta
    Gather client meta information.

  report
    Generate reports for an account. Default output is a .xlsx file.

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

The primary subcommands are `configure`, `etl`, `meta` and `report`.

The `zephyr meta` command initalizes the local database with client data from
AWS, Logicops and Salesforce including projects and unique identifiers.

Command                      | Description
-----------------------------|-----------------------------------------------
**`zephyr report`**          |
account-review               | Generate a report quantifing Logicworks' value proposition.
billing                      | Generate a billing summary with line items, aggregate line items, and monthly costs.
compute-av                   | Generate a report showing which instances have the anti-virus agent installed.
compute-details              | Generate a EC2 Details worksheet of the Account Review.
compute-migration            | Generate a EC2 migration recommendations worksheet.
compute-ri                   | Generate a RI recommendations worksheet.
compute-underutilized        | Generate a EC2 underutilized instances worksheet.
db-details                   | Generate a RDS Details worksheet.
db-idle                      | Generate a report with idle database instances.
domains                      | Generate a report of route-53 domains.
iam-users                    | Generate a report of IAM users.
lb-idle                      | Generate a report of idle load balancers.
service-requests             | Generate a report of current service requests assoicated to an account.
storage-detached             | Generate a report of detached storage volumes.
                             |
**`zephyr etl`**             |
dbr-ri                       | Filter the DBR leaving only reserved instance line items.
