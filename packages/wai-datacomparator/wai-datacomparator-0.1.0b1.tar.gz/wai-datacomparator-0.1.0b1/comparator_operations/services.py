from typing import Any
from logger.logger import Logger

from comparator_operations.utils import __compare_date_fields, __compare_numerical_fields


class TestPrimaryKeyConstants:
    PK_NOT_FOUND = "Primary key {primary_key} not found in one or both of the datasets"
    PK_NOT_UNIQUE_OLD = "Primary key {primary_key} not unique in old dataset"
    PK_NOT_UNIQUE_NEW = "Primary key {primary_key} not unique in new dataset"
    PK_TESTS_PASS = "Primary key tests pass"


class TestJoinsConstants:
    TEST_JOINS_LOG = "Testing joins"
    ROWS_IN_OLD_NOT_IN_NEW = "Rows in old not in new: {count} ({percentage}%)"
    ROWS_IN_NEW_NOT_IN_OLD = "Rows in new not in old: {count} ({percentage}%)"
    JOIN_TESTS_PASS = "Join tests pass"


class StoreResultsConstants:
    LOG_LINE_FORMAT = "{timestamp} {severity} {message}\n"


class ColumnComparisonConstants:
    COLUMN_COMPARISON_START = "Comparing columns"
    COLUMNS_MATCH = "Columns match exactly"
    OLD_NOT_IN_NEW = "There are {num_columns} columns in old not in new: {columns}"
    NEW_NOT_IN_OLD = "There are {num_columns} columns in new not in old: {columns}"


class ContentComparisonConstants:
    COMPARING_CONTENT = "Comparing content"
    COLUMN_MATCH_RATE = "Column {column} match rate: {rate}"
    CONTENT_MATCHES_EXACTLY = "Content matches exactly"


def _test_primary_key(
        logger: Logger,
        old_dataframe: Any,
        new_dataframe: Any,
        primary_key: str
) -> bool:
    if primary_key not in old_dataframe.columns or primary_key not in new_dataframe.columns:
        logger.error(TestPrimaryKeyConstants.PK_NOT_FOUND.format(primary_key=primary_key))
        return False

    if len(old_dataframe) != len(old_dataframe[primary_key].unique()):
        logger.error(TestPrimaryKeyConstants.PK_NOT_UNIQUE_OLD.format(primary_key=primary_key))
        return False

    if len(new_dataframe) != len(new_dataframe[primary_key].unique()):
        logger.error(TestPrimaryKeyConstants.PK_NOT_UNIQUE_NEW.format(primary_key=primary_key))
        return False

    logger.debug(TestPrimaryKeyConstants.PK_TESTS_PASS)
    return True


def _test_joins(
        logger: Logger,
        old_dataframe: Any,
        new_dataframe: Any,
        primary_key: str
):
    logger.debug(
        msg=TestJoinsConstants.TEST_JOINS_LOG,
        header=True
    )

    old_keys = set(old_dataframe[primary_key])
    new_keys = set(new_dataframe[primary_key])
    both_keys = old_keys.intersection(new_keys)

    old_only = old_keys - both_keys
    new_only = new_keys - both_keys

    issues_found = 0
    if len(old_only) > 0:
        logger.warning(msg=TestJoinsConstants.ROWS_IN_OLD_NOT_IN_NEW.format(
            count=len(old_only),
            percentage=100 * round(len(old_only) / len(old_keys), 4))
        )
        issues_found += 1
    if len(new_only) > 0:
        logger.warning(msg=TestJoinsConstants.ROWS_IN_NEW_NOT_IN_OLD.format(
            count=len(new_only),
            percentage=100 * round(len(new_only) / len(new_keys), 4))
        )
        issues_found += 1

    if issues_found == 0:
        logger.debug(TestJoinsConstants.JOIN_TESTS_PASS)


def _store_results(
        logger: Logger,
        file_path: str
):
    content = ''
    for log_record in logger.logs:
        content += StoreResultsConstants.LOG_LINE_FORMAT.format(
            timestamp=log_record["timestamp"],
            severity=log_record["severity"],
            message=log_record["message"]
        )

    with open(file_path, "w") as file:
        file.write(content)


def _compare_columns(
        logger: Logger,
        old_dataframe: Any,
        new_dataframe: Any
) -> bool:
    logger.debug(
        msg=ColumnComparisonConstants.COLUMN_COMPARISON_START,
        header=True
    )

    old_cols = set(old_dataframe.columns)
    new_cols = set(new_dataframe.columns)
    both_cols = old_cols.intersection(new_cols)

    old_only = old_cols - both_cols
    new_only = new_cols - both_cols

    n_issues: int = 0

    if old_only:
        old_only_str = " ".join(map(str, old_only))
        logger.warning(msg=ColumnComparisonConstants.OLD_NOT_IN_NEW.format(
            num_columns=len(old_only),
            columns=old_only_str)
        )
        n_issues += 1

    if new_only:
        new_only_str = " ".join(map(str, new_only))
        logger.warning(msg=ColumnComparisonConstants.NEW_NOT_IN_OLD.format(
            num_columns=len(new_only),
            columns=new_only_str)
        )
        n_issues += 1

    if n_issues == 0:
        logger.debug(msg=ColumnComparisonConstants.COLUMNS_MATCH)
        return True
    else:
        return False


def _compare_content(
        logger: Logger,
        old_dataframe: Any,
        new_dataframe: Any,
        primary_key: str,
        date_fields: Any,
        datetime_fields: Any,
        day_first_in_dates: Any,
        num_tolerances: Any
):
    logger.debug(
        msg=ContentComparisonConstants.COMPARING_CONTENT,
        header=True
    )

    columns = set(old_dataframe.columns).intersection(set(new_dataframe.columns))
    columns = columns - {primary_key}

    merged_dataframe = old_dataframe.merge(new_dataframe, on=primary_key)
    n_issues = 0

    for column in columns:
        column_x = f'{column}_x'
        column_y = f'{column}_y'

        if column in date_fields:
            merged_dataframe["difference"] = __compare_date_fields(
                date_field_old=merged_dataframe[column_x],
                date_field_new=merged_dataframe[column_y],
                day_first=day_first_in_dates
            )

        elif (merged_dataframe[column_x].dtype in ["float64", "int64"] and
              merged_dataframe[column_y].dtype in ["float64", "int64"]):
            if isinstance(num_tolerances, dict):
                num_tolerance = num_tolerances.get(column, num_tolerances.get("default"))
            else:
                num_tolerance = num_tolerances

            merged_dataframe["difference"] = __compare_numerical_fields(
                numeric_field_old=merged_dataframe[column_x],
                numeric_field_new=merged_dataframe[column_y],
                tolerance=num_tolerance
            )

        else:
            merged_dataframe[column_x].fillna("NA")
            merged_dataframe[column_y].fillna("NA")
            merged_dataframe["difference"] = merged_dataframe[column_x] == merged_dataframe[column_y]

        difference_average = merged_dataframe["difference"].mean()
        if difference_average < 1:
            message = ContentComparisonConstants.COLUMN_MATCH_RATE.format(
                column=column,
                rate=difference_average
            )
            if difference_average > 0.98:
                logger.debug(msg=message)
            elif difference_average > 0.9:
                logger.warning(msg=message)
            else:
                logger.error(msg=message)
            n_issues += 1

    if n_issues == 0:
        logger.debug(msg=ContentComparisonConstants.CONTENT_MATCHES_EXACTLY)

    return merged_dataframe

