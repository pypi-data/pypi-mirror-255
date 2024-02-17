from numbers import Number
from typing import Tuple

import pandas as pd


def normalize(x: Number, x_min: Number, x_max: Number) -> Number:
    x -= x_min
    x /= x_max - x_min
    return x


def normalize_field(df: pd.DataFrame, field: str) -> pd.DataFrame:
    min_x, max_x = min(df[field]), max(df[field])
    df.loc[:, field] = df[field].transform(lambda x: normalize(x, min_x, max_x))
    return df


def normalize_field_and_yield_min_max(
    df: pd.DataFrame, field: str
) -> Tuple[pd.DataFrame, Number, Number]:
    df = df.copy()
    min_x, max_x = min(df[field]), max(df[field])
    df.loc[:, field] = df[field].transform(lambda x: normalize(x, min_x, max_x))
    return df, min_x, max_x
