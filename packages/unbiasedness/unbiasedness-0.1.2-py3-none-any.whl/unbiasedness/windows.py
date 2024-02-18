from typing import Tuple, Iterable, Dict, Union
from collections import ChainMap

import pandas as pd
import numpy as np


def resample_windows(
    win_df: Dict[Tuple[int, int] | str, pd.DataFrame]
) -> Dict[Tuple[int, int] | str, pd.DataFrame]:
    """Resample observations with replacement.

    Args:
        win_df (Dict[Tuple[int, int], pd.DataFrame]): Dictionnary of dataframes with observations
        for each window.

    Returns:
        pd.DataFrame: Resampled observations.

    We assume that each dataframe has the same event dates. Each dataframe contains
    observations for a given window for multiple events. We resample with replacement
    by event date, i.e. we pick random event dates, and then pick all observations
    for those event dates. To avoid issues with duplicate event dates, we replace
    the resampled event dates with a simple index.

    The event dates are assumed to be in the column `index`.
    """
    if not win_df:
        raise ValueError("win_df is empty")

    try:
        first_key = next(iter(win_df))
        if type(win_df[first_key]) is not pd.DataFrame:
            raise ValueError("win_df must be a dictionary of dataframes")
        dates = win_df[first_key]["index"].unique()
    except AttributeError as e:
        raise ValueError("win_df must be a dictionary of dataframes") from e

    # Sample index with replacement
    dates = np.random.choice(dates, size=len(dates), replace=True)

    # Resample each dataframe
    return {k: v.set_index("index").loc[dates].reset_index() for k, v in win_df.items()}


def shuffle_window(
    df: pd.DataFrame, group_col: str = "index", shuffle_col: str = "ret"
) -> pd.Series:
    """Shuffle a column within groups.

    Args:
        df (pd.DataFrame): Dataframe with a column to shuffle.
        group_col (str, optional): Column to group by. Defaults to "index".
        shuffle_col (str, optional): Column to shuffle. Defaults to "ret".

    Returns:
        pd.Series: Shuffled column
    """
    idx = df.index
    s_out = df.groupby(group_col)[shuffle_col].sample(frac=1, replace=False)
    s_out.index = idx
    return s_out


def combine_return_windows(
    df: pd.DataFrame, windows: Iterable[Tuple[int, int]]
) -> Dict[Tuple[int, int], pd.DataFrame]:
    """Combines the returns in the windows into a single cumulative returns series

    Args:
        df (pd.DataFrame): DataFrame with columns "t", "ret", "index"
        windows (Iterable[Tuple[int, int]]): List of tuples with the start and end of each window

    Returns:
        Dict[Tuple[int, int], pd.DataFrame]: Augmented DataFrame for each window


    Output DataFrames have original columns plus "CRet" and "CRet_End".
    """
    df = df.sort_values(["index", "t"])
    out = {w: df[(df["t"] >= w[0]) & (df["t"] <= w[1])].copy() for w in windows}
    for w in out:
        out[w]["CRet"] = out[w].groupby("index")["ret"].cumsum()
        out[w]["CRet_End"] = out[w].groupby("index")["CRet"].transform("last")
        out[w] = out[w].reset_index(drop=True)

    return out


def merge_events_returns(
    returns: pd.Series, events: pd.DatetimeIndex, windows: Iterable[Tuple[int, int]]
) -> pd.DataFrame:
    """Merges the returns and events into a single DataFrame

    Args:
        returns (pd.Series): Series of returns
        events (pd.DatetimeIndex): DatetimeIndex of events

    Returns:
        pd.DataFrame: DataFrame with columns "t", "ret", "date_evt", and "date_t"
    """
    min_start = min(window[0] for window in windows)
    max_end = max(window[1] for window in windows)

    # Create longest possible window first
    returns_df = pd.DataFrame(returns)
    returns_df.columns = ["ret"]
    returns_df.index.name = "date"
    returns_df["date_t"] = pd.Series(range(len(returns)), index=returns.index)

    evt_dates_df = returns_df.loc[returns_df.index.intersection(events), ["date_t"]]
    evt_dates_df.index.name = "date"

    window_ts = pd.DataFrame({"t": range(min_start, max_end + 1)})

    evt_win_df = (
        evt_dates_df.assign(key=1)
        .reset_index()
        .merge(window_ts.assign(key=1), on="key")
        .drop(columns="key")
        .set_index("date")
    )
    evt_win_df["date_t"] = evt_win_df["date_t"] + evt_win_df["t"]

    win_df = pd.merge(
        evt_win_df.reset_index(),
        returns_df.reset_index()[["date", "date_t", "ret"]],
        on="date_t",
        suffixes=("_evt", "_obs"),
    )
    del win_df["date_t"]
    return win_df


def get_return_windows(
    returns: pd.Series,
    events: pd.DatetimeIndex,
    windows: Iterable[Tuple[int, int]],
    shuffle: bool = False,
) -> Dict[Tuple[int, int], pd.DataFrame]:
    """
    Computes return windows around a set of events.

    Args:
        returns: A pandas series of returns.
        events: A pandas datetime index of event dates.
        windows: An iterable of tuples representing the start and end offsets (in days)
        for each window.
            The start offset can be negative to indicate a window that starts before the
            event date.
            The end offset can be 'T1' to indicate a window that ends at the next event
            date.
        shuffle: Whether to shuffle the returns within each window for bootstrap, by
        default False.

    Returns:
        A dictionary of dataframes, where each key is a tuple representing the start and
        end offsets
        for a window, and each value is a dataframe containing the returns within that
        window for each event.
        The dataframes have the following columns:
            - t: The offset from the event date
            - ret: The return at that offset
            - index: The event date or resample id if resampling
            - date_obs: The date of the return
            - "CRet": The cumulative return at that offset
            - "CRet_End": The cumulative return at the end of the window
    """
    win_df = merge_events_returns(returns, events, windows)

    # Shuffle window for bootstrap
    if shuffle:
        win_df["ret"] = shuffle_window(win_df, group_col="index", shuffle_col="ret")

    win_df = win_df.rename(columns={"date_evt": "index"})

    return combine_return_windows(win_df, windows)


def period_prefix(p: Tuple[Union[int, str], int]) -> str:
    """Generate a prefix for a period.

    Args:
        p (Tuple[Union[int, str], int]): Period start and end.

    Returns:
        str: Prefix for the period.
    """
    p_label = f"p{p[0]}_p{p[1]}" if p[0] != p[1] else f"p{p[0]}"
    return p_label.replace("p-", "m").replace("pT1", "T1").replace("p0", "0")


def combine_period(
    period: Tuple[Union[int, str], int],
    window: Tuple[int, int],
    df: pd.DataFrame,
) -> Dict[str, float]:
    """Combines unbiasedness results for a specific period.

    Args:
        period (Tuple[Union[int, str], int]]): Start and end of the period.
        window (Tuple[int, int]]): Start and end of the window.
        df (pd.DataFrame): Unbiasedness regression results for the window.

    Returns:
        Dict[str, float]: Combined unbiasedness results for the period.

    Unbiasedness regression results are dataframes with columns "bench", "d_r2",
    "d_r2_excess" and index corresponding to an event time t.
    """

    p_label = period_prefix(period)

    t1 = window[0]
    t2 = window[1]

    if type(period[0]) == int:
        start = period[0]
    elif period[0] == "T1":
        start = int(df.index[0])
    else:
        raise ValueError(f"Invalid period start: {period[0]}")
    end = period[1]

    if (start < t1) or (end > t2):
        return {
            f"{p_label}_Delta_R2": np.nan,
            f"{p_label}_Delta_Excess_R2": np.nan,
            f"{p_label}_Benchmark": np.nan,
        }

    bench = df.loc[start:end, "bench"].sum()

    out = {
        f"{p_label}_Delta_R2": (d_r2 := df.loc[start:end, "d_r2"].sum()),
        f"{p_label}_Delta_Excess_R2": (d_r2 - bench) / bench,
        f"{p_label}_Benchmark": bench,
    }

    if start != end:
        return out

    return {
        f"{p_label}_R2": float(df.loc[start, "r2"]),
        f"{p_label}_Beta": float(df.loc[start, "beta"]),
        f"{p_label}_SE": float(df.loc[start, "se"]) if "se" in df else np.nan,
        f"{p_label}_VR": float(df.loc[start, "vr"]) if "vr" in df else np.nan,
    } | out


def combine_window(
    window: Tuple[int, int], reg: pd.DataFrame, periods: Iterable[Tuple[int, int]]
) -> Dict[str, float]:
    """
    Combine unbiasedness results for a given window and set of periods.

    Args:
        window (Tuple[int, int]): The start and end times of the window.
        reg (pd.DataFrame): Unbiasedness results for the window.
        periods (Iterable[Tuple[int, int]]): The start and end times of the periods.

    Returns:
        Dict[str, float]: Combined unbiasedness results for the window and periods.

    The `reg` dataframe should have columns "r2", "beta", and index corresponding
    to an event time t. "se", "vr" are optional columns. The function computes the
    unbiasedness results for each period and combines them into a dictionary with keys
    corresponding to the period and window.
    """
    df = reg.copy()
    df["d_r2"] = df["r2"].diff()
    df["d_r2"].iat[0] = df["r2"].iat[0]
    df["bench"] = 1 / len(df)
    df["cumbench"] = df["bench"].cumsum()

    return dict(ChainMap(*[combine_period(p, window, df) for p in periods]))
