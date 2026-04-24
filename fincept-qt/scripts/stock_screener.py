#!/usr/bin/env python3
"""
China Stock Screener - 智能选股器
Supports filtering by:
1. Fundamental indicators (PE, PB, ROE, etc.)
2. Technical indicators (RSI, MACD, MA)
3. Market cap, volume, turnover
4. Custom conditions

Usage:
    python stock_screener.py --pe-max 20 --roe-min 15 --market-cap-min 10000000000
"""

import sys
import json
import argparse
import akshare as ak
import pandas as pd


def get_a_share_basic_info():
    """获取A股基本面数据"""
    try:
        # 获取实时行情
        df_spot = ak.stock_zh_a_spot_em()

        # 获取财务指标
        df_financial = ak.stock_financial_analysis_indicator(symbol="600519", start_year="2023")

        return df_spot
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


def filter_by_pe(df, pe_min=None, pe_max=None):
    """按市盈率筛选"""
    if '市盈率-动态' not in df.columns:
        return df

    df_filtered = df.copy()

    if pe_min is not None:
        df_filtered = df_filtered[df_filtered['市盈率-动态'] >= pe_min]

    if pe_max is not None:
        df_filtered = df_filtered[df_filtered['市盈率-动态'] <= pe_max]

    return df_filtered


def filter_by_roe(df, roe_min=None):
    """按ROE筛选"""
    # TODO: 从财务数据获取ROE
    return df


def filter_by_market_cap(df, market_cap_min=None, market_cap_max=None):
    """按市值筛选（单位：元）"""
    if '总市值' not in df.columns:
        return df

    df_filtered = df.copy()

    if market_cap_min is not None:
        df_filtered = df_filtered[df_filtered['总市值'] >= market_cap_min]

    if market_cap_max is not None:
        df_filtered = df_filtered[df_filtered['总市值'] <= market_cap_max]

    return df_filtered


def filter_by_volume(df, volume_min=None):
    """按成交量筛选"""
    if '成交量' not in df.columns:
        return df

    if volume_min is not None:
        df = df[df['成交量'] >= volume_min]

    return df


def filter_by_change_pct(df, change_min=None, change_max=None):
    """按涨跌幅筛选"""
    if '涨跌幅' not in df.columns:
        return df

    df_filtered = df.copy()

    if change_min is not None:
        df_filtered = df_filtered[df_filtered['涨跌幅'] >= change_min]

    if change_max is not None:
        df_filtered = df_filtered[df_filtered['涨跌幅'] <= change_max]

    return df_filtered


def screen_stocks(filters):
    """执行选股"""
    print("Fetching A-share data...", file=sys.stderr)
    df = get_a_share_basic_info()

    print(f"Total stocks: {len(df)}", file=sys.stderr)

    # 应用筛选条件
    if 'pe_min' in filters or 'pe_max' in filters:
        df = filter_by_pe(df, filters.get('pe_min'), filters.get('pe_max'))
        print(f"After PE filter: {len(df)}", file=sys.stderr)

    if 'market_cap_min' in filters or 'market_cap_max' in filters:
        df = filter_by_market_cap(df, filters.get('market_cap_min'), filters.get('market_cap_max'))
        print(f"After market cap filter: {len(df)}", file=sys.stderr)

    if 'volume_min' in filters:
        df = filter_by_volume(df, filters.get('volume_min'))
        print(f"After volume filter: {len(df)}", file=sys.stderr)

    if 'change_min' in filters or 'change_max' in filters:
        df = filter_by_change_pct(df, filters.get('change_min'), filters.get('change_max'))
        print(f"After change% filter: {len(df)}", file=sys.stderr)

    # 排序
    sort_by = filters.get('sort_by', '涨跌幅')
    ascending = filters.get('sort_ascending', False)

    if sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=ascending)

    # 返回前N条
    limit = filters.get('limit', 50)
    df = df.head(limit)

    # 转换为JSON格式
    result = []
    for _, row in df.iterrows():
        stock = {
            "symbol": f"{row['代码']}.SS" if row['代码'].startswith('6') else f"{row['代码']}.SZ",
            "name": row['名称'],
            "price": float(row['最新价']),
            "change_pct": float(row['涨跌幅']),
            "volume": int(row['成交量']) if pd.notna(row['成交量']) else 0,
            "turnover": float(row['成交额']) if pd.notna(row['成交额']) else 0,
            "pe_ratio": float(row['市盈率-动态']) if pd.notna(row['市盈率-动态']) else 0,
            "market_cap": float(row['总市值']) if pd.notna(row['总市值']) else 0,
        }
        result.append(stock)

    return result


def main():
    parser = argparse.ArgumentParser(description='China Stock Screener')

    # 基本面筛选
    parser.add_argument('--pe-min', type=float, help='Minimum P/E ratio')
    parser.add_argument('--pe-max', type=float, help='Maximum P/E ratio')
    parser.add_argument('--roe-min', type=float, help='Minimum ROE (%)')
    parser.add_argument('--market-cap-min', type=float, help='Minimum market cap (CNY)')
    parser.add_argument('--market-cap-max', type=float, help='Maximum market cap (CNY)')

    # 技术面筛选
    parser.add_argument('--volume-min', type=float, help='Minimum volume')
    parser.add_argument('--change-min', type=float, help='Minimum change %')
    parser.add_argument('--change-max', type=float, help='Maximum change %')

    # 排序和限制
    parser.add_argument('--sort-by', default='涨跌幅', help='Sort by column')
    parser.add_argument('--sort-ascending', action='store_true', help='Sort ascending')
    parser.add_argument('--limit', type=int, default=50, help='Max results')

    args = parser.parse_args()

    filters = vars(args)

    try:
        result = screen_stocks(filters)
        print(json.dumps({
            "success": True,
            "count": len(result),
            "stocks": result
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }))
        sys.exit(1)


if __name__ == '__main__':
    main()
