#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MACD 指数平滑异同移动平均线 (Moving Average Convergence Divergence)
==================================================================

基于 4 小时 K 线计算 MACD(12, 26, 9)。

公式
----
    EMA_fast = EMA(close, fast)
    EMA_slow = EMA(close, slow)
    DIF      = EMA_fast - EMA_slow
    DEA      = EMA(DIF, signal)
    MACD     = (DIF - DEA) * 2        # A 股常用约定，柱状值放大 2 倍

用法
----
    python indicators/macd.py                         # stock NVDA 4h MACD(12,26,9)
    python indicators/macd.py --symbol AAPL --fast 12 --slow 26 --signal 9
    python indicators/macd.py --category commodity --symbol XAU --json
"""

from __future__ import annotations

import pandas as pd

import common


def macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """计算 MACD，返回含 DIF / DEA / MACD 三列的 DataFrame。"""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    hist = (dif - dea) * 2
    return pd.DataFrame({"DIF": dif, "DEA": dea, "MACD": hist})


def compute(df: pd.DataFrame, args) -> pd.DataFrame:
    out = macd(df["close"], args.fast, args.slow, args.signal)
    df[["DIF", "DEA", "MACD"]] = out
    return df


def _add_args(parser) -> None:
    parser.add_argument("--fast", type=int, default=12, help="快线 EMA 周期")
    parser.add_argument("--slow", type=int, default=26, help="慢线 EMA 周期")
    parser.add_argument("--signal", type=int, default=9, help="DEA 信号周期")


if __name__ == "__main__":
    common.run_indicator(
        "MACD 指标 (4h)",
        compute,
        lambda args: ["DIF", "DEA", "MACD"],
        add_args=_add_args,
    )
