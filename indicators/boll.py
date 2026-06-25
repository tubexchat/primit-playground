#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOLL 布林带 (Bollinger Bands)
=============================

基于 4 小时 K 线计算布林带(20, 2)。中轨为 SMA，上下轨为中轨 ± n 倍标准差
（采用总体标准差 ddof=0，符合常见约定）。

公式
----
    MID = SMA(close, period)
    STD = STD(close, period, ddof=0)
    UP  = MID + mult * STD
    LOW = MID - mult * STD

用法
----
    python indicators/boll.py                         # BOLL(20, 2)
    python indicators/boll.py --symbol AAPL --period 20 --mult 2
    python indicators/boll.py --category commodity --symbol XAU --json
"""

from __future__ import annotations

import pandas as pd

import common


def bollinger(close: pd.Series, period: int = 20, mult: float = 2.0) -> pd.DataFrame:
    """计算布林带，返回含 BOLL_MID / BOLL_UP / BOLL_LOW 三列的 DataFrame。"""
    mid = close.rolling(period).mean()
    std = close.rolling(period).std(ddof=0)
    up = mid + mult * std
    low = mid - mult * std
    return pd.DataFrame({"BOLL_MID": mid, "BOLL_UP": up, "BOLL_LOW": low})


def compute(df: pd.DataFrame, args) -> pd.DataFrame:
    out = bollinger(df["close"], args.period, args.mult)
    df[["BOLL_MID", "BOLL_UP", "BOLL_LOW"]] = out
    return df


def _add_args(parser) -> None:
    parser.add_argument("--period", type=int, default=20, help="布林带周期")
    parser.add_argument("--mult", type=float, default=2.0, help="标准差倍数")


if __name__ == "__main__":
    common.run_indicator(
        "BOLL 布林带 (4h)",
        compute,
        lambda args: ["BOLL_MID", "BOLL_UP", "BOLL_LOW"],
        add_args=_add_args,
    )
