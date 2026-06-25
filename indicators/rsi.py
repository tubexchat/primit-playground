#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSI 相对强弱指标 (Relative Strength Index)
==========================================

基于 4 小时 K 线计算 RSI，采用 Wilder 平滑（RMA，alpha = 1/period）。

公式
----
    delta     = close.diff()
    gain      = max(delta, 0)
    loss      = max(-delta, 0)
    avg_gain  = Wilder 平滑(gain, period)
    avg_loss  = Wilder 平滑(loss, period)
    RS        = avg_gain / avg_loss
    RSI       = 100 - 100 / (1 + RS)

用法
----
    python indicators/rsi.py                          # stock NVDA 4h RSI(14)
    python indicators/rsi.py --symbol AAPL --period 14
    python indicators/rsi.py --category commodity --symbol XAU --json
"""

from __future__ import annotations

import pandas as pd

import common


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """计算 RSI 序列（Wilder 平滑）。供 stochrsi 等模块复用。"""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    # Wilder 平滑等价于 alpha = 1/period 的 EWM（adjust=False）
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss
    out = 100 - 100 / (1 + rs)
    # avg_loss 为 0（持续上涨）时 RSI 记为 100
    out = out.where(avg_loss != 0, 100.0)
    return out


def compute(df: pd.DataFrame, args) -> pd.DataFrame:
    df["RSI"] = rsi(df["close"], args.period)
    return df


def _add_args(parser) -> None:
    parser.add_argument("--period", type=int, default=14, help="RSI 周期")


if __name__ == "__main__":
    common.run_indicator(
        "RSI 相对强弱指标 (4h)",
        compute,
        lambda args: ["RSI"],
        add_args=_add_args,
    )
