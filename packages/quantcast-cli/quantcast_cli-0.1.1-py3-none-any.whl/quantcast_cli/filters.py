from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from functools import reduce, partial

import pandas as pd

from .search import find_first_occurrence, find_last_occurrence, notfound


def filter_by_date(date: str, df: pd.DataFrame) -> pd.DataFrame:
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"The date '{date}' does not match the ISO 8601 format 'YYYY-MM-DD'."
        )

    first = find_first_occurrence(date, df)
    last = find_last_occurrence(date, df)
    if first is notfound or last is notfound:
        return pd.DataFrame(columns=df.columns)

    return df.iloc[first : last + 1]


def calc_session_counts(date: str, df: pd.DataFrame) -> pd.Series:
    return filter_by_date(date, df).groupby("cookie").size()


def _default_reducer(acc, prev):
    return acc + prev


def map_reduce(func, iterable, reducer=_default_reducer):
    with ProcessPoolExecutor() as executor:
        results = [executor.submit(func, chunk) for chunk in iterable]
    if not results:
        return None
    retrieved_results = map(lambda x: x.result(), results)
    reduced_result = reduce(lambda acc, prev: reducer(acc, prev), retrieved_results)
    return reduced_result


def series_reducer(acc, prev):
    return acc.add(prev, fill_value=0)


def find_most_active_cookies(date: str, file, chunk_size: int = 10**6) -> list[str]:
    try:
        chunks = pd.read_csv(file, chunksize=chunk_size)
    except pd.errors.EmptyDataError:
        return []
    counter = partial(calc_session_counts, date)
    counts = map_reduce(counter, chunks, series_reducer)
    max_count: int = counts.max()
    most_active_cookies_series: pd.Series = counts.loc[counts == max_count]
    most_active_cookies: list[str] = most_active_cookies_series.index.tolist()
    return most_active_cookies
