import json
from logger.logger import Logger

from io_operations import read_data_executor
from comparator_operations import run_comparison_executor


class DataComparator:
    def __init__(self, config_path):
        with open(config_path, "r") as file:
            self.config = json.load(file)

        self.logger = Logger()
        self.logger.test_mode = self.config["logger"]["test_mode"]
        self.logger.req_id = self.config["logger"]["req_id"]
        self.logger.application_name = self.config["logger"]["application_name"]
        self.logger.application_version = self.config["logger"]["application_version"]
        self.logger.environment = self.config["logger"]["environment"]
        self.logger.environment_modifier = self.config["logger"]["environment_modifier"]

    def run_comparison(self):
        old_dataframe = read_data_executor(
            logger=self.logger,
            file_path=self.config["data"]["old_file_path"],
            csv=self.config["data"]["csv_format"],
            label="old"
        )
        new_dataframe = read_data_executor(
            logger=self.logger,
            file_path=self.config["data"]["new_file_path"],
            csv=self.config["data"]["csv_format"],
            label="new"
        )

        primary_key = self.config["comparison"]["primary_key"]

        comparison_dataframe = run_comparison_executor(
            logger=self.logger,
            old_dataframe=old_dataframe,
            new_dataframe=new_dataframe,
            primary_key=primary_key
        )
        return comparison_dataframe
