from typing import List, Union, Callable, Dict, Tuple, Iterable
import datetime as dt
from datetime import date, datetime
from multiprocessing import Pool, cpu_count
import logging

import operator

import pandas as pd
import numpy as np

from .unbiasedness import estim_unbiasedness_regs, estim_unbiasedness_windows
from .windows import get_return_windows, resample_windows


def draw_dates(
    dates: pd.DatetimeIndex,
    N: int,
    dates_pool: pd.DatetimeIndex,
) -> List[pd.DatetimeIndex]:
    """Random draw of matched dates from a given range.

    For each date in dates, draw N dates from the range start_date-end_date,
    with replacement, and matching on day of week and quarter.


    Args:
        dates (pd.DatetimeIndex): Initial dates to match
        N (int): Number of random draws
        dates_pool (pd.DatetimeIndex): Dates to draw from

    Returns:
        List[pd.DatetimeIndex]: List of N random draws of matched dates.
    """

    dr_df = pd.DataFrame(index=dates_pool)
    dr_df["day_of_week"] = dr_df.index.day_of_week
    dr_df["quarter"] = dr_df.index.quarter
    dr_df["year"] = dr_df.index.year

    # For each date, sample from dates in the same quarter and the same day of the
    # week.
    draws = []
    for dt in dates:
        draw = (
            dr_df[
                (dr_df.day_of_week == dt.day_of_week)
                & (dr_df.quarter == dt.quarter)
                & (dr_df.year == dt.year)
            ][[]]
            .sample(n=N, replace=True)
            .reset_index()
        )
        draws.append(draw.T)

    return [
        pd.DataFrame(x, columns=["date"]).set_index("date").index
        for x in np.hsplit(pd.concat(draws).values, N)
    ]


def remove_bad_pvals(df: pd.DataFrame) -> pd.DataFrame:
    """Remove values that are not for Excess Delta R2

    Args:
        df (pd.DataFrame): DataFrame with p-values

    Returns:
        pd.DataFrame: DataFrame with p-values only for Excess Delta R2
    """
    df = df.copy()

    for c in df:
        if not c.endswith("Delta_Excess_R2"):
            df[c] = np.nan

    return df


def shuffles_pvals(res: pd.DataFrame, bs: np.ndarray, n_bs: int = 1000):
    res[[c for c in res.columns if c.endswith("Excess_R2")]]
    bs_pvals = pd.DataFrame(
        np.sum(res.values > bs, axis=0) / n_bs,
        index=res.index,
        columns=res.columns,
    )
    bs_pvals[res.isnull()] = np.nan
    return remove_bad_pvals(bs_pvals)


def bootstrap_pvals(
    res: pd.DataFrame,
    bs: np.ndarray,
    oper: Callable = operator.ge,
    bench: float = 0.0,
    n_bs: int = 1000,
):
    bs_pvals = pd.DataFrame(
        np.sum(oper(bs, bench), axis=0) / n_bs,
        index=res.index,
        columns=res.columns,
    )
    bs_pvals[res.isnull()] = np.nan
    return remove_bad_pvals(bs_pvals)


def _swur_wrapper(args):
    np.random.seed()
    returns, dates, windows, periods, n_bs = args
    logging.info(f"One process for {n_bs} samples running.")
    return [
        estim_unbiasedness_regs(
            returns, dates, windows, periods, use_se=False, shuffle=True
        )
        for _ in range(n_bs)
    ]


def shuffle_window_unbiasedness_reg(
    res: pd.DataFrame,
    returns: pd.Series,
    dates: pd.DatetimeIndex,
    windows: Iterable[Tuple[int, int]],
    periods: Iterable[Tuple[int, int]],
    n_bs: int = 1000,
    multiprocessing: Union[bool, int] = False,
):
    if multiprocessing:
        n_proc = multiprocessing if (type(multiprocessing) is int) else cpu_count()
        n_proc = min(n_proc, n_bs)
        tasks = [
            (returns, dates, windows, periods, n_bs // n_proc)
            for _ in range(n_proc - 1)
        ]
        tasks += [
            (returns, dates, windows, periods, n_bs - n_bs // n_proc * (n_proc - 1))
        ]
        logging.info(
            f"Launching {n_proc} processes for {n_bs} samples for window shuffles."
        )

        with Pool(processes=n_proc) as pool:
            x = pool.map(_swur_wrapper, tasks)
        shuffle = []
        for s in x:
            shuffle += s
    else:
        shuffle = [
            estim_unbiasedness_regs(
                returns, dates, windows, periods, use_se=False, shuffle=True
            )
            for _ in range(n_bs)
        ]

    return shuffles_pvals(
        res,
        np.array(shuffle),
        n_bs=n_bs,
    )


def _sdur_wrapper(args):
    np.random.seed()
    returns, dates, windows, periods, returns.index, n_bs = args
    logging.info(f"One process for {n_bs} samples running.")
    return [
        estim_unbiasedness_regs(returns, d, windows, periods, use_se=False)
        for d in draw_dates(dates, n_bs, returns.index)
    ]


def shuffle_dates_unbiasedness_reg(
    res: pd.DataFrame,
    returns: pd.Series,
    dates: pd.DatetimeIndex,
    windows: Iterable[Tuple[int, int]],
    periods: Iterable[Tuple[int, int]],
    n_bs: int = 1000,
    multiprocessing: Union[bool, int] = False,
):
    if multiprocessing:
        n_proc = multiprocessing if (type(multiprocessing) is int) else cpu_count()
        n_proc = min(n_proc, n_bs)
        tasks = [
            (returns, dates, windows, periods, returns.index, n_bs // n_proc)
            for _ in range(n_proc - 1)
        ]
        remainder = n_bs - n_bs // n_proc * (n_proc - 1)
        tasks += [(returns, dates, windows, periods, returns.index, remainder)]
        logging.info(
            f"Launching {n_proc} processes for {n_bs} samples for dates shuffles."
        )

        with Pool(processes=n_proc) as pool:
            x = pool.map(_sdur_wrapper, tasks)
        shuffle = []
        for s in x:
            shuffle += s
    else:
        shuffle = [
            estim_unbiasedness_regs(returns, d, windows, periods, use_se=False)
            for d in draw_dates(dates, n_bs, returns.index)
        ]

    return shuffles_pvals(
        res,
        np.array(shuffle),
        n_bs=n_bs,
    )


def _bur_wrapper(args):
    np.random.seed()
    win_dfs, periods, n_bs = args
    logging.info(f"One process for {n_bs} samples running.")
    return [
        estim_unbiasedness_windows(resample_windows(win_dfs), periods, use_se=False)
        for _ in range(n_bs)
    ]


def bootstrap_unbiasedness_regs(
    res: pd.DataFrame,
    returns: pd.Series,
    dates: pd.DatetimeIndex,
    windows: Iterable[Tuple[int, int]],
    periods: Iterable[Tuple[int, int]],
    n_bs: int = 1000,
    multiprocessing: Union[bool, int] = False,
) -> np.array:
    win_dfs = get_return_windows(returns, dates, windows)

    # Each iteration, resample with replacement
    if multiprocessing:
        bootstrap = compute_bs_pvals_mp(multiprocessing, n_bs, win_dfs, periods)
    else:
        bootstrap = [
            estim_unbiasedness_windows(resample_windows(win_dfs), periods, use_se=False)
            for _ in range(n_bs)
        ]

    return bootstrap_pvals(
        res,
        np.array(bootstrap),
        n_bs=n_bs,
    )


def compute_bs_pvals_mp(
    multiprocessing: Union[bool, int],
    n_bs: int,
    win_dfs: Dict[str, pd.DataFrame],
    periods: Iterable[Tuple[int, int]],
) -> List[pd.DataFrame]:
    n_proc = multiprocessing if (type(multiprocessing) is int) else cpu_count()
    n_proc = min(n_proc, n_bs)
    tasks = [(win_dfs, periods, n_bs // n_proc) for _ in range(n_proc - 1)]
    remainder = n_bs - n_bs // n_proc * (n_proc - 1)
    tasks += [(win_dfs, periods, remainder)]
    logging.info(f"Launching {n_proc} processes for {n_bs} samples for bootstrap.")

    with Pool(processes=n_proc) as pool:
        x = pool.map(_bur_wrapper, tasks)
    result = []
    for s in x:
        result += s
    return result


def estim_unbiasedness_regs_bs(
    returns: pd.Series,
    dates: pd.DatetimeIndex,
    windows: Iterable[Tuple[int, int]],
    periods: Iterable[Tuple[int, int]],
    shuffle_window=False,
    shuffle_dates=False,
    bootstrap=True,
    n_bs=1000,
    multiprocessing: Union[bool, int] = False,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if n_bs <= 0:
        raise ValueError(
            f"The number of boostrap samples (n_bs) should be positive: {n_bs}"
        )

    returns = returns.dropna()

    # Keep only dates that are in the returns
    dates = returns.index.intersection(dates)

    # Estimate unbiasedness regressions
    res = estim_unbiasedness_regs(returns, dates, windows, periods)

    pvals = []
    # Shuffles
    # First shuffle: keep the same dates/windows, but shuffle dates within
    # each window.
    if shuffle_window:
        shuffle_window_vals = shuffle_window_unbiasedness_reg(
            res=res,
            returns=returns,
            dates=dates,
            windows=windows,
            periods=periods,
            n_bs=n_bs,
            multiprocessing=multiprocessing,
        )
        pvals.append(shuffle_window_vals)

    # Second shuffle: draw new dates, matching on year/quarter/day of week
    if shuffle_dates:
        shuffle_dates_vals = shuffle_dates_unbiasedness_reg(
            res=res,
            returns=returns,
            dates=dates,
            windows=windows,
            periods=periods,
            n_bs=n_bs,
            multiprocessing=multiprocessing,
        )
        pvals.append(shuffle_dates_vals)

    # # Bootstrap
    if bootstrap:
        bootstrap_vals = bootstrap_unbiasedness_regs(
            res=res,
            returns=returns,
            dates=dates,
            windows=windows,
            periods=periods,
            n_bs=n_bs,
            multiprocessing=multiprocessing,
        )
        pvals.append(bootstrap_vals)

    return tuple([res] + pvals)
