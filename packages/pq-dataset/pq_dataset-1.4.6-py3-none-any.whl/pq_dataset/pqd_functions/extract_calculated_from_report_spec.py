from bs4 import BeautifulSoup
import pandas as pd
import os
from typing import List
from loguru import logger


def extract_calculated_from_report_spec(file_path: str, report_spec: str, analysis: int, var_overview: pd.DataFrame) -> List[str]:
    """Needs a complete rewrite - possibly needs to be expanded as well"""
    logger.debug(f'Started extracted_calculated_from_report_spec from {report_spec}')

    file_name = f'{file_path}{os.path.sep}{report_spec}'
    with open(file_name, 'r') as f:
        file = f.read()

    soup = BeautifulSoup(file, 'lxml-xml')
    questions = soup.find_all('question') + soup.find_all('questionOpenString')
    questions_red = [q for q in questions if q.get('idref') is None and q.get('variableName').startswith('{*3/')]
    # If no calc vars were found, return an empty list
    if not questions_red:
        return []

    data: dict[str: List[str]] = {}
    data['variableName'] = [q.get('variableName') for q in questions_red]
    data['analysisID'] = [q.get('analysisID') for q in questions_red]
    # Converting dict to dataframe # should not be done in pandas
    df_report_vars = pd.DataFrame(data).query(f'analysisID=="{analysis}"')
    df_report_vars['analysis_var_ref'] = df_report_vars['analysisID'] + '_' + df_report_vars['variableName']

    # Merging ajd_name onto the variables
    df_vo_temp = var_overview[['adj_name', 'analysis_var_ref']]
    df_report_vars_calc = pd.merge(left=df_report_vars, right=df_vo_temp, on='analysis_var_ref', how='left')
    rel_vars = df_report_vars_calc['adj_name'].tolist()
    logger.info(f'Done extracting variables from report specification: {file_name}. Identified the following relevant variables: {rel_vars}.')

    return rel_vars
