from dataclasses import dataclass
import re
import pandas as pd
from typing import List

from ..utils.InputFile import InputFile
from ..utils.variable_overview import VariableOverview
from .pd_clean_up_columns import pd_clean_up_columns


@dataclass
class CsvVukvoDataset:
    input_file: str
    json_file: str

    def __post_init__(self):

        if not InputFile(self.input_file).valid():
            raise OSError(f'{self.input_file} not found')

    def load(self):
        raise NotImplementedError

    def load_as_pandas_df(self, columns_subset: List[str] = [], root_var: str = '') -> pd.DataFrame:

        def generate_var_overview(json_file: str) -> pd.DataFrame:
            return VariableOverview(json_file).var_overview

        def clean_root_data(df: pd.DataFrame, root_var: str) -> pd.DataFrame:
            query_string = f'{root_var}.notnull()'
            try:
                df2 = df.query(query_string)
            except KeyError:
                # self.logger.debug('clean_root_data tried to filter df, but variable does not exist')
                return df
            # self.logger.debug(f'clean_root_data removed {self.data.shape[0] - df2.shape[0]} cases from dataframe')
            return df2

        if columns_subset:
            df = pd.read_csv(self.input_file, use_cols=columns_subset, encoding='utf-8-sig', sep=';', decimal=',', low_memory=False)
        else:
            df = pd.read_csv(self.input_file, encoding='utf-8-sig', sep=';', decimal=',', low_memory=False)

        df = df.rename(columns=lambda x: re.sub(r'(\/)', '__', x))  # Replacing / with __
        df.columns = [col.lower() for col in df.columns]
        if root_var:
            df = clean_root_data(df, root_var)
        df = pd_clean_up_columns(df)
        return df
