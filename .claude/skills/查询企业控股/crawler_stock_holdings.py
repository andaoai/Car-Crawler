# -*- coding: utf-8 -*-
# 企业股东持股比例查询工具 - 使用 AKShare API 动态获取数据
import csv
import sys
import io
import os
import warnings
from datetime import datetime

# 修复 Windows 控制台中文乱码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 抑制 AKShare 的 FutureWarning
warnings.filterwarnings('ignore', category=FutureWarning)

# 主要车企列表（A股）
CAR_COMPANIES = {
    "比亚迪": "002594",
    "上汽集团": "600104",
    "广汽集团": "601238",
    "长城汽车": "601633",
    "长安汽车": "000625",
    "江淮汽车": "600418",
    "海马汽车": "000572",
}


def get_stock_holdings_akshare(stock_code):
    """从 AKShare API 获取股东持股比例

    Args:
        stock_code: 股票代码（如：002594、600104）

    Returns:
        dict: 包含控股股东、持股比例等信息的字典
        None: 获取失败时返回 None
    """
    try:
        import akshare as ak

        print(f"正在查询: {stock_code} 的股东持股比例")

        # 获取主要股东数据
        df = ak.stock_main_stock_holder(stock=stock_code)

        if df is None or df.empty:
            print(f"  未找到股东数据")
            return None

        # 获取最新的股东数据（第一条）
        latest_record = df.iloc[0]

        # 提取关键信息
        top_shareholder = latest_record.get("股东名称", "")
        holding_ratio = latest_record.get("持股比例", "")
        share_count = latest_record.get("持股数量", "")
        share_nature = latest_record.get("股本性质", "")
        report_date = latest_record.get("截至日期", "")

        # 格式化持股比例
        if pd.isna(holding_ratio):
            holding_ratio_str = "未披露"
        else:
            holding_ratio_str = f"{holding_ratio}%"

        # 格式化持股数量
        if pd.notna(share_count):
            share_count_str = f"{share_count / 100000000:.2f}亿股" if share_count > 100000000 else f"{share_count / 10000:.2f}万股"
        else:
            share_count_str = "未披露"

        # 判断企业性质（根据股东名称）
        if any(keyword in str(top_shareholder) for keyword in ["集团", "国资委", "国资", "人民政府", "实业", "投资"]):
            nature = "国有控股"
            actual_controller = "地方政府/国务院"
        else:
            nature = "民营"
            # 尝试从股东名称推断实际控制人
            if len(str(top_shareholder)) > 2:
                actual_controller = str(top_shareholder)[:4] + "..."
            else:
                actual_controller = "未知"

        print(f"  ✅ 成功获取数据（截至：{report_date}）")

        return {
            "控股股东": top_shareholder,
            "持股比例": holding_ratio_str,
            "持股数量": share_count_str,
            "股本性质": share_nature,
            "实际控制人": actual_controller,
            "性质": nature,
            "截至日期": report_date,
            "原始数据": df  # 保留原始数据用于进一步分析
        }

    except ImportError:
        print(f"  ❌ AKShare 库未安装")
        print(f"  💡 请运行: uv add akshare")
        return None
    except Exception as e:
        print(f"  ❌ 获取失败: {e}")
        return None


def get_all_top_shareholders(stock_code, top_n=10):
    """获取前 N 大股东详细信息

    Args:
        stock_code: 股票代码
        top_n: 获取前N大股东

    Returns:
        list: 股东信息列表
    """
    try:
        import akshare as ak
        import pandas as pd

        df = ak.stock_main_stock_holder(stock=stock_code)

        if df is None or df.empty:
            return []

        # 获取最新报告期的数据
        latest_date = df.iloc[0]["截至日期"]
        latest_data = df[df["截至日期"] == latest_date].head(top_n)

        shareholders = []
        for _, row in latest_data.iterrows():
            shareholder_info = {
                "排名": int(row.get("编号", 0)),
                "股东名称": row.get("股东名称", ""),
                "持股数量": row.get("持股数量", ""),
                "持股比例": row.get("持股比例", ""),
                "股本性质": row.get("股本性质", ""),
            }
            shareholders.append(shareholder_info)

        return shareholders

    except Exception as e:
        print(f"  获取股东详情失败: {e}")
        return []


def print_holdings_info(company_name, stock_code, info):
    """打印持股信息"""
    print(f"\n{'='*70}")
    print(f"📊 {company_name} ({stock_code}) - 股东持股比例")
    print(f"{'='*70}")
    print(f"🏢 控股股东: {info.get('控股股东', 'N/A')}")
    print(f"📈 持股比例: {info.get('持股比例', 'N/A')}")
    print(f"📊 持股数量: {info.get('持股数量', 'N/A')}")
    print(f"👤 实际控制人: {info.get('实际控制人', 'N/A')}")
    print(f"🏷️  企业性质: {info.get('性质', 'N/A')}")
    print(f"📅 数据截至: {info.get('截至日期', 'N/A')}")
    print(f"{'='*70}")

    if '原始数据' in info:
        df = info['原始数据']
        latest_date = df.iloc[0]["截至日期"]
        latest_data = df[df["截至日期"] == latest_date].head(5)

        print(f"📋 前5大股东详情:")
        for _, row in latest_data.iterrows():
            ratio = row.get("持股比例", "")
            ratio_str = f"{ratio}%" if pd.notna(ratio) else "未披露"
            print(f"   {row.get('编号', '')}. {row.get('股东名称', '')}: {ratio_str}")

    print(f"{'='*70}\n")


def save_holdings_to_csv(holdings_data, filename):
    """保存持股数据到CSV

    Args:
        holdings_data: 持股数据字典 {company_name: {stock_code: info}}
        filename: 文件名
    """
    rows = []

    for company_name, codes_data in holdings_data.items():
        for code, info in codes_data.items():
            row = {
                "公司名称": company_name,
                "股票代码": code,
                "控股股东": info.get("控股股东", ""),
                "持股比例": info.get("持股比例", ""),
                "持股数量": info.get("持股数量", ""),
                "实际控制人": info.get("实际控制人", ""),
                "性质": info.get("性质", ""),
                "数据截至日期": info.get("截至日期", ""),
            }
            rows.append(row)

    if not rows:
        print("没有数据需要保存")
        return False

    os.makedirs("out", exist_ok=True)
    filepath = os.path.join("out", filename)

    fieldnames = [
        "公司名称", "股票代码", "控股股东", "持股比例", "持股数量",
        "实际控制人", "性质", "数据截至日期"
    ]

    try:
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\n✅ 数据已保存到 {filepath}")
        print(f"共 {len(rows)} 条记录")
        return True

    except Exception as e:
        print(f"保存文件失败: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='企业股东持股比例查询工具 - 使用 AKShare API 动态获取',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  # 查询所有车企持股比例
  uv run .claude/skills/查询企业控股/crawler_stock_holdings.py

  # 显示特定公司
  uv run .claude/skills/查询企业控股/crawler_stock_holdings.py --company 比亚迪

  # 查询指定股票代码
  uv run .claude/skills/查询企业控股/crawler_stock_holdings.py --code 002594

  # 获取前10大股东详情
  uv run .claude/skills/查询企业控股/crawler_stock_holdings.py --code 002594 --detail
        '''
    )

    parser.add_argument(
        '--company',
        type=str,
        metavar='NAME',
        help='显示特定公司的持股比例'
    )

    parser.add_argument(
        '--code',
        type=str,
        metavar='CODE',
        help='查询指定股票代码的持股比例'
    )

    parser.add_argument(
        '--detail',
        action='store_true',
        help='显示前10大股东详细信息'
    )

    args = parser.parse_args()

    # 动态获取持股数据
    holdings_data = {}

    if args.code:
        # 查询指定股票代码
        info = get_stock_holdings_akshare(args.code)
        if info:
            # 反查公司名称
            company_name = next((k for k, v in CAR_COMPANIES.items() if v == args.code), f"股票{args.code}")
            holdings_data[company_name] = {args.code: info}
            print_holdings_info(company_name, args.code, info)

            if args.detail:
                shareholders = get_all_top_shareholders(args.code, top_n=10)
                if shareholders:
                    print(f"\n📋 前10大股东详细信息:")
                    print(f"{'='*70}")
                    for s in shareholders:
                        ratio_str = f"{s['持股比例']}%" if pd.notna(s['持股比例']) else "未披露"
                        print(f"  {s['排名']}. {s['股东名称']}: {ratio_str} ({s['股本性质']})")
                    print(f"{'='*70}\n")

    elif args.company:
        # 显示特定公司
        if args.company in CAR_COMPANIES:
            stock_code = CAR_COMPANIES[args.company]
            info = get_stock_holdings_akshare(stock_code)
            if info:
                holdings_data[args.company] = {stock_code: info}
                print_holdings_info(args.company, stock_code, info)

                if args.detail:
                    shareholders = get_all_top_shareholders(stock_code, top_n=10)
                    if shareholders:
                        print(f"\n📋 前10大股东详细信息:")
                        print(f"{'='*70}")
                        for s in shareholders:
                            ratio_str = f"{s['持股比例']}%" if pd.notna(s['持股比例']) else "未披露"
                            print(f"  {s['排名']}. {s['股东名称']}: {ratio_str} ({s['股本性质']})")
                        print(f"{'='*70}\n")
        else:
            print(f"\n❌ 未找到 '{args.company}' 的数据")
            print(f"\n可用的公司: {', '.join(CAR_COMPANIES.keys())}")
    else:
        # 显示所有公司
        print("\n🔍 主要汽车企业股东持股比例")
        print("="*70)

        for company_name, stock_code in CAR_COMPANIES.items():
            info = get_stock_holdings_akshare(stock_code)
            if info:
                holdings_data[company_name] = {stock_code: info}
                print_holdings_info(company_name, stock_code, info)

        # 保存到CSV
        if holdings_data:
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"企业持股比例_{date_str}.csv"
            save_holdings_to_csv(holdings_data, filename)


if __name__ == "__main__":
    # 导入 pandas 用于处理 NaN 值
    import pandas as pd
    main()
