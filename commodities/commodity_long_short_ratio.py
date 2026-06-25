#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品多空比获取脚本 (Commodity Long/Short Ratio)
===============================================

调用 Primit 数据中心的两个多空比接口（同一份 schema，按 --type 选择）：
    GET https://api.pipai.org/commodity/v1/whaleLongShortRatio   鲸鱼（大户）多空比
    GET https://api.pipai.org/commodity/v1/topLongShortRatio     头部账户多空比

请求参数
--------
    symbol   string    是   —     商品代码，例如 XAU（黄金）、XAG（白银）。
    period   string    否   4h    周期，例如 5m、15m、1h、4h、1d。
    limit    integer   否   30    返回数量。

鉴权
----
    需在请求头携带 ``X-Primit-API-Key``，密钥从项目根目录的 ``.env``
    文件中的 ``APIKEY`` 读取。

返回
----
    时间序列数组，每个元素：
        {"symbol": "XAUUSDT", "longAccount": "0.55", "shortAccount": "0.45",
         "longShortRatio": "1.22", "timestamp": 1782360000000}
    longShortRatio = longAccount / shortAccount；timestamp 为 Unix 毫秒。

注意
----
    接口路径为 ``commodity``（单数），与本目录名 ``commodities`` 不同。

用法示例
--------
    python commodities/commodity_long_short_ratio.py                       # 默认 whale, XAU, 4h
    python commodities/commodity_long_short_ratio.py --type top --symbol XAG
    python commodities/commodity_long_short_ratio.py --period 1d --limit 60
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

CATEGORY = "commodity"
# --type -> 接口名
ENDPOINTS = {"whale": "whaleLongShortRatio", "top": "topLongShortRatio"}
API_KEY_HEADER = "X-Primit-API-Key"


def load_api_key() -> str:
    """从项目根目录的 .env 文件读取 APIKEY。"""
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
    api_key = os.getenv("APIKEY")
    if not api_key:
        sys.exit("错误：未在 .env 中找到 APIKEY，请先配置 API 密钥。")
    return api_key


def fetch_long_short_ratio(
    symbol: str,
    ratio_type: str = "whale",
    period: str = "4h",
    limit: int = 30,
    *,
    api_key: str | None = None,
    timeout: int = 30,
) -> list[dict]:
    """
    获取多空比时间序列。

    ratio_type: "whale"（鲸鱼/大户）或 "top"（头部账户）。
    返回字典列表（按时间升序）。
    """
    if ratio_type not in ENDPOINTS:
        raise ValueError(
            f"未知 type：{ratio_type!r}，可选：{sorted(ENDPOINTS)}"
        )
    if api_key is None:
        api_key = load_api_key()

    url = f"https://api.pipai.org/{CATEGORY}/v1/{ENDPOINTS[ratio_type]}"
    resp = requests.get(
        url,
        params={"symbol": symbol, "period": period, "limit": limit},
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
        description="获取 Primit 商品多空比 (whale / top long-short ratio)。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--type",
        default="whale",
        choices=sorted(ENDPOINTS),
        help="whale=鲸鱼/大户多空比，top=头部账户多空比",
    )
    parser.add_argument("--symbol", default="XAU", help="商品代码，例如 XAU、XAG")
    parser.add_argument("--period", default="4h", help="周期，例如 5m、1h、4h、1d")
    parser.add_argument("--limit", type=int, default=30, help="返回数量")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    try:
        rows = fetch_long_short_ratio(args.symbol, args.type, args.period, args.limit)
    except (RuntimeError, ValueError) as exc:
        sys.exit(f"错误：{exc}")

    if not rows:
        sys.exit("接口返回空数据。")

    # 最新一条 -> stderr 摘要
    latest = rows[-1]
    ts = datetime.fromtimestamp(latest["timestamp"] / 1000, tz=timezone.utc)
    print(
        f"# {args.symbol} {args.type} 多空比 @ {ts:%Y-%m-%d %H:%M} UTC | "
        f"longShortRatio={latest['longShortRatio']} "
        f"(多 {latest['longAccount']} / 空 {latest['shortAccount']})",
        file=sys.stderr,
    )
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
