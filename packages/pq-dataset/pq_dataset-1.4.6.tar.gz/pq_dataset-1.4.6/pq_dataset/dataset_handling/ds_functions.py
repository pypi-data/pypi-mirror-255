from loguru import logger
import pandas as pd
from typing import List

from ..utils.InputFile import InputFile
from .parquet import ParquetDataset
from .csv_vukvo import CsvVukvoDataset


def return_dataset_type(input_file: str) -> str:
    dataset_types = {'.parquet': 'parquet',
                     '.zip': 'parquet',
                     '.csv': 'csv'}
    file_extension = InputFile(input_file).file_type
    return dataset_types[file_extension]


def dataset_loader(input_file: str, json_file: str, columns_subset: List[str] = [], root_var: str = '', rel_vars: List[str] = []) -> pd.DataFrame:

    logger.debug(f'Started preparing dataset from file: {input_file}')

    if not InputFile(input_file).valid():
        raise OSError(f'{input_file} not found')

    file_type = return_dataset_type(input_file)

    if file_type == 'parquet':
        df = ParquetDataset(input_file, json_file).load_as_pandas_df(columns_subset, root_var)
    elif file_type == 'csv':
        df = CsvVukvoDataset(input_file, json_file).load_as_pandas_df(columns_subset, root_var)
    else:
        raise ValueError(f'{file_type} is not supported')

    logger.debug(f'Done loading {input_file} (type: {file_type}) as pd.DataFrame')

    return df
