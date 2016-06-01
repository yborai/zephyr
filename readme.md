## EC2 details sheet generator

To use this generator just import `create_sheet` function from `zephyr.ec2_details` module and run it:

```python
from zephyr.ec2_details_sheet import create_sheet

create_sheet(json_string, csv_filepath)
```

New csv file will appear on provided path.
Default value for `csv_filepath` param is `ec2_details.csv` (file will appear in current directory).

## RDS details sheet generator

To use this generator just import `create_sheet` function from `zephyr.rds_details` module and run it:

```python
from zephyr.rds_details import create_sheet

create_sheet(json_string, csv_filepath)
```

New csv file will appear on provided path.
Default value for `csv_filepath` param is `rds_details.csv` (file will appear in current directory).

## EC2 RI recommendations sheet generator

To use this generator just import `create_sheet` function from `zephyr.ec2_ri_recommendations` module and run it:

```python
from zephyr.ec2_ri_recommendations import create_sheet

create_sheet(json_string, csv_filepath)
```

New csv file will appear on provided path.
Default value for `csv_filepath` param is `ec2_ri_recommendations.csv` (file will appear in current directory).

## EC2 migration recommendations sheet generator

To use this generator just import `create_sheet` function from `zephyr.ec2_migration_recommendations` module and run it:

```python
from zephyr.ec2_migration_recommendations import create_sheet

create_sheet(json_string, csv_filepath)
```

New csv file will appear on provided path.
Default value for `csv_filepath` param is `ec2_migration_recommendations.csv` (file will appear in current directory).

## EC2 underutilized instances sheet generator

To use this generator just import `create_sheet` function from `zephyr.ec2_underutilized_instances` module and run it:

```python
from zephyr.ec2_underutilized_instances import create_sheet

create_sheet(json_string, csv_filepath)
```

New csv file will appear on provided path.
Default value for `csv_filepath` param is `ec2_underutilized_instances.csv` (file will appear in current directory).

## EC2 underutilized instances breakdown sheet generator

To use this generator import `create_sheet` function from `zephyr.ec2_underutilized_instances_breakdown` module.
Also you need a function to define category for each line of review. You need to create this function by yourself
and provide it as a parameter.
Example:

```python
from zephyr.ec2_underutilized_instances_breakdown import create_sheet

def define_category(raw_category):
    if "prod" in raw_category:
        return "prod"
    if "mgmt" in raw_category:
        return "mgmt"
    if "stage" in raw_category or "staging" in raw_category:
        return "stage"

    return "other"

create_sheet(json_string, define_category, csv_filepath)
```

New csv file will appear on provided path.
Default value for `csv_filepath` param is `ec2_instances_breakdown.csv` (file will appear in current directory).

## Service requests sheet generator

To use this generator just import `create_sheet` function from `zephyr.service_requests` module and run it:

```python
from zephyr.service_requests import create_sheet

create_sheet(json_string, csv_filepath)
```

New csv file will appear on provided path. Also two other minor csv reviews will appear near the provided path.
Default value for `csv_filepath` param is `service_requests.csv` (file will appear in current directory).

## Complete account review xlsx sheet generator

To use this generator you need import `create_xlsx_account_review` function from `zephyr.account_review` module.
After the import you may use this function.
To do so you need to pass a bunch of arguments to fulfill the entire review generation:

```python
import zephyr.account_review

def define_category(raw_category):
    if "prod" in raw_category:
        return "prod"
    if "mgmt" in raw_category:
        return "mgmt"
    if "stage" in raw_category or "staging" in raw_category:
        return "stage"

    return "other"


create_xlsx_account_review(destination_folder_path, result_review_filename,
service_requests_json=service_requests_json,
ec2_details_json=ec2_details_json,
rds_details_json=rds_details_json,
ec2_ri_recommendations_json=ec2_ri_recommendations_json,
ec2_migration_recommendations_json=ec2_migration_recommendations_json,
ec2_underutilized_instances_json=ec2_underutilized_instances_json,
define_category_func=define_category,
temporary_folder_name=temp_folder_name
)
```

Each `*_json` argument is a string to be parsed to create a review.
If any `*_json` argument will be omitted it will not appear in final review.
To create `EC2 underutilized instances breakdown` review you also need to pass define_category_func.
If this function is omitted, `EC2 underutilized instances breakdown` review will not be created.
