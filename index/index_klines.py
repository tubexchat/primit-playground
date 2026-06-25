#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数 K 线获取脚本 (Index Klines)
================================

调用 Primit 数据中心的指数 K 线接口：
    GET https://api.pipai.org/index/v1/klines

请求参数
--------
    symbol      string   是   —     指数代码，例如 SPX、NDX。
    interval    string   否   1d    取值：1m、5m、15m、30m、1h、1d、1w、1M。
    limit       integer  否   100   返回的 K 线数量。
    startTime   integer  否   —     起始时间（含），Unix 毫秒。
    endTime     integer  否   —     结束时间（含），Unix 毫秒。

鉴权
----
    需在请求头携带 ``X-Primit-API-Key``，密钥从项目根目录的 ``.env``
    文件中的 ``APIKEY`` 读取。

注意
----
    本接口仅接受“指数代码”。SPY 属于 ETF/股票（equity）品类，会被接口
    拒绝；标普 500 指数在本接口对应的代码为 ``SPX``。

用法示例
--------
    python index/index_klines.py                          # 默认 SPX, 1d, 100 根
    python index/index_klines.py --symbol NDX --interval 1h --limit 50
    python index/index_klines.py --symbol SPX --start 1782259200000 --end 1782345600000
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
BASE_URL = "https://api.pipai.org/index/v1/klines"
API_KEY_HEADER = "X-Primit-API-Key"
VALID_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "1d", "1w", "1M"}

# K 线数组的字段含义（接口返回 Binance 风格的二维数组）
KLINE_FIELDS = [
    "open_time",            # 开盘时间 (ms)
    "open",                 # 开盘价
    "high",                 # 最高价
    "low",                  # 最低价
    "close",                # 收盘价
    "volume",               # 成交量
    "close_time",           # 收盘时间 (ms)
    "quote_volume",         # 成交额
    "trade_count",          # 成交笔数
    "taker_buy_base",       # 主动买入成交量
    "taker_buy_quote",      # 主动买入成交额
    "ignore",               # 忽略字段
]


def load_api_key() -> str:
    """从项目根目录的 .env 文件读取 APIKEY。"""
    # .env 位于本脚本上一级目录（项目根）
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")

    api_key = os.getenv("APIKEY")
    if not api_key:
        sys.exit("错误：未在 .env 中找到 APIKEY，请先配置 API 密钥。")
    return api_key


def fetch_klines(
    symbol: str,
    interval: str = "1d",
    limit: int = 100,
    start_time: int | None = None,
    end_time: int | None = None,
    *,
    api_key: str | None = None,
    timeout: int = 30,
) -> list[list]:
    """
    获取指数 K 线。

    参数
    ----
    symbol      指数代码，例如 "SPX"、"NDX"。
    interval    K 线周期，默认 "1d"。
    limit       返回数量，默认 100。
    start_time  起始时间（含），Unix 毫秒，可选。
    end_time    结束时间（含），Unix 毫秒，可选。
    api_key     可显式传入，否则自动从 .env 读取。
    timeout     请求超时秒数。

    返回
    ----
    K 线二维数组（每个元素对应 KLINE_FIELDS）。
    """
    if interval not in VALID_INTERVALS:
        raise ValueError(
            f"interval 非法：{interval!r}，可选值：{sorted(VALID_INTERVALS)}"
        )

    if api_key is None:
        api_key = load_api_key()

    params: dict[str, object] = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }
    if start_time is not None:
        params["startTime"] = start_time
    if end_time is not None:
        params["endTime"] = end_time

    headers = {API_KEY_HEADER: api_key}

    resp = requests.get(BASE_URL, params=params, headers=headers, timeout=timeout)

    # 接口异常时返回 {"detail": "..."}，给出可读报错
    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise RuntimeError(f"请求失败 [HTTP {resp.status_code}]: {detail}")

    return resp.json()


def to_records(klines: list[list]) -> list[dict]:
    """将原始二维数组转换为带字段名的字典列表，便于阅读 / 入库。"""
    return [dict(zip(KLINE_FIELDS, row)) for row in klines]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="获取 Primit 指数 K 线 (index klines)。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # 默认 SPX：标普 500 指数。SPY 为 ETF，不被指数接口接受。
    parser.add_argument("--symbol", default="SPX", help="指数代码，例如 SPX、NDX")
    parser.add_argument(
        "--interval",
        default="1d",
        choices=sorted(VALID_INTERVALS),
        help="K 线周期",
    )
    parser.add_argument("--limit", type=int, default=100, help="返回的 K 线数量")
    parser.add_argument(
        "--start", type=int, default=None, help="起始时间（含），Unix 毫秒"
    )
    parser.add_argument(
        "--end", type=int, default=None, help="结束时间（含），Unix 毫秒"
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="输出接口原始二维数组（默认输出带字段名的 JSON）",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    try:
        klines = fetch_klines(
            symbol=args.symbol,
            interval=args.interval,
            limit=args.limit,
            start_time=args.start,
            end_time=args.end,
        )
    except (RuntimeError, ValueError) as exc:
        sys.exit(f"错误：{exc}")

    data = klines if args.raw else to_records(klines)
    print(f"# {args.symbol} {args.interval} —— 共 {len(klines)} 根 K 线", file=sys.stderr)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
