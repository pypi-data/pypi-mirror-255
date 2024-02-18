from dataclasses import dataclass
from loguru import logger
import pandas as pd
from pathlib import Path
from zipfile import ZipFile
from typing import List
import pyarrow.parquet as pq
import pyarrow.compute as pc
import pyarrow as pa
import shutil

from ..utils.InputFile import InputFile
from ..utils.variable_overview import VariableOverview


@dataclass
class ParquetDataset:
    input_file: str
    json_file: str

    def __post_init__(self):

        logger.debug(f'Instantiated {self.__class__.__name__} from {self.input_file}')

        if not InputFile(self.input_file).valid():
            raise OSError(f'{self.input_file} not found')

        self.type = InputFile(self.input_file).file_type

    def load(self) -> pa.Table:
        return self.__read_file_to_table()

    def load_as_pandas_df(self, columns_subset: List[str] = [], root_var: str = '', rel_vars: List[str] = []) -> pd.DataFrame:

        logger.debug('Started loading parquet file as pandas df')

        def generate_var_overview(json_file: str) -> pd.DataFrame:
            return VariableOverview(json_file).var_overview

        if not columns_subset:
            try:
                df = self.__read_file_to_table(root_var=root_var).to_pandas()
            except MemoryError:
                raise MemoryError(
                    f'{self.input_file} cannot be read due to memory issues. Consider reducing the amount of columns')
        else:
            columns_subset_renamed = self.__convert_varnames_to_varrefs(
                columns_subset)
            df = self.__read_file_to_table(
                columns_subset_renamed, root_var).to_pandas()

        var_overview = generate_var_overview(self.json_file)
        colnames_dict = dict(
            zip(var_overview.reference, var_overview.adj_name))
        df.rename(columns=colnames_dict, inplace=True)

        logger.debug('Finished loading parquet file as pandas df')
        return df

    def __convert_varnames_to_varrefs(self, list_of_cols: List[str]) -> List[str]:
        var_map = VariableOverview(self.json_file).var_map
        list_of_varsrefs = [var_map[col] for col in list_of_cols]
        return list_of_varsrefs

    def __read_file_to_table(self, columns_subset: List[str] = [], root_var: str = '') -> pa.Table:

        def clean_up_root_variable(pa_table: pa.Table, root_var: str) -> pa.Table:
            root_var_renamed = self.__convert_varnames_to_varrefs([root_var])[
                0]
            exp = pc.is_valid(pa_table.column(root_var_renamed))
            table_temp = pa_table.filter(exp)
            logger.debug(
                f'clean_up_root_variable deleted {pa_table.num_rows-table_temp.num_rows} cases where {root_var} is null')
            return table_temp

        def drop_columns_with_all_nulls(pa_table: pa.Table) -> pa.Table:
            columns_with_all_nulls = [col_name for col_name in pa_table.column_names if pc.count(
                pa_table.column(col_name), mode='only_null').as_py() == pa_table.num_rows]
            logger.debug(
                f'drop_columns_with_all_nulls deleted {len(columns_with_all_nulls)} columns')
            # Needs to be adjusted; variables defined
            return pa_table.drop(columns_with_all_nulls)

        def drop_static_zero_columns(pa_table: pa.Table) -> pa.Table:
            static_cols: List[str] = []
            numeric_cols = [col for col in pa_table.column_names if pa_table.column(
                col).type not in ['binary', 'string']]
            for col in numeric_cols:
                if pc.count_distinct(pa_table.column(col), mode='all').as_py() == 1:
                    if pc.mean(pa_table.column(col)).as_py() == 0:
                        static_cols.append(col)
            logger.debug(
                f'drop_static_zero_columns deleted {len(static_cols)} columns')
            return pa_table.drop(static_cols)

        def drop_static_ptypets(pa_table: pa.Table, var_map: dict['str': 'str']) -> pa.Table:
            ptypes = {key: var_map[key] for key in var_map if key.startswith(
                'background__ptype')}
            ptypes_reduced = {key: ptypes[key] for key, value in ptypes.items(
            ) if value in pa_table.column_names}
            binary_cols = [col for col in list(ptypes_reduced.values(
            )) if pa_table.column(col).type in ['binary', 'string']]
            cols_to_drop: List[str] = []
            for col in binary_cols:
                if pc.count_distinct(pa_table.column(col), mode='all').as_py() == 1:
                    cols_to_drop.append(col)

            cols_to_drop.extend([ptypes_reduced[col[:-1]] for col,
                                value in ptypes_reduced.items() if value in cols_to_drop])
            logger.debug(
                f'drop_static_ptypets deleted {len(cols_to_drop)} columns')
            return pa_table.drop(cols_to_drop)

        def convert_binaries_to_strings(pa_table: pa.Table) -> pa.Table:
            binary_cols = [col for col in pa_table.column_names if pa_table.column(
                col).type == 'binary']
            for col in binary_cols:
                decoded = pc.cast(pa_table.column(
                    col), target_type=pa.string())
                pa_table = pa_table.set_column(
                    pa_table.schema.get_field_index(col), col, decoded)
            logger.debug('Converted all binary columns to utf-8 strings')
            return pa_table

        file_name = InputFile(self.input_file).full_path_filename
        file_path = InputFile(self.input_file).full_path

        logger.debug(
            f'__read_file_to_table started handling parqet file of type: {self.type}')

        if self.type == '.zip':

            upd_path = Path(file_path) / 'temp_parq'
            if Path(upd_path).exists():
                shutil.rmtree(upd_path)

            with ZipFile(file_name, 'r') as zip_obj:
                zip_obj.extractall('temp_parq')

            logger.debug('Finished extracting zip-archive')

            table = pq.ParquetDataset(Path(upd_path)).read(
                columns=columns_subset) if columns_subset else pq.ParquetDataset(Path(upd_path)).read()
            logger.debug('Loaded unpacked files as table')

        elif self.type == '.parquet':

            table = pq.read_table(
                file_name, columns=columns_subset) if columns_subset else pq.read_table(file_name)

        # Stupid - vildere klovn vildere
        if root_var:
            table = clean_up_root_variable(table, root_var)
        table = drop_columns_with_all_nulls(table)
        table = drop_static_zero_columns(table)
        # Removed - seemed to create problems in some cases
        # table = drop_static_ptypets(
        #     table, VariableOverview(self.json_file).var_map)
        table = convert_binaries_to_strings(table)

        logger.debug('__read_file_to_table finished')
        return table
