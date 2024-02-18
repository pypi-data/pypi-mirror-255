import pandas as pd

from typing import Any


class CompareFieldsConstants:
    DEFAULT_DATE_FILL = "1900-01-01"
    DEFAULT_NUMERIC_FILL = 0


def __compare_date_fields(
        date_field_old: pd.Series,
        date_field_new: pd.Series,
        day_first: bool = False
) -> Any:
    old_date = pd.to_datetime(date_field_old, errors="coerce", dayfirst=day_first)
    new_date = pd.to_datetime(date_field_new, errors="coerce", dayfirst=day_first)

    old_date.fillna(value=CompareFieldsConstants.DEFAULT_DATE_FILL, inplace=True)
    new_date.fillna(value=CompareFieldsConstants.DEFAULT_DATE_FILL, inplace=True)

    difference = old_date == new_date

    return difference


def __compare_numerical_fields(
        numeric_field_old: pd.Series,
        numeric_field_new: pd.Series,
        tolerance: float
) -> Any:
    # TODO: Implement a separate test for NAs, because we can accidentally miss an issue if the correct value is 0,
    #  but one DF has missing values and we impute them to 0.
    numeric_field_old.fillna(value=CompareFieldsConstants.DEFAULT_NUMERIC_FILL, inplace=True)
    numeric_field_new.fillna(value=CompareFieldsConstants.DEFAULT_NUMERIC_FILL, inplace=True)

    difference = abs(numeric_field_old - numeric_field_new) < tolerance

    return difference
