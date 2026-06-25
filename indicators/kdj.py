#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KDJ 随机指标 (Stochastic Oscillator KDJ)
========================================

基于 4 小时 K 线计算 KDJ(9, 3, 3)。K、D 采用经典递推（初值 50，权重 2/3 旧值
+ 1/3 新值），J = 3K - 2D。

公式
----
    RSV = (close - LLV(low, n)) / (HHV(high, n) - LLV(low, n)) * 100
    K_t = (m1 - 1)/m1 * K_{t-1} + 1/m1 * RSV_t      (m1=3, 初值 50)
    D_t = (m2 - 1)/m2 * D_{t-1} + 1/m2 * K_t         (m2=3, 初值 50)
    J   = 3K - 2D

用法
----
    python indicators/kdj.py                          # KDJ(9, 3, 3)
    python indicators/kdj.py --symbol AAPL --n 9 --m1 3 --m2 3
    python indicators/kdj.py --category index --symbol SPX --json
"""

from __future__ import annotations

import pandas as pd

import common


def kdj(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    n: int = 9,
    m1: int = 3,
    m2: int = 3,
) -> pd.DataFrame:
    """计算 KDJ，返回含 K / D / J 三列的 DataFrame。"""
    llv = low.rolling(n).min()
    hhv = high.rolling(n).max()
    rng = hhv - llv
    rsv = (close - llv) / rng * 100
    rsv = rsv.where(rng != 0, 0.0).fillna(0.0)

    k_vals, d_vals = [], []
    k_prev, d_prev = 50.0, 50.0
    for r in rsv:
        k_prev = (m1 - 1) / m1 * k_prev + 1 / m1 * r
        d_prev = (m2 - 1) / m2 * d_prev + 1 / m2 * k_prev
        k_vals.append(k_prev)
        d_vals.append(d_prev)

    k = pd.Series(k_vals, index=close.index)
    d = pd.Series(d_vals, index=close.index)
    j = 3 * k - 2 * d
    return pd.DataFrame({"K": k, "D": d, "J": j})


def compute(df: pd.DataFrame, args) -> pd.DataFrame:
    out = kdj(df["high"], df["low"], df["close"], args.n, args.m1, args.m2)
    df[["K", "D", "J"]] = out
    return df


def _add_args(parser) -> None:
    parser.add_argument("--n", type=int, default=9, help="RSV 回看周期")
    parser.add_argument("--m1", type=int, default=3, help="K 平滑系数")
    parser.add_argument("--m2", type=int, default=3, help="D 平滑系数")


if __name__ == "__main__":
    common.run_indicator(
        "KDJ 随机指标 (4h)",
        compute,
        lambda args: ["K", "D", "J"],
        add_args=_add_args,
    )
