#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StochRSI 随机相对强弱指标 (Stochastic RSI)
==========================================

基于 4 小时 K 线计算 StochRSI(14, 14, 3, 3)。先算 RSI，再对 RSI 做随机指标，
最后做 K / D 平滑。RSI 计算复用 rsi 模块，保持一致。

公式
----
    rsi       = RSI(close, rsi_period)
    stochrsi  = (rsi - min(rsi, stoch_period)) /
                (max(rsi, stoch_period) - min(rsi, stoch_period)) * 100
    K         = SMA(stochrsi, k)
    D         = SMA(K, d)

用法
----
    python indicators/stochrsi.py                     # stock NVDA 4h StochRSI(14,14,3,3)
    python indicators/stochrsi.py --symbol AAPL --rsi-period 14 --stoch-period 14 --k 3 --d 3
    python indicators/stochrsi.py --category index --symbol SPX --json
"""

from __future__ import annotations

import pandas as pd

import common
from rsi import rsi


def stochrsi(
    close: pd.Series,
    rsi_period: int = 14,
    stoch_period: int = 14,
    k: int = 3,
    d: int = 3,
) -> pd.DataFrame:
    """计算 StochRSI，返回含 STOCHRSI / K / D 三列的 DataFrame。"""
    r = rsi(close, rsi_period)
    low = r.rolling(stoch_period).min()
    high = r.rolling(stoch_period).max()
    rng = high - low
    raw = (r - low) / rng * 100
    raw = raw.where(rng != 0, 0.0)  # 区间为 0 时记为 0，避免除零
    k_line = raw.rolling(k).mean()
    d_line = k_line.rolling(d).mean()
    return pd.DataFrame({"STOCHRSI": raw, "K": k_line, "D": d_line})


def compute(df: pd.DataFrame, args) -> pd.DataFrame:
    out = stochrsi(df["close"], args.rsi_period, args.stoch_period, args.k, args.d)
    df[["STOCHRSI", "K", "D"]] = out
    return df


def _add_args(parser) -> None:
    parser.add_argument("--rsi-period", type=int, default=14, help="RSI 周期")
    parser.add_argument("--stoch-period", type=int, default=14, help="随机指标回看周期")
    parser.add_argument("--k", type=int, default=3, help="K 线平滑周期")
    parser.add_argument("--d", type=int, default=3, help="D 线平滑周期")


if __name__ == "__main__":
    common.run_indicator(
        "StochRSI 指标 (4h)",
        compute,
        lambda args: ["STOCHRSI", "K", "D"],
        add_args=_add_args,
    )
