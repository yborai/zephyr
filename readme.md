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

1. clone the repository 

```
$ git clone ssh://git@code.logicworks.net:44322/zephyr/zephyr.git
```

2. install the requirements inside a virtualenv and the cloned repository 

```
$pip install --editable 
```

## configure subcommand

```
$ zephyr configure --help
usage: zephyr (sub-commands ...) [options ...] {arguments ...}

Configure zephyr.

optional arguments:
  -h, --help  show this help message and exit
  --debug     toggle debug output
  --quiet     suppress all output
  -o {json}   output handler
```

## data subcommand

```
$ zephyr data --help
usage: zephyr (sub-commands ...) [options ...] {arguments ...}

Generate single table reports for an account.

commands:

  billing-monthly
    Get the monthly billing meta information.

  instance-details
    Get the detailed instance meta information.

  migration-recommendations
    Get the migration recommendations meta information

  rds-details
    Get the detailed rds meta information

  ri-pricings
    Get the detailed ri pricings meta information.

  ri-recommendations
    Get the ri recommendations meta information.

  service-requests
    get the detailed service requests meta information.

  underutilized-instances
    Get the underutilized instance meta information

  underutilized-instances-breakdown
    Get the underutilized instance breakdown meta information

optional arguments:
  -h, --help       show this help message and exit
  --debug          toggle debug output
  --quiet          suppress all output
  -o {json}        output handler
  --config CONFIG  Path to configuration file
  --cache CACHE    The path to the cached response to use.
```

## report subcommand

```
$ zephyr report --help
usage: zephyr (sub-commands ...) [options ...] {arguments ...}

Generate advanced reports.

commands:

  account-review
    Generate an account review for a given account.

optional arguments:
  -h, --help  show this help message and exit
  --debug     toggle debug output
  --quiet     suppress all output
  -o {json}   output handler
```

## stub

```
$ zephyr stub --help
usage: zephyr (sub-commands ...) [options ...] {arguments ...}

a test plugin

commands:

  echo
    Echo a message.

optional arguments:
  -h, --help  show this help message and exit
  --debug     toggle debug output
  --quiet     suppress all output
  -o {json}   output handler
```
