#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数持仓量获取脚本 (Index Open Interest)
========================================

调用 Primit 数据中心的指数持仓量接口：
    GET https://api.pipai.org/index/v1/openInterest

请求参数
--------
    symbol   string   是   —   指数代码，例如 SPX、NDX。

鉴权
----
    需在请求头携带 ``X-Primit-API-Key``，密钥从项目根目录的 ``.env``
    文件中的 ``APIKEY`` 读取。

返回
----
    单个当前快照（非历史序列）：
        {"symbol": "SPXUSDT", "openInterest": "12168039", "time": 1782393510092}
    其中 time 为 Unix 毫秒。接口仅返回最新持仓量，period/limit 等参数无效。

注意
----
    本接口仅接受“指数代码”（如 SPX、NDX），SPY 等 ETF 不被接受。

用法示例
--------
    python index/index_open_interest.py                # 默认 SPX
    python index/index_open_interest.py --symbol NDX
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_URL = "https://api.pipai.org/index/v1/openInterest"
API_KEY_HEADER = "X-Primit-API-Key"


def load_api_key() -> str:
    """从项目根目录的 .env 文件读取 APIKEY。"""
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
    api_key = os.getenv("APIKEY")
    if not api_key:
        sys.exit("错误：未在 .env 中找到 APIKEY，请先配置 API 密钥。")
    return api_key


def fetch_open_interest(
    symbol: str,
    *,
    api_key: str | None = None,
    timeout: int = 30,
) -> dict:
    """
    获取指数当前持仓量。

    返回形如 {"symbol": ..., "openInterest": ..., "time": ...} 的字典。
    """
    if api_key is None:
        api_key = load_api_key()

    resp = requests.get(
        BASE_URL,
        params={"symbol": symbol},
        headers={API_KEY_HEADER: api_key},
        timeout=timeout,
    )
    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise RuntimeError(f"请求失败 [HTTP {resp.status_code}]: {detail}")

    return resp.json()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="获取 Primit 指数持仓量 (open interest)。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--symbol", default="SPX", help="指数代码，例如 SPX、NDX")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    try:
        data = fetch_open_interest(args.symbol)
    except RuntimeError as exc:
        sys.exit(f"错误：{exc}")

    # 将毫秒时间戳转为可读 UTC 时间，附在摘要里
    ts = datetime.fromtimestamp(data["time"] / 1000, tz=timezone.utc)
    print(
        f"# {args.symbol} 持仓量 = {data['openInterest']} "
        f"@ {ts:%Y-%m-%d %H:%M:%S} UTC",
        file=sys.stderr,
    )
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
