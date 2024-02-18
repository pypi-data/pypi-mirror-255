from typing import Iterable, Union, Callable, Tuple, List, Any, Dict
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd


class TableFileType(Enum):
    LATEX = 1
    MARKDOWN = 2


@dataclass
class TableFormat:
    file_type: TableFileType
    sep: str
    newline: str
    line_start: str
    line_end: str
    empty_col: str
    empty_col_header: str
    footer: str
    col_name_formatter: Callable[Tuple[str, int], str]
    coef_formatter: Callable[[Union[float, np.float64]], str]
    pval_formatter: Callable[[Union[float, np.float64]], str]
    header: Callable[[Union[int, int]], str]
    header_sep: Callable[[Union[int, int]], str]


TEX_EMPTY_COL = " " * 3
MD_EMPTY_COL = " " * 10


def tex_header_sep(nindex: int, col_names_list: List[List[Any]]) -> str:
    i = nindex
    out = ""
    for c in col_names_list:
        out += f"\\cmidrule(lr){'{'}{i+1}-{i+c[1]}{'}'}"
        i += c[1]
    return out + "\n"


latex = TableFormat(
    file_type=TableFileType.LATEX,
    sep=" & ",
    newline="\\\\\n",
    line_start="",
    line_end="",
    empty_col=TEX_EMPTY_COL,
    empty_col_header="{}",
    footer="\\hline\n\\hline\n\\end{tabular}\n",
    col_name_formatter=lambda c, n: "\\multicolumn{" + f"{n}" + "}{c}{" + c + "}"
    if n > 1
    else c,
    coef_formatter=lambda x: TEX_EMPTY_COL if np.isnan(x) else f"{x:0.3f}",
    pval_formatter=lambda x: TEX_EMPTY_COL
    if np.isnan(x)
    else f"\\emph{'{'}{x:0.3f}{'}'}",
    header=lambda nindex, ncols: (
        "\\begin{tabular}{" + "r" * nindex + "c" * ncols + "}\n\\hline\n\\hline\n"
    ),
    header_sep=tex_header_sep,
)

markdown = TableFormat(
    file_type=TableFileType.MARKDOWN,
    sep=" | ",
    newline="\n",
    line_start="| ",
    line_end=" |",
    empty_col=MD_EMPTY_COL,
    empty_col_header=" ",
    footer="\n",
    col_name_formatter=lambda c, n: c + " | " * (n - 1),
    coef_formatter=lambda x: MD_EMPTY_COL if np.isnan(x) else f"{x:10.3f}",
    pval_formatter=lambda x: MD_EMPTY_COL if np.isnan(x) else f"_{x:0.3f}_",
    header=lambda nindex, ncols: "",
    header_sep=lambda nindex, col_names_list: ("|:---" * nindex)
    + "|"
    + "---:|" * sum(x[1] for x in col_names_list)
    + "\n",
)


# Utility function to format windows labels
def win_lbl(w: Tuple[int, int]) -> str:
    return f"$[{w[0]},{w[1]}]$"


# Utility function for maps to keep ordering constant with stack/unstack
def map_ordering(l: List[str]) -> Tuple[Dict[str, int], Dict[int, str]]:
    unique = []
    for x in l:
        if x not in unique:
            unique.append(x)
    return {x: i for i, x in enumerate(unique)}, dict(enumerate(unique))


class UnbiasednessTable:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    @staticmethod
    def _format_index(index: Union[str, Tuple[str]], sep: str) -> Tuple[str, bool]:
        if isinstance(index, str):
            index = (index,)
        return sep.join(index), index[-1] != ""

    @staticmethod
    def _col_names_row(nindex, col_names_list, format: TableFormat):
        cols_headers = [format.empty_col_header] * nindex
        for c, n in col_names_list:
            cols_headers.append(format.col_name_formatter(c, n))
        return format.sep.join(cols_headers) + format.line_end

    @staticmethod
    def _df_to_col_names(cols: Iterable[str]) -> List[List[List[Any]]]:
        out = []
        for i in range(cols.nlevels):
            vals = cols.get_level_values(i)
            col_names_list = []
            for j, v in enumerate(vals):
                if not col_names_list or col_names_list[-1][0] != v:
                    col_names_list.append([v, 1])
                elif (
                    i > 0
                    and cols.get_level_values(0)[j] != cols.get_level_values(0)[j - 1]
                ):
                    col_names_list.append([v, 1])
                else:
                    col_names_list[-1][1] += 1
            out.append(col_names_list)
        return out

    @staticmethod
    def _copy_df_and_rename_cols(df, cols, windows, label):
        df = df[[c for c in cols if c in df.columns]].copy()
        df.columns = pd.MultiIndex.from_tuples(
            zip([label] * len(df.columns), df.columns)
        )
        return df.loc[windows]

    @staticmethod
    def _format_df(df: pd.DataFrame, long: bool = False) -> pd.DataFrame:
        df = df.reset_index().copy()

        sample = "Sample" in df.columns.names

        if long and sample:
            raise NotImplementedError(
                "Long format not implemented for multiple samples"
            )
        elif long:
            # Need to rename periods and windows to keep ordering
            # (stack/unstack will change it)
            win_map, win_map_inv = map_ordering(df.Window.unique())
            df["Window"] = df.Window.map(win_map)
            df = df.set_index(["Window", "Value"]).T.reset_index()
            per_map, per_map_inv = map_ordering(df.Period.unique())
            df["Period"] = df.Period.map(per_map)
            df = df.set_index(["Period", "Metric"]).T

            df = df.unstack(level="Value").stack(level="Metric").T.reset_index()
            df["Period"] = df.Period.map(per_map_inv)
            df = df.set_index(["Period", "Value"])

            df = df.T.reset_index()
            df["Window"] = df.Window.map(win_map_inv)
            df = df.set_index(["Window", "Metric"]).T.reset_index(level=1)

            df = df.reset_index()
            df.loc[df.Value != "1_coef", "Period"] = ""
            df = df.set_index("Period")
        else:
            df.loc[df.Value != "1_coef", "Window"] = ""
            df = df.set_index("Window")
        del df["Value"]
        df.index.names = [""]

        return df

    @staticmethod
    def _build_table(
        df,
        format: TableFormat = latex,
        header=True,
        col_header=True,
        footer=True,
        index=True,
        long=False,
    ):
        # Format df properly and get column names.
        df = UnbiasednessTable._format_df(df, long=long)
        ncols = df.shape[1]
        col_names_list = UnbiasednessTable._df_to_col_names(df.columns)

        nindex = 1 if index else 0

        out = ""
        if header:
            out += format.header(nindex=nindex, ncols=ncols)

        if col_header:
            out += (
                format.line_start
                + UnbiasednessTable._col_names_row(nindex, col_names_list[0], format)
                + format.newline
            )
            out += format.header_sep(nindex, col_names_list[0])
            if len(col_names_list) > 1:
                for c in col_names_list[1:]:
                    out += (
                        format.line_start
                        + UnbiasednessTable._col_names_row(nindex, c, format)
                        + format.newline
                    )

        for r in df.iterrows():
            out += format.line_start
            index_val, is_coef = UnbiasednessTable._format_index(
                index=r[0], sep=format.sep
            )
            if index:
                out += index_val + format.sep

            if is_coef:
                out += format.sep.join([format.coef_formatter(x) for x in r[1]])
            else:
                out += format.sep.join([format.pval_formatter(x) for x in r[1]])

            out += format.line_end + format.newline
        if footer:
            out += format.footer
        elif format.file_type == TableFileType.LATEX:
            # Remove last line ending
            new_end = len(format.line_end + format.newline)
            out = out[:-new_end]
        return out

    def to_latex(
        self,
        fn,
        header: bool = True,
        col_header: bool = True,
        footer: bool = True,
        index: bool = True,
        long: bool = False,
    ):
        with open(fn, "w") as file:
            file.write(
                self._build_table(
                    self.df,
                    format=latex,
                    header=header,
                    col_header=col_header,
                    footer=footer,
                    index=index,
                    long=long,
                )
            )

    def to_markdown(
        self,
        fn,
        header: bool = True,
        col_header: bool = True,
        footer: bool = True,
        index: bool = True,
        long: bool = False,
    ):
        with open(fn, "w") as file:
            file.write(
                self._build_table(
                    self.df,
                    format=markdown,
                    header=header,
                    col_header=col_header,
                    footer=footer,
                    index=index,
                    long=long,
                )
            )

    def _repr_markdown_(self):
        return self._build_table(
            self.df, format=markdown, header=True, footer=True, long=True
        )

    @staticmethod
    def _compile_unbiasedness_regs_df(
        res,
        period_labels,
        windows,
        bs_vals: Iterable[pd.DataFrame] = (),
        add_h0=True,
        excess_only=False,
    ):
        base_cols = ["_Delta_R2", "_Delta_Excess_R2"]
        if excess_only:
            base_cols = ["_Delta_Excess_R2"]
        cols = [x[0] + s for x in period_labels for s in base_cols]

        table_out = (
            pd.concat(
                [
                    UnbiasednessTable._copy_df_and_rename_cols(
                        res, cols, windows, "0_Estim"
                    )
                ]
                + [
                    UnbiasednessTable._copy_df_and_rename_cols(
                        b, cols, windows, f"{i+1}_BS{i+1}"
                    )
                    for i, b in enumerate(bs_vals)
                ],
                axis=1,
            )
            .stack(level=0)[cols]
            .reset_index(level=2, drop=True)
        )

        val_labels = ["1_coef"] + [f"bs{i+1}" for i in range(len(bs_vals))]

        table_out.index = pd.MultiIndex.from_arrays(
            [
                [win_lbl(w) for w in windows for _ in range(len(val_labels))],
                val_labels * len(windows),
            ],
            names=["Window", "Value"],
        )

        table_out.columns = (
            pd.MultiIndex.from_arrays(
                [
                    [p[1] for p in period_labels],
                    ["Excess $\Delta R^2$"] * len(period_labels),
                ],
                names=["Period", "Metric"],
            )
            if excess_only
            else pd.MultiIndex.from_arrays(
                [
                    [p[1] for p in period_labels for _ in (0, 1)],
                    list(["$\Delta R^2$", "Excess $\Delta R^2$"] * len(period_labels)),
                ],
                names=["Period", "Metric"],
            )
        )

        if add_h0:
            table_out.insert(
                0,
                "$H_0$",
                pd.Series({win_lbl(w): 1 / (w[1] - w[0] + 1) for w in windows}),
            )
        return table_out

    @staticmethod
    def from_unbiasedness_regs(
        res,
        period_labels,
        windows,
        bs_vals: Iterable[pd.DataFrame] = (),
        add_h0=True,
        excess_only=False,
    ):
        table_out = UnbiasednessTable._compile_unbiasedness_regs_df(
            res,
            period_labels,
            windows,
            bs_vals=bs_vals,
            add_h0=add_h0,
            excess_only=excess_only,
        )

        return UnbiasednessTable(table_out)

    @staticmethod
    def _compile_subsample_df(subsample_regs, period_labels, windows):
        cols = [x[0] + s for x in period_labels for s in ["_Delta_Excess_R2"]]

        tables_samples = []
        for x in subsample_regs:
            res = subsample_regs[x][0]
            bs_vals = subsample_regs[x][1:]

            val_labels = ["1_coef"] + [f"bs{i+1}" for i in range(len(bs_vals))]
            table_sample = (
                pd.concat(
                    [
                        UnbiasednessTable._copy_df_and_rename_cols(
                            res, cols, windows, "0_Estim"
                        )
                    ]
                    + [
                        UnbiasednessTable._copy_df_and_rename_cols(
                            bs, cols, windows, f"{i+1}_BS{i+1}"
                        )
                        for i, bs in enumerate(bs_vals)
                    ],
                    axis=1,
                )
                .stack(level=0)[cols]
                .reset_index(level=2, drop=True)
            )
            table_sample.index = pd.MultiIndex.from_arrays(
                [
                    [win_lbl(w) for w in windows for _ in range(len(val_labels))],
                    val_labels * len(windows),
                ],
                names=["Window", "Value"],
            )
            tables_samples.append(table_sample)

        table_out = pd.concat(tables_samples, axis=1)

        table_out.columns = pd.MultiIndex.from_arrays(
            [
                [s for s in subsample_regs for _ in range(len(period_labels))],
                ["Excess $\Delta R^2$"] * len(period_labels) * len(subsample_regs),
                [p[1] for p in period_labels] * len(subsample_regs),
            ]
        )
        table_out.columns.names = ["Sample", "Metric", "Period"]

        return table_out

    @staticmethod
    def from_subsample_regs(subsample_regs, period_labels, windows):
        df = UnbiasednessTable._compile_subsample_df(
            subsample_regs, period_labels, windows
        )

        return UnbiasednessTable(df=df)
