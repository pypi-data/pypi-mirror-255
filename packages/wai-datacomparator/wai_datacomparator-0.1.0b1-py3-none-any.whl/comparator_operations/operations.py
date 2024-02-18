from typing import Any, Dict

from logger.logger import Logger
from comparator_operations.services import (
    _test_primary_key,
    _test_joins,
    _compare_columns,
    _compare_content,
    _store_results
)


class ComparisonConstants:
    STARTING_COMPARISON_LOG = "Starting comparison"
    NUMERAL_TOLERANCES_LOG = "Numeral tolerances: {tolerances}"
    MAPPING_VALUES_LOG = "Mapping values prior to doing the comparison"
    COMPLETED_COMPARISON_LOG = "Completed comparison"


def _run_comparison(
        logger: Logger,
        old_dataframe: Any,
        new_dataframe: Any,
        primary_key: str,
        old_columns_exclude: Any = [],
        date_fields: Any = [],
        datetime_fields: Any = [],
        day_first_in_dates: bool = False,
        numerical_tolerances: float = 0.0001,
        output_file: str = None
) -> Any:
    logger.debug(
        msg=ComparisonConstants.STARTING_COMPARISON_LOG,
        header=True
    )
    logger.debug(msg=ComparisonConstants.NUMERAL_TOLERANCES_LOG.format(
        tolerances=numerical_tolerances)
    )

    old_dataframe.drop(columns=old_columns_exclude, inplace=True)

    if not _test_primary_key(logger, old_dataframe, new_dataframe, primary_key):
        return

    _test_joins(
        logger=logger,
        old_dataframe=old_dataframe,
        new_dataframe=new_dataframe,
        primary_key=primary_key
    )

    _compare_columns(
        logger=logger,
        old_dataframe=old_dataframe,
        new_dataframe=new_dataframe
    )

    combined_dataframe = _compare_content(
        logger=logger,
        old_dataframe=old_dataframe,
        new_dataframe=new_dataframe,
        primary_key=primary_key,
        date_fields=date_fields,
        datetime_fields=datetime_fields,
        day_first_in_dates=day_first_in_dates,
        num_tolerances=numerical_tolerances
    )

    if output_file is not None:
        _store_results(
            logger=logger,
            file_path=output_file
        )

    logger.debug(
        msg=ComparisonConstants.COMPLETED_COMPARISON_LOG,
        header=True
    )

    return combined_dataframe


def map_values_prior_to_comparison(
        logger: Logger,
        dataframe: Any, value_mappings: Dict
) -> Any:
    logger.debug(msg=ComparisonConstants.MAPPING_VALUES_LOG)

    for column, mapping in value_mappings.items():
        for old_value, new_value in mapping.items():
            if old_value == "null":
                dataframe[column].fillna(new_value, inplace=True)
            else:
                dataframe[column] = dataframe[column].replace(old_value, new_value)

    return dataframe
