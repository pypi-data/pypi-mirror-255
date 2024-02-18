from dataclasses import dataclass
from loguru import logger
import pandas as pd
from pathlib import Path
import os
import codecs
import json
from typing import List, Optional

# Class functions


# Module specific functions
from . import room_specific_config as room_config
from .pqd_functions.extract_calculated_from_report_spec import extract_calculated_from_report_spec
from .pqd_functions.reduce_columns_based_on_input import reduce_columns_based_on_input
from .utils.variable_overview import VariableOverview
from .utils.InputFile import InputFile
from .dataset_handling.ds_functions import dataset_loader, return_dataset_type
from .dataset_handling.pd_clean_up_columns import pd_clean_up_columns


@dataclass
class PQDataset:
    """A class making it easier to work with dataset from H&H.

    Attributes
    ----------
    input_file: int
        The file containing data.
    json_file: str
        json map of variables from graphQL query
    input_path: str
        Path of the input files (datasets, json strings with grapql export etc.)
    output_path: str
        Path of the output_path files generated
    room_id: int
        The source of the datasets -
        491, 729 or 999999 are valid entries. 999999 indicates non-H&H Results room.
    debug: bool, default: False
        If True debugging information is logged to file
    relevant_scopes: List[str]
        List of strings matching scopes or parts of scopes. Every variable matching the string will be included in the dataframe.
        E.g. 'background__ptype' includes every ptype variable
    relevant_variables: List[str]
        List of variables to be included in the dataframe

    Output
    ------
    When initiated this class adds two dataframes to the class.
    .data which holds the data as a pandas dataframe
    .var_overview which holds a variable overview of the full dataset

    E.g. 'sprog = PQDataset()' allows for sprog.data and sprog.var_overview to be called

    Methods
    -------
    The class have the following methods which can be called

    .clients_only(): Returns a dataset which only contains clients data - the selection depends on the room (491 or 729)
    .identify_relevante_data_ftp(): Allows for identifying which variables are relevant for data which are to be made avaiable for our clients
    .create_json_ftp_config():

    Config
    ------
    The file room_specific_config.py holds basic configuration for each of the allowed Results rooms


    """

    input_file: str
    json_file: str
    input_path: str
    output_path: str
    room_id: int
    debug: bool = False
    relevant_scopes: Optional[List[str]] = None
    relevant_variables: Optional[List[str]] = None

    def __post_init__(self):
        # Move most of this to main()
        os.chdir(self.input_path)
        self.file_extensions = ['.csv', '.zip', '.parquet']
        self.accepted_rooms = [491, 729, 999999]

        logger.info(f'*** START *** Initializing PQDataset from file: {self.input_file}')

        self.file_type = return_dataset_type(self.input_file)

        if not self.__validate_inputs():
            logger.error('Invalid inputs found')
            raise ValueError('Unrecognized inputs')

        self.config = room_config.setup_config(self.room_id)
        # Probably no need for making this a class attribute
        self.var_map = VariableOverview(self.json_file).var_map
        self.data = self.__load_data()

        logger.info(
            f'*** END *** Done preparing data from {self.input_file}. You can access the dataframe by appending .data to the object that you created - i.e. barnbg.data')

    def __load_data(self) -> pd.DataFrame:
        root_var = self.__return_config_parameter(
            'root_variable')[0] if self.__return_config_parameter('root_variable') else ''
        if self.relevant_scopes or self.relevant_variables:
            list_of_cols = list(self.__create_dict_of_cols())
            if root_var and root_var not in list_of_cols:
                list_of_cols.append(root_var)
            return dataset_loader(self.input_file, self.json_file, columns_subset=list_of_cols, root_var=root_var, rel_vars=self.relevant_variables)
        else:
            return dataset_loader(self.input_file, self.json_file, root_var=root_var)

    def __create_dict_of_cols(self) -> dict[str: str]:
        # Not exactly needed as renaming of variables in parquet datasets have been moved to dataset_handling
        relevant_cols = {}

        if self.relevant_scopes:
            for scope in self.relevant_scopes:
                temp_cols = {var: self.var_map[var]
                             for var in self.var_map if var.startswith(scope)}
            if not temp_cols:
                logger.warning(
                    f'No variables starting with {self.relevant_scopes} was found in data')
            else:
                relevant_cols.update(temp_cols)

        if self.relevant_variables:
            rel_vars_lower = [var.lower() for var in self.relevant_variables]
            temp_vars = {
                var: self.var_map[var] for var in self.var_map if var in rel_vars_lower}
            if not temp_vars:
                logger.warning(
                    f'No variables from {self.relevant_variables} was found in data')
            else:
                relevant_cols.update(temp_vars)

        return relevant_cols

    def __create_list_of_config_vars(self, include_cpr: bool = True) -> List[str]:
        config_vars_to_include: List[str] = []

        if include_cpr:
            for var in self.__return_config_parameter('cpr_variables'):
                if var in self.data.columns:
                    config_vars_to_include.append(var)

        # Appending variables which should always be included
        config_vars_to_include.extend(
            self.__return_config_parameter('must_include_variables'))

        # Adding room specific variables to be included in dataset
        config_vars_to_include.extend(
            self.__return_config_parameter('room_specific_variables'))

        return config_vars_to_include

    def __validate_inputs(self) -> bool:

        if not InputFile(self.input_file).valid():
            logger.critical(f'{self.input_file} is not valid ')
            return False
        if not InputFile(self.json_file).valid():
            logger.critical(f'{self.json_file} is not valid ')
            return False
        if not Path(self.input_path).exists():
            logger.critical(f'The path {self.input_path} does not exist.')
            return False
        if not Path(self.output_path).exists():
            logger.critical(
                f'The path {self.output_path} does not exist.')
            return False
        if self.room_id not in self.accepted_rooms:
            logger.critical(f'Unknown room id {self.room_id}')
            return False
        logger.debug('All inputs are ok.')
        return True

    def __return_config_parameter(self, parameter_name: str) -> List[str]:
        return self.config.get(parameter_name)

    def clean_up_data(self,
                      clients_only: bool = True,
                      remove_testareas: bool = True,
                      remove_archive: bool = False,
                      predaycare_only: bool = False,
                      relevant_scopes: List[str] = [],
                      relevant_variables: List[str] = []) -> pd.DataFrame:
        """Missing description




        """

        def general_setup_check(df: pd.DataFrame, parameter_bool: bool, parameter_variables: List[str]) -> bool:

            parameter_should_be_included_in_query = True

            if not parameter_bool:
                logger.debug(
                    'clean_up_data: Skipping parameter as it is false')
                parameter_should_be_included_in_query = False
                return parameter_should_be_included_in_query

            if not parameter_variables:
                logger.debug('clean_up_data: List of variables is empty')
                parameter_should_be_included_in_query = False
                return parameter_should_be_included_in_query

            variables_in_df = [
                var for var in parameter_variables if var in df.columns]

            if not variables_in_df:
                logger.debug(
                    'clean_up_data: None of the variables supplied is present in dataframe')
                parameter_should_be_included_in_query = False
                return parameter_should_be_included_in_query

            return parameter_should_be_included_in_query

        def parse_testarea_setup(df: pd.DataFrame, remove_testareas: bool, testarea_variables: List[str]) -> str:

            if general_setup_check(df, remove_testareas, testarea_variables):

                testarea_variables_reduced = [
                    var for var in testarea_variables if var in df.columns]
                testarea_variables_queries = [
                    f'not({col}.str.lower().str.startswith("*Test", na=False).values)' for col in testarea_variables_reduced]
                testarea_query = ' and '.join(testarea_variables_queries)
                return testarea_query

            return None

        def parse_archive_setup(df: pd.DataFrame, remove_archive: bool, archive_variables: List[str]) -> str:

            if general_setup_check(df, remove_archive, archive_variables):

                archive_variables_reduced = [
                    var for var in archive_variables if var in df.columns]
                archive_queries = [
                    f'{var}.isnull()' for var in archive_variables_reduced if var in df.columns]

                archive_query = ' and '.join(archive_queries)

                return archive_query

            return None

        query_string_total = []
        archive_variables = self.__return_config_parameter('archive_variables')
        testarea_variables = self.__return_config_parameter(
            'testarea_variables')

        df = self.data

        if clients_only:
            clients_query = self.__return_config_parameter('clients_query')
            if clients_query:
                query_string_total.append(f'{clients_query[0]}')

        if parse_archive_setup(df, remove_archive, archive_variables):
            query_string_total.append(
                f'({parse_archive_setup(df, remove_archive, archive_variables)})')

        if parse_testarea_setup(df, remove_testareas, testarea_variables):
            query_string_total.append(
                f'({(parse_testarea_setup(df, remove_testareas, testarea_variables))})')

        if query_string_total:
            query_string_total_str = ' and '.join(query_string_total)
            df_temp = df.query(f'{query_string_total_str}', engine='python')
        else:
            df_temp = df

        if relevant_scopes or relevant_variables:
            relevant_variables.extend(self.__create_list_of_config_vars())
            df_temp = reduce_columns_based_on_input(
                df_temp, relevant_scopes, relevant_variables)

        return df_temp

    def identify_relevante_data_ftp(self,
                                    analysis_id: int,
                                    reduced_data: pd.DataFrame = None,
                                    relevant_scopes: List[str] = ['background__ptype', 'questionnaire__'],
                                    relevant_variables: List[str] = [],
                                    include_calculated_from_report: str = '',
                                    save_variable_overview: bool = True
                                    ) -> None:
        """Prepares and returns client relevant dataset (pandas dataframe) and variables.

        Parameters
        ----------
        analysis_id: int
        reduced_data : pd.DataFrame, optional (default=None)
            Useful if
        relevant_scopes : List[str], optional (default=[background__ptype] and [questionnaire__])
            Specifies which scopes should be included. If not specified then [background__ptype] and [questionnaire__] scope is included.
        relevant_variables : List[str], optional (default=None)
            Specifies which specfic variables should be included. This is used if only certain variables from a specific scope are relevant
        include_calculated_from_report : str, optional (default=None)
            This is useful for a 'automated' mode for indentifying relevant variables. The supplied string should be the name of the file with the xml config of the relevant report. In most cases this would be the report on child level and not aggregated.
        save_variable_overview : bool, optional (default=True)
            Whether or not an excel-file with a description of the included variables should be saved.

        """
        logger.info('Started identify_relevant_data_ftp')

        if reduced_data is None:
            df = self.data
        else:
            df = pd_clean_up_columns(reduced_data)

        if include_calculated_from_report:
            used_calc_vars = extract_calculated_from_report_spec(self.input_path, include_calculated_from_report, analysis_id, VariableOverview(self.json_file).var_overview)
            if used_calc_vars:
                relevant_variables.extend(used_calc_vars)

        relevant_variables.extend(self.__create_list_of_config_vars())
        df = reduce_columns_based_on_input(df, relevant_scopes, relevant_variables)

        self.data_ftp = df
        var_overview = VariableOverview(self.json_file).var_overview
        self.var_overview_reduced = var_overview[var_overview['adj_name'].isin(self.data_ftp.columns)]

        if save_variable_overview:
            file_name = f'{InputFile(self.input_file).file_name_wo_ext}_variabel_beskrivelse.xlsx'
            file_path = f'{self.output_path}\{file_name}'
            relevant_cols = ['adj_name', 'name', 'referenceType', 'text', 'choice_value']
            try:
                self.var_overview_reduced[relevant_cols].to_excel(
                    file_path, index=False)
                logger.info(
                    f'Saved description of variables to be transferred to ftp as {file_path}')
            except PermissionError:
                logger.info(
                    f'Error saving file as a file with ({file_name}) is already open.')

        logger.info(
            'Ended identify_relevant_data_ftp. Data can be accessed by appending .data_ftp to your object.')

        return None

    def create_json_ftp_config(self, name: str, analysis: int, ftp_path: str) -> None:

        json_output = {'name': name,
                       'analysisId': analysis,
                       'output': ftp_path,
                       'variables': []
                       }

        for _, row in self.var_overview_reduced.iterrows():
            if row['referenceType'] == 'TypeChoiceSingle':
                continue
            if row['referenceType'] == 'TypeClosedMultiple' and row['nb_choices_all'] == 1:
                continue                
            json_output['variables'].append(
                {'reference': row['reference'], 'displayName': row['adj_name']})

        file_name = f'{InputFile(self.input_file).file_name_wo_ext}_ftp_config.json'

        json_output_file = self.output_path + os.path.sep + file_name

        with codecs.open(json_output_file, 'w', 'UTF-8-SIG') as outfile:
            json.dump(json_output, outfile, indent=4)

        print(f'Json file saved as {file_name} in {self.output_path}')

        return None
