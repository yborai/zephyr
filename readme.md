## ec2 details sheet generator

To use this generator just import `create_sheet` method from `ec2_details` module and run it:

```python
from ec2_details_sheet import create_sheet

create_sheet(json_string, csv_filepath)
```

New csv file will appear on provided path.
Default value for `csv_filepath` param is `ec2_details.csv` (file will apper in current directory).

## rds details sheet generator

To use this generator just import `create_sheet` method from `rds_details` module and run it:

```python
from rds_details import create_sheet

create_sheet(json_string, csv_filepath)
```

New csv file will appear on provided path.
Default value for `csv_filepath` param is `ec2_details.csv` (file will apper in current directory).
