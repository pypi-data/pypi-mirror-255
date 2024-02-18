
# Data Comparator Service

Data Comparator is a Python package for comparing data from two files. The service reads a configuration file that specifies the details of the comparison operation, such as the logger configurations, old file and new file for the comparison along with the file type, Primary key information. Easy to use and highly flexible, Data Comparator simplifies the process of merging data.

## Installation

You can install DataComparator from PyPI:

```bash
pip install wai-datacomparator
```

## Usage

To use Data Comparator Service, you need to create a configuration file in JSON format. Here’s an example:

```json
{
    "logger": {
        "test_mode": true,
        "req_id": "001",
        "application_name": "Wilson AI Test",
        "application_version": "0.0.1",
        "environment": "Development",
        "environment_modifier": ""
    },
    "data": {
        "old_file_path": "./scores_properties.csv",
        "new_file_path": "./scores_properties_1.csv",
        "csv_format": true
    },
    "comparison": {
        "primary_key": "property_id"
    }
}

```

Once you have your configuration file, you can perform the merge operation with a single function call:

```python
from data_comparator import DataComparator

config_path = "./config.json"
data = DataComparator(config_path=config_path)
data.run_comparison()
```

Replace "config.json" with the path to your actual configuration file.


## Contributing

If you want to contribute to this project, please submit a pull request.

## License

This project is licensed under the MIT License.
