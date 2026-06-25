#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MA / EMA 移动平均线 (Simple & Exponential Moving Average)
========================================================

基于 4 小时 K 线计算简单移动平均（SMA）与指数移动平均（EMA）。
默认 SMA 5/20/60、EMA 12/26，可通过 CLI 自定义周期列表。

用法
----
    python indicators/ma.py                           # SMA 5/20/60 + EMA 12/26
    python indicators/ma.py --symbol AAPL --sma 10,30 --ema 12,26
    python indicators/ma.py --category commodity --symbol XAU --json
"""

from __future__ import annotations

import pandas as pd

import common


def moving_averages(
    close: pd.Series,
    sma_windows: list[int],
    ema_spans: list[int],
) -> pd.DataFrame:
    """返回各 SMA / EMA 列组成的 DataFrame。列名形如 MA20、EMA12。"""
    data = {}
    for w in sma_windows:
        data[f"MA{w}"] = close.rolling(w).mean()
    for s in ema_spans:
        data[f"EMA{s}"] = close.ewm(span=s, adjust=False).mean()
    return pd.DataFrame(data, index=close.index)


def _cols(args) -> list[str]:
    return [f"MA{w}" for w in args.sma] + [f"EMA{s}" for s in args.ema]


def compute(df: pd.DataFrame, args) -> pd.DataFrame:
    out = moving_averages(df["close"], args.sma, args.ema)
    for col in out.columns:
        df[col] = out[col]
    return df


def _periods(text: str) -> list[int]:
    return [int(x) for x in text.split(",") if x.strip()]


def _add_args(parser) -> None:
    parser.add_argument(
        "--sma", type=_periods, default=[5, 20, 60], help="SMA 周期列表，逗号分隔"
    )
    parser.add_argument(
        "--ema", type=_periods, default=[12, 26], help="EMA 周期列表，逗号分隔"
    )


if __name__ == "__main__":
    common.run_indicator(
        "MA / EMA 移动平均线 (4h)",
        compute,
        _cols,
        add_args=_add_args,
    )
