from loguru import logger
from dataclasses import dataclass
import os
import codecs
import json
import pandas as pd
import numpy as np
from .InputFile import InputFile


@dataclass
class VariableOverview:
    file_name: str

    def __post_init__(self):

        logger.debug(f'Instantiated {self.__class__.__name__} from {self.file_name}')

        if not InputFile(self.file_name).valid():
            raise OSError(f'{self.file_name} is not a valid')

        self.input_path = InputFile(self.file_name).full_path
        self.var_overview = self.__parse_json_file_to_df()
        self.var_map = self.__create_var_map()

    def __create_var_map(self) -> dict[str: str]:
        temp_var_overview = self.var_overview.query(r'referenceType != "TypeChoiceSingle"')
        return dict(zip(temp_var_overview.adj_name.to_list(), temp_var_overview.reference.to_list()))

    def __parse_json_file_to_df(self) -> pd.DataFrame:

        with codecs.open(self.file_name, mode='r', encoding='UTF-8-SIG') as f:
            json_data = json.load(f)

        try:
            df_data = json_data['data']['administrator']['consultant']['bgVariables']
        except KeyError:
            df_data = json_data['data']['administrator']['consultant']['fgVariables']

        # Creating dataframe
        df = pd.DataFrame(df_data)

        # Removing line breaks, carriage returns and tabs from labels
        df['text'] = df.text.replace(to_replace=[r'\\t|\\n|\\r', '\t|\n|\r'], value=[' ', ' '], regex=True)

        # Creating dataframe with choice info
        df_choices = df[df['choiceInfo'].map(lambda d: len(d)) > 0]

        # Creating columns with number of choices
        pd.options.mode.chained_assignment = None
        df_choices['nb_choices'] = df['choiceInfo'].apply(lambda x: len(x))
        pd.options.mode.chained_assignment = 'warn'

        # Creating one row pr. choice
        df_choices = df_choices.explode('choiceInfo').reset_index()

        # Extracting info form concatenated strings
        df_choices['choice_id'] = [d.get('choiceId') if isinstance(d, dict) else '' for d in df_choices['choiceInfo']]
        df_choices['choice_value'] = [d.get('value') if isinstance(d, dict) else '' for d in df_choices['choiceInfo']]
        df_choices['choice_text'] = [d.get('text') if isinstance(d, dict) else '' for d in df_choices['choiceInfo']]

        # Creating full reference which is used to merge choice data onto df
        df_choices['part1'] = df_choices['reference'].str.extract(r'({\*.*)\*}')
        df_choices['fullRef'] = df_choices['part1'] + r':' + df_choices['choice_id'].astype(str) + r'*}'

        df_choices = df_choices[['fullRef', 'choice_value', 'choice_id', 'nb_choices']]

        df = pd.merge(left=df, right=df_choices, how='left', left_on='reference', right_on='fullRef')

        # Creating full variable name (scope/varName)
        df['analysisId'] = df['id'].str.split('_', expand=True)[0]
        df['scopeShort'] = df['id'].str.split('_', expand=True)[1]

        df['choice_value_1'] = df.choice_value.fillna(0).astype(int).astype(str)

        df['name'] = df.name.ffill()
        df['choice_id_adj'] = (df.groupby(['scopeShort', 'name'])['name'].rank(method='first') - 1).astype(int)

        df['fullName'] = np.where(
            (df['referenceType'].str.contains(r'TypeChoiceMultiple')) & (df['nb_choices'] > 1),
            df['scopeShort'] + r'/' + df['name'] + r'_' + df['choice_id_adj'].astype(str),
            df['scopeShort'] + r'/' + df['name']
        )

        df['adj_name'] = df['fullName'].str.replace('/', '__').str.lower()
        df['analysis_var_ref'] = df['analysisId'] + '_' + df['reference']

        df['nb_choices_all'] = df.groupby('adj_name')['nb_choices'].transform('max')
        return df


if __name__ == '__main__':

    os.chdir(r'C:\Users\ctf\pq_data\tilsyn_data')

    print(VariableOverview('1817107.json').var_overview.columns)
