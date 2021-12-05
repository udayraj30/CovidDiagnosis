import logging
import math
import os
import re

import numpy as np
import pandas as pd

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import seaborn as sns

from scipy import stats
from typing import List

plt.style.use('fivethirtyeight')

logging.getLogger().setLevel('INFO')

PATH = 'data'

LABEL = 'covid19_test_results'
LABEL_VALUES = ['Negative', 'Positive',]

SYMPTOMS = [
    'labored_respiration',
    'rhonchi',
    'wheezes',
    'cough',
    'cough_severity',
    'loss_of_smell',
    'loss_of_taste',
    'runny_nose',
    'muscle_sore',
    'sore_throat',
    'fever',
    'sob', 
    'sob_severity', 
    'diarrhea', 
    'fatigue', 
    'headache',
    'ctab',
    'days_since_symptom_onset',
]

VITALS = [
    'temperature', 
    'pulse', 
    'sys', 
    'dia', 
    'rr',
    'sats', 
]

COMORBIDITIES = [
    'diabetes', 
    'chd', 
    'htn', 
    'cancer', 
    'asthma',
    'copd', 
    'autoimmune_dis',
    'smoker',
]

RISKS = [
    'age',
    'high_risk_exposure_occupation',
    'high_risk_interactions',
]

TEST_RESULTS = [ 
    'batch_date',
    LABEL,
    'rapid_flu_results', 
    'rapid_strep_results', 
    'swab_type', 
    'test_name', 
]

CXR_FIELDS = [
    'cxr_findings', 'cxr_impression', 'cxr_label', 'cxr_link',
]


def open_data() -> pd.DataFrame:
    '''Open all data in `PATH`.
    
    Returns
    -------
    pandas.DataFrame
    '''    
    return pd.concat(
        [
            pd.read_csv(f'{PATH}/{filename}') 
            for filename in os.listdir(PATH) 
            if filename.endswith('.csv')
        ]
    )


def get_percent(x: int, total: int) -> float:
    '''Return percentage.

    Returns 0 if `total` == 0 to bypass `division by 0` error. 

    Parameters
    ----------
    x : int
        The numerator.
    total : int
        The denominator.

    Returns
    -------
    float
    '''
    if total == 0:
        logging.info(f'Returning 0 to avoid `division by 0` error.')
        return 0

    return (x / total) * 100



def filter_pos(data: pd.DataFrame) -> pd.DataFrame:
    '''Filter data on cases where `LABEL` column is 'Positive'.

    Parameters
    ----------
    data : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
    '''
    return data[data[LABEL] == 'Positive']


def filter_patients(
    df: pd.DataFrame, cols_to_check: List[str], col_type: str='bool'
) -> pd.DataFrame:
    '''Filter data if `cols_to_check` values are present in the data.

    `cols` can be `SYMPTOMS`, `VITALS`, or any other list of features.

    Expample: detects asymptomatic patients by checking where there are no `True` 
    in `SYMPTOMS` columns. Confirm that a `True` indicates a symptom or 
    abnormality. If not, use `reverse_bool` function to flip True/False values.

    Parameters
    ----------
    df : pandas.DataFrame
    cols : List[str]
    col_type : str, default='bool'
        Either `bool` (if columns are boolean columns) or `numeric` (if columns 
        are ints or floats).

    Returns
    -------
    df : pandas.DataFrame
    '''
    logging.info('Filtering out patients...')

    if col_type == 'bool':
        f = is_any_true
    elif col_type == 'numeric':
        f = is_any_nonnull
    else:
        logging.info('ERROR: `col_type` should be either `bool` or `numeric`.')
        return None

    df_filtered = df[df.apply(lambda x: f(x, cols_to_check), axis=1)]
    logging.info(
      f'    ---- {len(df)} --> {len(df_filtered)} '
      f'({get_percent(len(df_filtered), len(df)):.2f}%)'
    )

    return df_filtered


def is_any_true(row: pd.Series, cols: List[str]) -> bool:
    '''Check whether rows exhibit True for any values in `cols`.

    Parameters
    ----------
    row : pandas.Series
        pandas.DataFrame Row 
    cols : List[str]
        Columns to look through (can be `symptoms`, `vitals`, etc.)

    Returns
    -------
    bool
    '''
    return any(row[col] == True for col in cols)


def is_any_nonnull(row: pd.Series, cols: List[str]) -> bool:
    '''Check whether there is at least one non-empty value in `cols`.

    Parameters
    ----------
    row : pandas.Series
        pandas.DataFrame Row 
    cols : List[str]
        Columns to look through (can be `symptoms`, `vitals`, etc.)

    Returns
    -------
    bool
    '''
    return any(not math.isnan(row[col]) for col in cols)



def print_data_info(data: pd.DataFrame):
    '''Print out information on columns containing only one unique value.

    Parameters
    ----------
    data : pandas.DataFrame
    '''
    for col in data.columns:
        if len(data[col].unique()) == 1:
            logging.info(
                f'`{col}` only has single unique value of {data[col].iloc[0]} '
                'in entire dataset.'
            )



LABELS = [
    'Test Results',
    'Epi Factors',
    'Comorbidities',  
    'Vitals', 
    'Symptoms', 
    'Radiological Findings', 
    'Other'
]

COLOR_PALETTE = sns.color_palette('husl', len(LABELS))
COLOR_PALETTE[-1] = 'gray'


def add_legend():
    '''Add legend describing color definitions for `fill_rate` plot.
    '''
    mappings = {
        label: COLOR_PALETTE[i] for i, label in enumerate(LABELS)
    }
    
    patches = [
        mpatches.Patch(color=color, label=label) 
        for label, color in mappings.items()
    ]
    
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1))

    
def get_color(col: str) -> str:
    '''Get color for plot. 

    Different color depending on category of feature (`gray` if color doesn't 
    belong in any of the pre-defined categories).

    Parameters
    ----------
    col : str
      The column name.

    Returns
    -------
    str
      `matplotlib` named color.     
    '''
    if col in TEST_RESULTS:
        return COLOR_PALETTE[0]
    if col in RISKS:
        return COLOR_PALETTE[1]
    if col in COMORBIDITIES:
        return COLOR_PALETTE[2]
    if col in VITALS:
        return COLOR_PALETTE[3]
    if col in SYMPTOMS:
        return COLOR_PALETTE[4]
    if col in CXR_FIELDS:
        return COLOR_PALETTE[5]
    return 'gray'


def plot_fill_rates(data: pd.DataFrame, title: str=''):
    '''Plot fill rates of all the columns in the data.

    Parameters
    ----------
    data : pd.DataFrame
        The data.
    title : str, default=''
        The title for the plot. Empty string if no title.
    '''
    total = len(data)
    cols = data.columns

    _, ax = plt.subplots(figsize=(7, 15), facecolor='white')
    ax.set_facecolor('white')

    x = range(len(cols))
    y = [sum(~data[col].isnull()) / total for col in cols]
    colors = [get_color(col) for col in cols]

    sns.barplot(y, list(x), palette=colors, orient='h',)
        
    plt.xlabel('Fill Rate')
    plt.yticks(x, cols,)
    plt.title(title)
    add_legend()
    plt.show()


ABNORMALITIES = [
    r'.+(lobe|RML|peribronchial|basilar) infiltrate',
    'lobe scarring or atelectasis',
    r'(perihilar|Trace).+opacity',
    'Peribronchial thickeneing', 
    'Left lower lobe consolidation',
    r'Consolidation in the.+lung',
    r'(?<!No )(Multifocal|lung|pulmonary).+opacities',
    'left pulmonary nodules',
    r'(?<!no ) opacity',
    r'.?(left|Left) lung base',
    r'(Subtle left basilar|mass-like spiculated) density',
    'basilar atelectasis or scarring',
    'Elevated right hemidiaphragm',
    '(right hilar|septal) prominence',
]

NO_ABNORMALITIES = [
    r'No.+(acute|significant|definite|suspicious).+(abnormality|disease|opacities)',
    'Normal',
    'No pulmonary opacities visualized',
    'No evidence of acute cardiopulmonary disease',
    'No lobar consolidation',
]


def is_abnormal_cxr(cxr_imp: str) -> bool:
    '''Check whether xray scan is abnormal according to xray notes.

    NOTE: Returns `None` if unclear.

    Parameters
    ----------
    cxr_imp : str

    Returns
    -------
    bool 
    '''
    if any(re.search(x, cxr_imp) for x in NO_ABNORMALITIES):
        return False
    if any(re.search(x, cxr_imp) for x in ABNORMALITIES):
        return True
    return None


SEVERITY_MAPPINGS = {
    'Mild': 1,
    'Moderate': 2,
    'Severe': 3,
}


def get_sym_severity_score(row: pd.Series) -> int:
    '''Calculate score based on severity of symptoms.

    Score ranges from low severity (0) to high severity (7). Score of -1 means 
    no symptoms. The score is calculated from the `cough_severity`, 
    `sob_severity`, and `fever` columns.
    
    Parameters
    ----------
    row : pandas.Series
        pandas.DataFrame Row 

    Returns
    -------
    int 
        Returns a score between -1 and 7.
    '''
    if row['num_symptoms'] == 0:
        return -1
    
    return (
        SEVERITY_MAPPINGS.get(row['cough_severity'], 0) + 
        SEVERITY_MAPPINGS.get(row['sob_severity'], 0) + 
        (row['fever'] == True)
    )
   

def get_sym_severity(score: int) -> str:
    '''Get symptom severity bucket from severity score.

    Asymptomatic -- has no symptoms.
    Extremely Mild -- has symptoms, but no cough, no sob, and no fever.
    Mild -- has either a mild cough, mild sob, or fever at some point.
    Moderate -- has either a moderate cough, moderate sob, high grade fever up 
        to the time of testing, or at least two mild symptoms (mild cough, mild 
        sob, or fever that didn't last up to testing).
    Severe -- severe cough or sever sob, or some combination of symptoms that 
        add up to more than the threshold for Moderate.

    Parameters
    ----------
    score : int
        The symptom severity score, ranging from -1 to 7.
    
    Returns
    -------
    str
        Returns symptom severity description.
    '''
    if score < 0:
        return 'Asymptomatic'
    if score < 1:
        return 'Extremely Mild'
    if score < 2:
        return 'Mild'
    if score < 3:
        return 'Moderate'
    else:
        return 'Severe'
