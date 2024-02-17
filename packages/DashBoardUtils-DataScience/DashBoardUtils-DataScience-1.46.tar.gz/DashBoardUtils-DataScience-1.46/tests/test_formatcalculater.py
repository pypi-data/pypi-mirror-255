import pytest

# test formatcalculater
from package.formatcalculator import FormatCalculator, Mitter, Ordring
from typing import Generator


def test_format_df_hash():
    import pandas as pd
    import re

    df = pd.DataFrame(
        {"var1": ["a", "b", "c"], "other_var": [4, 7, 3], "yet_another": [8, 0, 2]}
    )
    dfq = FormatCalculator.hash_df_formats(df)
    tests = re.compile(dfq.iloc[0, 0])
    result = tests.match(df.iloc[0, 0])
    validation = False
    if result:
        validation = True
    assert isinstance(df, pd.DataFrame)
    assert isinstance(dfq, pd.DataFrame)
    assert isinstance(result, re.Match)
    assert len(dfq) == len(df)
    assert dfq.columns.to_list() == df.columns.to_list()
    assert validation


def test_datamiter_column_wise():
    import pandas as pd

    df = pd.DataFrame(
        {"var1": ["a", "b", "c"], "other_var": [4, 7, 3], "yet_another": [8, 0, 2]}
    )
    mitter = FormatCalculator.generate_datamiter(df)
    assert isinstance(mitter, Mitter)
    assert isinstance(df, pd.DataFrame)
    assert isinstance(mitter._df, pd.DataFrame)
    assert isinstance(mitter.dataset, pd.DataFrame)
    assert isinstance(mitter.colhashes, Generator)
    assert len(mitter._df) == 1
    assert len(df) == len(mitter.dataset)
    assert len(df.iloc[:, 0].to_list()) >= len(list(mitter.colhashes)[0][1])


def test_split_all_labels_to_words_with_new_cols():
    import pandas as pd

    df = pd.DataFrame(
        {
            "var1": ["a c", "b w c", "c x"],
            "other_var": [4, 7, 3],
            "yet_another": [8, 0, 2],
        }
    )
    splitdf = FormatCalculator.split_all_labels_to_words_with_new_cols(df, exer=[" "])
    assert len(df.columns.to_list()) < len(splitdf.columns.to_list())
    assert len(df)==len(splitdf)
