#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标公共模块 (Indicators Common)
====================================

为 indicators/ 下各指标脚本提供统一的：
  1. 4 小时（及其它周期）K 线抓取，并转换为 pandas DataFrame；
  2. 共享命令行参数解析；
  3. 统一的输出（完整序列 + 最新值摘要）。

所有指标脚本都基于本模块取数，避免重复抓取代码。

数据接口
--------
    GET https://api.pipai.org/<category>/v1/klines
    鉴权头：X-Primit-API-Key（密钥取自项目根目录 .env 的 APIKEY）

    category 与接口路径映射（注意接口路径多为单数）：
        stock      -> /stock/v1/klines
        index      -> /index/v1/klines
        commodity  -> /commodity/v1/klines
    crypto 没有专门的接口路径：整套 API 实为 Binance U 本位合约
    (fapi.binance.com, <symbol>USDT) 的代理，加密货币在任一品类接口上都能
    pass-through 取到相同数据，故 crypto 复用其中一个已确认路径即可。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
API_HOST = "https://api.pipai.org"
API_KEY_HEADER = "X-Primit-API-Key"
VALID_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"}

# category -> 接口路径片段（接口路径多为单数）。
# crypto 无独立路径：API 是 Binance <symbol>USDT 合约的代理，加密货币在任一
# 品类接口上 pass-through 返回相同数据，这里复用 stock 路径即可。
CATEGORY_PATHS = {
    "stock": "stock",
    "index": "index",
    "commodity": "commodity",
    "crypto": "stock",
}

# 接口返回 Binance 风格二维数组的字段顺序
KLINE_FIELDS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "trade_count",
    "taker_buy_base",
    "taker_buy_quote",
    "ignore",
]
_NUMERIC_COLS = [
    "open", "high", "low", "close", "volume",
    "quote_volume", "taker_buy_base", "taker_buy_quote",
]


def load_api_key() -> str:
    """从项目根目录 .env 读取 APIKEY。"""
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
    api_key = os.getenv("APIKEY")
    if not api_key:
        sys.exit("错误：未在 .env 中找到 APIKEY，请先配置 API 密钥。")
    return api_key


def fetch_df(
    category: str,
    symbol: str,
    interval: str = "4h",
    limit: int = 300,
    *,
    api_key: str | None = None,
    timeout: int = 30,
) -> pd.DataFrame:
    """
    抓取指定品类 / 标的的 K 线并返回 DataFrame。

    返回的 DataFrame：
      - 以开盘时间（datetime, UTC）为索引；
      - 数值列（open/high/low/close/volume...）已转为 float；
      - 按时间升序。
    """
    if category not in CATEGORY_PATHS:
        raise ValueError(
            f"未知 category：{category!r}，可选：{sorted(CATEGORY_PATHS)}"
        )
    if interval not in VALID_INTERVALS:
        raise ValueError(
            f"interval 非法：{interval!r}，可选值：{sorted(VALID_INTERVALS)}"
        )

    if api_key is None:
        api_key = load_api_key()

    url = f"{API_HOST}/{CATEGORY_PATHS[category]}/v1/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    resp = requests.get(
        url, params=params, headers={API_KEY_HEADER: api_key}, timeout=timeout
    )
    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise RuntimeError(f"请求失败 [HTTP {resp.status_code}]: {detail}")

    rows = resp.json()
    if not rows:
        raise RuntimeError(f"接口返回空数据：{category}/{symbol} {interval}")

    df = pd.DataFrame(rows, columns=KLINE_FIELDS)
    for col in _NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)
    df = df.set_index("open_time").sort_index()
    return df


def build_parser(description: str) -> argparse.ArgumentParser:
    """构造各指标脚本共享的命令行参数解析器（可在 main 中追加指标专属参数）。"""
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--category",
        default="stock",
        choices=sorted(CATEGORY_PATHS),
        help="品类",
    )
    parser.add_argument("--symbol", default="NVDA", help="标的代码，例如 NVDA")
    parser.add_argument(
        "--interval",
        default="4h",
        choices=sorted(VALID_INTERVALS),
        help="K 线周期（默认 4 小时）",
    )
    parser.add_argument("--limit", type=int, default=300, help="抓取的 K 线数量")
    parser.add_argument(
        "--tail",
        type=int,
        default=20,
        help="完整序列只显示最后 N 行（0 表示全部）",
    )
    parser.add_argument(
        "--json", action="store_true", help="以 JSON records 输出（默认表格）"
    )
    return parser


def emit(
    df: pd.DataFrame,
    value_cols: list[str],
    *,
    args: argparse.Namespace,
    decimals: int = 4,
) -> None:
    """
    统一输出：
      - stdout：完整序列（time + close + 指标列），表格或 JSON；
      - stderr：最新一根 K 线的各指标值摘要。
    """
    cols = ["close"] + value_cols
    out = df[cols].copy()
    out[cols] = out[cols].round(decimals)

    if getattr(args, "tail", 0):
        out = out.tail(args.tail)

    # 最新值摘要 -> stderr
    latest = df.iloc[-1]
    ts = df.index[-1].strftime("%Y-%m-%d %H:%M")
    head = f"# {args.category}/{args.symbol} {args.interval} | 最新 {ts} (UTC) | close={latest['close']:.4f}"
    summary = "  ".join(f"{c}={latest[c]:.4f}" for c in value_cols if pd.notna(latest[c]))
    print(head, file=sys.stderr)
    print("  " + summary, file=sys.stderr)

    # 完整序列 -> stdout
    if args.json:
        records = out.reset_index()
        records["open_time"] = records["open_time"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        print(json.dumps(records.to_dict("records"), ensure_ascii=False, indent=2))
    else:
        print(out.to_string())


def run_indicator(description: str, compute, value_cols, *, add_args=None) -> None:
    """
    各指标脚本 main() 的统一执行框架：
      解析参数 -> 抓 4h 数据 -> compute(df, args) 追加指标列 -> emit。

    参数
    ----
    compute     函数 (df, args) -> df，追加指标列后返回。
    value_cols  函数 (args) -> list[str]，返回要展示的指标列名。
    add_args    可选，函数 (parser) -> None，用于追加指标专属参数。
    """
    parser = build_parser(description)
    if add_args is not None:
        add_args(parser)
    args = parser.parse_args()

    try:
        df = fetch_df(args.category, args.symbol, args.interval, args.limit)
        df = compute(df, args)
    except (RuntimeError, ValueError) as exc:
        sys.exit(f"错误：{exc}")

    emit(df, value_cols(args), args=args)
