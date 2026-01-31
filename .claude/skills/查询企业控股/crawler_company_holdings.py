# -*- coding: utf-8 -*-
# 企业控股信息查询工具
import requests
from bs4 import BeautifulSoup
import csv
import argparse
import sys
import io
import json

# 修复 Windows 控制台中文乱码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 主要车企列表（A股）
CAR_COMPANIES = {
    "比亚迪": {"code": "002594", "market": "sz"},
    "上汽集团": {"code": "600104", "market": "sh"},
    "广汽集团": {"code": "601238", "market": "sh"},
    "长城汽车": {"code": "601633", "market": "sh"},
    "长安汽车": {"code": "000625", "market": "sz"},
    "蔚来": {"code": "NIO", "market": "us"},  # 美股
    "小鹏": {"code": "XPEV", "market": "us"},   # 美股
    "理想": {"code": "LI", "market": "us"},     # 美股
}

# 全局headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "http://data.eastmoney.com/",
}


def get_company_overview_eastmoney(stock_code, market="sh"):
    """从东方财富网获取公司概况

    Args:
        stock_code: 股票代码
        market: 市场代码（sh/sz）

    Returns:
        dict: 公司信息字典
    """
    url = "http://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/CompanySurveyAjax"
    params = {"code": f"{market}{stock_code}"}

    try:
        print(f"正在查询: {market}{stock_code}")
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"  请求失败: HTTP {response.status_code}")
            return None

        data = response.json()

        # 检查是否有错误
        if "jbzl" not in data:
            print(f"  未找到公司信息")
            return None

        jbzl = data.get("jbzl", {})

        company_info = {
            "公司名称": jbzl.get("gsmc", ""),
            "英文名称": jbzl.get("ywmc", ""),
            "股票代码": stock_code,
            "董事长": jbzl.get("zjl", ""),
            "法定代表人": jbzl.get("frdb", ""),
            "董秘": jbzl.get("dm", ""),
            "独立董事": jbzl.get("dlds", ""),
            "电话": jbzl.get("lxdh", ""),
            "邮箱": jbzl.get("dzxx", ""),
            "地址": jbzl.get("bgdz", ""),
            "主营业务": jbzl.get("jyfw", ""),
            "行业": jbzl.get("sshy", ""),
            "网址": jbzl.get("gswz", ""),
        }

        return company_info

    except Exception as e:
        print(f"  请求异常: {e}")
        return None


def get_sohu_company_info(company_name):
    """从搜狐财经获取企业基本信息（备用方案）

    Args:
        company_name: 公司名称

    Returns:
        dict: 公司信息字典
    """
    # 搜狐财经公司资料
    url = f"https://q.stock.sohu.com/search.jsp?keyword={company_name}"

    try:
        print(f"正在从搜狐财经查询: {company_name}")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"  请求失败: HTTP {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # 这里需要解析HTML结构（具体实现需要分析页面）
        # 暂时返回空字典
        return {"公司名称": company_name, "备注": "需要进一步分析HTML结构"}

    except Exception as e:
        print(f"  请求异常: {e}")
        return None


def print_company_info(info):
    """打印公司信息"""
    if not info:
        print("  未找到公司信息")
        return

    print(f"\n{'='*60}")
    print(f"公司名称: {info.get('公司名称', 'N/A')}")
    print(f"股票代码: {info.get('股票代码', 'N/A')}")
    print(f"{'='*60}")
    print(f"董事长: {info.get('董事长', 'N/A')}")
    print(f"法定代表人: {info.get('法定代表人', 'N/A')}")
    print(f"董秘: {info.get('董秘', 'N/A')}")
    print(f"独立董事: {info.get('独立董事', 'N/A')}")
    print(f"电话: {info.get('电话', 'N/A')}")
    print(f"邮箱: {info.get('邮箱', 'N/A')}")
    print(f"地址: {info.get('地址', 'N/A')}")
    print(f"行业: {info.get('行业', 'N/A')}")
    print(f"网址: {info.get('网址', 'N/A')}")
    print(f"主营业务: {info.get('主营业务', 'N/A')[:100]}...")
    print(f"{'='*60}\n")


def save_to_csv(data_list, filename):
    """保存到CSV文件

    Args:
        data_list: 数据列表
        filename: 文件名
    """
    if not data_list:
        print("没有数据需要保存")
        return

    import os
    os.makedirs("out", exist_ok=True)
    filepath = os.path.join("out", filename)

    fieldnames = [
        "公司名称", "股票代码", "董事长", "法定代表人", "董秘",
        "独立董事", "电话", "邮箱", "地址", "行业", "网址", "主营业务", "英文名称"
    ]

    try:
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_list)

        print(f"\n数据已保存到 {filepath}")
        print(f"共 {len(data_list)} 条记录")

    except Exception as e:
        print(f"保存文件失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='企业控股信息查询工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  # 查询单个公司
  uv run .claude/skills/查询企业控股/crawler_company_holdings.py --code 002594

  # 查询多个公司
  uv run .claude/skills/查询企业控股/crawler_company_holdings.py --names 比亚迪 上汽集团

  # 查询所有A股车企
  uv run .claude/skills/查询企业控股/crawler_company_holdings.py --all

  # 测试小鹏（美股）
  uv run .claude/skills/查询企业控股/crawler_company_holdings.py --test-xiaopeng
        '''
    )

    parser.add_argument(
        '--code',
        type=str,
        metavar='CODE',
        help='股票代码（如：002594、600104）'
    )

    parser.add_argument(
        '--market',
        type=str,
        default='auto',
        metavar='MARKET',
        choices=['sh', 'sz', 'auto'],
        help='市场代码（sh/sz/auto，默认：auto）'
    )

    parser.add_argument(
        '--names',
        nargs='+',
        metavar='NAME',
        help='公司名称列表（如：比亚迪 上汽集团）'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='查询所有A股车企'
    )

    parser.add_argument(
        '--test-xiaopeng',
        action='store_true',
        help='测试小鹏汽车控股信息'
    )

    args = parser.parse_args()

    results = []

    # 测试小鹏汽车
    if args.test_xiaopeng:
        print("\n🔍 测试：小鹏汽车控股信息查询")
        print("="*60)
        print("\n⚠️  注意：小鹏汽车在美股上市（代码: XPEV）")
        print("   国内实体公司：广州小鹏汽车科技有限公司")
        print("="*60)

        # 尝试查询小鹏的国内实体
        info = get_sohu_company_info("广州小鹏汽车科技有限公司")
        if info:
            print_company_info(info)
            results.append(info)

        print("\n💡 小鹏汽车控股信息（手动整理）:")
        print("-" * 60)
        print("创始人: 何小鹏")
        print("主要股东: 阿里巴巴、IDG资本、经纬创投等")
        print("上市地: 纽约证券交易所 (XPEV)")
        print("性质: 外资/混合所有制")
        print("-" * 60)

    # 查询单个股票代码
    elif args.code:
        # 自动判断市场
        market = args.market
        if market == 'auto':
            if args.code.startswith('6'):
                market = 'sh'
            elif args.code.startswith('0') or args.code.startswith('3'):
                market = 'sz'
            else:
                market = 'sh'  # 默认

        info = get_company_overview_eastmoney(args.code, market)
        if info:
            print_company_info(info)
            results.append(info)

            # 保存到CSV
            from datetime import datetime
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"企业控股_{args.code}_{date_str}.csv"
            save_to_csv(results, filename)

    # 查询指定公司名称列表
    elif args.names:
        for name in args.names:
            if name in CAR_COMPANIES:
                company_data = CAR_COMPANIES[name]
                info = get_company_overview_eastmoney(
                    company_data["code"],
                    company_data["market"]
                )
                if info:
                    print_company_info(info)
                    results.append(info)
            else:
                print(f"\n⚠️  公司 '{name}' 不在预定义列表中")
                # 尝试备用方案
                info = get_sohu_company_info(name)
                if info:
                    print_company_info(info)
                    results.append(info)

        # 保存到CSV
        if results:
            from datetime import datetime
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"企业控股_{'_'.join(args.names)}_{date_str}.csv"
            save_to_csv(results, filename)

    # 查询所有A股车企
    elif args.all:
        print("\n🔍 查询所有A股车企控股信息")
        print("="*60)

        for name, data in CAR_COMPANIES.items():
            if data["market"] in ["sh", "sz"]:
                info = get_company_overview_eastmoney(data["code"], data["market"])
                if info:
                    print_company_info(info)
                    results.append(info)

        # 保存到CSV
        if results:
            from datetime import datetime
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"企业控股_A股车企_{date_str}.csv"
            save_to_csv(results, filename)

    else:
        # 默认：查询比亚迪作为示例
        print("\n🔍 示例：查询比亚迪控股信息")
        print("="*60)

        info = get_company_overview_eastmoney("002594", "sz")
        if info:
            print_company_info(info)
            results.append(info)

            # 保存到CSV
            from datetime import datetime
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"企业控股_002594_{date_str}.csv"
            save_to_csv(results, filename)


if __name__ == "__main__":
    main()
