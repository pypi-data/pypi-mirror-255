import pandas as pd
from pathlib import Path
from typing import Union, Optional
from pandas import DataFrame
from logger.logger import Logger


class ReadDataConstants:
    READ_ROWS_LOG = "Read {rows} rows from {file_name} ({label})"
    READ_ERROR_LOG = "Unable to read data from {file_path} - {error}"
    DEFAULT_LABEL = "na"
    DELIMITER = "\t"


def _read_data(
        logger: Logger,
        file_path: Union[str, Path],
        csv: bool = False,
        label: str = ReadDataConstants.DEFAULT_LABEL
) -> Optional[DataFrame]:
    try:
        file_path = Path(file_path)
        if csv:
            data: DataFrame = pd.read_csv(filepath_or_buffer=file_path)
        else:
            data: DataFrame = pd.read_csv(
                filepath_or_buffer=file_path,
                delimiter=ReadDataConstants.DELIMITER,
                low_memory=False
            )

        logger.debug(msg=ReadDataConstants.READ_ROWS_LOG.format(
            rows=len(data),
            file_name=file_path.name,
            label=label)
        )
        return data
    except Exception as e:
        logger.error(msg=ReadDataConstants.READ_ERROR_LOG.format(
            file_path=file_path,
            error=e)
        )
        return None
