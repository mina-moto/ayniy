import os

import pandas as pd
from sklearn.model_selection import KFold
import xfeat
from xfeat import (ArithmeticCombinations,
                   LabelEncoder,
                   CountEncoder,
                   ConcatCombination,
                   TargetEncoder)

from ayniy.preprocessing import xfeat_runner


categorical_cols = [
    'Type',
    'Breed1',
    'Breed2',
    'Gender',
    'Color1',
    'Color2',
    'Color3',
    'State',
    'RescuerID'
]

numerical_cols = [
    'Age',
    'Dewormed',
    'Fee',
    'FurLength',
    'Health',
    'MaturitySize',
    'PhotoAmt',
    'Quantity',
    'Sterilized',
    'Vaccinated',
    'VideoAmt'
]

target_col = 'AdoptionSpeed'


def load_petfinder() -> pd.DataFrame:
    filepath = '../input/petfinder-adoption-prediction/train_test.ftr'
    if not os.path.exists(filepath):
        # Convert dataset into feather format.
        train = pd.read_csv('../input/petfinder-adoption-prediction/train/train.csv')
        test = pd.read_csv('../input/petfinder-adoption-prediction/test/test.csv')

        xfeat.utils.compress_df(
            pd.concat([train, test], sort=False)
        ).reset_index(drop=True).to_feather(filepath)

    return pd.read_feather(filepath)


if __name__ == '__main__':

    train = load_petfinder()

    # ArithmeticCombinations
    xfeat_runner(
        pipelines=[
            ArithmeticCombinations(
                drop_origin=True, operator='+', r=2,
            ),
        ],
        input_df=train[numerical_cols],
        output_filename='../input/petfinder-adoption-prediction/ArithmeticCombinations.ftr'
    )

    # LabelEncoder
    xfeat_runner(
        pipelines=[
            LabelEncoder(output_suffix=''),
        ],
        input_df=train[categorical_cols],
        output_filename='../input/petfinder-adoption-prediction/LabelEncoder.ftr'
    )

    # CountEncoder
    xfeat_runner(
        pipelines=[
            LabelEncoder(output_suffix=''),
            CountEncoder(),
        ],
        input_df=train[categorical_cols],
        output_filename='../input/petfinder-adoption-prediction/CountEncoder.ftr'
    )

    # ConcatCombination r=2
    xfeat_runner(
        pipelines=[
            LabelEncoder(output_suffix=''),
            ConcatCombination(drop_origin=True, r=2),
            LabelEncoder(output_suffix=''),
        ],
        input_df=train[categorical_cols],
        output_filename='../input/petfinder-adoption-prediction/ConcatCombinationR2.ftr'
    )

    # ConcatCombination r=2 & CountEncoder
    xfeat_runner(
        pipelines=[
            LabelEncoder(output_suffix=''),
            ConcatCombination(drop_origin=True, r=2),
            CountEncoder(),
        ],
        input_df=train[categorical_cols],
        output_filename='../input/petfinder-adoption-prediction/ConcatCombinationCountEncoder.ftr'
    )

    # TargetEncoder
    xfeat_runner(
        pipelines=[
            TargetEncoder(
                fold=KFold(n_splits=5, shuffle=True, random_state=7),
                target_col=target_col,
            ),
        ],
        input_df=train[categorical_cols + [target_col]],
        output_filename='../input/petfinder-adoption-prediction/TargetEncoder.ftr'
    )
