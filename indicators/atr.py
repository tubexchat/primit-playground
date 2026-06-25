#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATR 真实波幅均值 (Average True Range)
=====================================

基于 4 小时 K 线计算 ATR(14)，采用 Wilder 平滑（RMA，alpha = 1/period）。

公式
----
    TR  = max( high - low,
               |high - prev_close|,
               |low  - prev_close| )
    ATR = Wilder 平滑(TR, period)

另外输出 ATR 占收盘价的百分比 ATR_PCT，便于跨标的比较波动性。

用法
----
    python indicators/atr.py                          # ATR(14)
    python indicators/atr.py --symbol AAPL --period 14
    python indicators/atr.py --category commodity --symbol XAU --json
"""

from __future__ import annotations

import pandas as pd

import common


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """计算真实波幅 TR。"""
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return tr


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """计算 ATR 序列（Wilder 平滑）。"""
    tr = true_range(high, low, close)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def compute(df: pd.DataFrame, args) -> pd.DataFrame:
    df["ATR"] = atr(df["high"], df["low"], df["close"], args.period)
    df["ATR_PCT"] = df["ATR"] / df["close"] * 100
    return df


def _add_args(parser) -> None:
    parser.add_argument("--period", type=int, default=14, help="ATR 周期")


if __name__ == "__main__":
    common.run_indicator(
        "ATR 真实波幅均值 (4h)",
        compute,
        lambda args: ["ATR", "ATR_PCT"],
        add_args=_add_args,
    )
