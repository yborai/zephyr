# zephyr

```
$ zephyr
usage: zephyr (sub-commands ...) [options ...] {arguments ...}

The zephyr reporting toolkit

commands:

    configure
      Configure zephyr.
    
    data
      Generate single table reports for an account.
    
    report
      Generate advanced reports.
      
    stub
      a test plugin
      
optional arguments:
    -h, --help  show this help message and exit
    --debug     toggle debug output
    --quiet     suppresss all output
    -o {json}   ouput handler
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

Command Name                | Description
----------------------------|------------------------------------------
billing-monthly             | Provides a monthly itemized billing summary. 
instance-details            | Get the detailed instance meta information.
migration-recommendations   | Recommends which insatnces should be updated.
rds-details                 | Get the detailed rds meta information.
ri-pricings                 | Outlines pricing information for reserved instances
ri-recommendations          | Recommends which instances be transfered to reserved instances based on usage data.
service-requests            | Lists the open service requests assoicated to an account.
underutilized-instances     | Lists instances which have low CPU utilization.


## report subcommand

Command Name   | Description
---------------|-------------------------------------------------------
report         | Returns a comprehensive report of a specified account. Includes information about each data subcommand.
