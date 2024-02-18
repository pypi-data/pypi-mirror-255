from loguru import logger
from typing import List
import pandas as pd


def reduce_columns_based_on_input(df: pd.DataFrame, relevant_scopes: List[str] = [], relevant_variables: List[str] = []) -> pd.DataFrame:

    def validate_inputs(existing_columns: List[str],
                        relevant_scopes: List[str],
                        relevant_variables: List[str] = []) -> None:

        nb_cols_with_scope = [col for scope in relevant_scopes for col in existing_columns if col.startswith(scope)]
        if len(nb_cols_with_scope) == 0:
            logger.warning(f'No columns were found starting with {relevant_scopes}. This indicates an error in the specification of relevant_scopes')

        if relevant_variables:
            missing_vars = [var for var in relevant_variables if var not in existing_columns]
            if missing_vars:
                logger.warning(f'The following variables was not found in dataset: {missing_vars} This indicates an error in the specification of relevant_variables')

        return None

    logger.debug('Started reduce_columns_based_on_input')

    validate_inputs(df.columns, relevant_scopes, relevant_variables)

    # Only select the variable scopes defined in relevant_scopes
    relevant_cols: List[str] = [col for col in df.columns for scope in relevant_scopes if col.startswith(scope)]

    # Appending individual variables
    if relevant_variables:
        relevant_cols.extend(relevant_variables)

    # Reducing number of columns in dataframe
    df = df[[col for col in df.columns if col in relevant_cols]]

    return df
