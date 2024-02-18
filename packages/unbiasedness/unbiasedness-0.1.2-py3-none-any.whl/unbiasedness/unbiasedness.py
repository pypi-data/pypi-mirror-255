from typing import Tuple, Iterable, Dict

import pandas as pd
import numba as nb

from .numba_jit import compute_unbiasedness_reg_se_jit, compute_unbiasedness_reg_jit

from .windows import get_return_windows, combine_window


def unbiasedness_reg(
    df: pd.DataFrame, use_se: bool = True, include_vr: bool = False
) -> pd.DataFrame:
    """Estimates the betas and R-squared of an unbiasedness regression

    Args:
        df (_type_): DatFrame with columns "t", "CRet", "CRet_End"
        use_se (bool, optional): Include standard errors in the output. Defaults to True.
        include_vr (bool, optional): Include variance ratio in the output. Defaults to False.

    Returns:
        pd.DataFrame: beta coefficients and R-squared associated with each time period
    """
    df = df.copy()
    df["cst"] = 1

    windows = {
        l: (x[["CRet_End"]].values, x[["cst", "CRet"]].values)
        for l, x in df.groupby("t")
    }
    keys = list(windows.keys())

    if not keys:
        return pd.DataFrame(
            columns=["beta", "se", "r2"] if use_se else ["beta", "r2"]
        ).T

    data = nb.typed.List([windows[k] for k in keys])

    if use_se:
        out = pd.DataFrame(
            compute_unbiasedness_reg_se_jit(data),
            columns=keys,
            index=["beta", "se", "r2"],
        ).T
    else:
        out = pd.DataFrame(
            compute_unbiasedness_reg_jit(data), columns=keys, index=["beta", "r2"]
        ).T

    out.index.name = "t"

    if include_vr:
        out["vr"] = df.groupby("t")["CRet"].var() / df.groupby("t")["CRet_End"].var()

    return out


def estim_unbiasedness_windows(
    win_dfs: Dict[str, pd.DataFrame],
    periods: Iterable[Tuple[int, int]],
    use_se: bool = True,
    include_vr: bool = False,
) -> pd.DataFrame:
    regs = {
        w: unbiasedness_reg(win_df, use_se=use_se, include_vr=include_vr)
        for w, win_df in win_dfs.items()
    }
    return pd.DataFrame({w: combine_window(w, regs[w], periods) for w in win_dfs}).T


def estim_unbiasedness_regs(
    returns: pd.Series,
    dates: pd.DatetimeIndex,
    windows: Iterable[Tuple[int, int]],
    periods: Iterable[Tuple[int, int]],
    use_se: bool = False,
    include_vr: bool = False,
    shuffle: bool = False,
) -> pd.DataFrame:
    # Keep only dates that are in the returns
    dates = returns.index.intersection(dates)

    win_dfs = get_return_windows(returns, dates, windows, shuffle=shuffle)
    return estim_unbiasedness_windows(
        win_dfs, periods, use_se=use_se, include_vr=include_vr
    )
