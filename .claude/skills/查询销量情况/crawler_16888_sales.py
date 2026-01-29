# -*- coding: utf-8 -*-
# 汽车销量爬虫 - 从车主之家抓取销量数据
import requests
from bs4 import BeautifulSoup
import time
import csv
import random
import argparse
import sys
import io
import os
import json

# 修复 Windows 控制台中文乱码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE = "https://xl.16888.com"

# 全局headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

# 保留session用于其他请求
session = requests.Session()
session.headers.update(headers.copy())
session.headers.update({"Referer": "https://xl.16888.com/"})


def api_request(endpoint):
    """API 请求封装"""
    url = f"{BASE}{endpoint}"
    request_headers = headers.copy()
    request_headers["Referer"] = f"{BASE}/style.html"
    try:
        r = requests.get(url, headers=request_headers, timeout=15)
        r.encoding = r.apparent_encoding
        return r.json()
    except Exception as e:
        print(f"API 请求失败: {e}")
        return None


def get_brands():
    """获取所有品牌"""
    print("正在获取品牌列表...")
    data = api_request("/xl.php?mod=api&extra=getCarBrand")
    if data and data.get("ret") == "ok":
        brands = []
        for group in data.get("data", []):
            brands.extend(group.get("list", []))
        return {b["cat_id"]: b["title"] for b in brands}
    return {}


def get_facturers(brand_id):
    """获取指定品牌的厂商列表"""
    data = api_request(f"/xl.php?mod=api&extra=getCarBrand&bid={brand_id}")
    if data and data.get("ret") == "ok":
        factories = []
        data_list = data.get("data")
        if not isinstance(data_list, list):
            return {}
        for group in data_list:
            factories.extend(group.get("list", []))
        return {f["cat_id"]: f["title"] for f in factories}
    return {}


def get_series(factory_id):
    """获取指定厂商的车型列表"""
    data = api_request(f"/xl.php?mod=api&extra=getCarBrand&fid={factory_id}")
    if data and data.get("ret") == "ok":
        models = data.get("data", {}).get("list", [])
        return {m["cat_id"]: m["title"] for m in models}
    return {}


def list_brands():
    """列出所有可用品牌"""
    brands = get_brands()
    if brands:
        print(f"\n找到 {len(brands)} 个品牌:\n")
        print("品牌ID  | 品牌名称")
        print("-" * 80)
        for bid in sorted(brands.keys(), key=lambda x: brands[x]):
            print(f"{bid:>8} | {brands[bid]}")
    else:
        print("未能获取品牌信息")


def list_facturers(brand_id):
    """列出指定品牌的厂商"""
    brands = get_brands()
    if brand_id not in brands:
        print(f"品牌ID {brand_id} 不存在")
        return

    print(f"\n品牌: {brands[brand_id]}")
    facturers = get_facturers(brand_id)
    if facturers:
        print(f"找到 {len(facturers)} 个厂商:\n")
        print("厂商ID  | 厂商名称")
        print("-" * 80)
        for fid in sorted(facturers.keys(), key=lambda x: facturers[x]):
            print(f"{fid:>8} | {facturers[fid]}")
    else:
        print("未能获取厂商信息")


def list_series(factory_id):
    """列出指定厂商的车型"""
    # 首先需要获取品牌列表来查找厂商
    brands = get_brands()
    factory_name = None
    brand_name = None

    # 遍历所有品牌找到这个厂商
    for bid in brands:
        facturers = get_facturers(bid)
        if factory_id in facturers:
            factory_name = facturers[factory_id]
            brand_name = brands[bid]
            break

    if not factory_name:
        print(f"厂商ID {factory_id} 不存在")
        return

    print(f"\n品牌: {brand_name}")
    print(f"厂商: {factory_name}")

    series = get_series(factory_id)
    if series:
        print(f"找到 {len(series)} 个车型:\n")
        print("车型ID  | 车型名称")
        print("-" * 80)
        for sid in sorted(series.keys(), key=lambda x: series[x]):
            print(f"{sid:>8} | {series[sid]}")
    else:
        print("未能获取车型信息")


def scrape_model_sales(series_id, series_name):
    """抓取指定车型的历史销量数据

    Args:
        series_id: 车型ID
        series_name: 车型名称
    """
    sales_data = []
    url = f"{BASE}/s/{series_id}/"

    print(f"\n正在抓取车型销量: {series_name}")
    print(f"URL: {url}")

    try:
        request_headers = headers.copy()
        request_headers["Referer"] = f"{BASE}/style.html"

        r = requests.get(url, headers=request_headers, timeout=15)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "lxml")
    except Exception as e:
        print(f"获取页面失败: {e}")
        return False

    # 找到销量表格
    table = soup.find("table")
    if not table:
        print("未找到销量表格")
        return False

    rows = table.find_all("tr")
    print(f"找到 {len(rows) - 1} 条销量记录")

    for row in rows[1:]:  # 跳过表头
        tds = row.find_all("td")
        if not tds or len(tds) < 4:
            continue

        # 提取销量信息
        month = tds[0].get_text(strip=True)  # 月份
        sales = tds[1].get_text(strip=True)  # 销量
        change = tds[2].get_text(strip=True)  # 环比变化

        # 保存数据
        sales_record = {
            "月份": month,
            "销量": sales,
            "环比": change,
        }

        sales_data.append(sales_record)

    # 保存到 CSV 文件
    if sales_data:
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{series_name}_销量_{date_str}.csv"

        os.makedirs("out", exist_ok=True)
        filepath = os.path.join("out", filename)

        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["月份", "销量", "环比"])
            writer.writeheader()
            writer.writerows(sales_data)

        print(f"\n数据已保存到 {filepath}")
        print(f"共 {len(sales_data)} 条记录")
        return True
    else:
        print("没有获取到任何数据")
        return False


def scrape_sales(max_pages=5):
    """抓取车型销量排行

    Args:
        max_pages: 最大抓取页数
    """
    sales_data = []

    print(f"开始抓取车型销量排行...")
    print(f"将抓取第 1 到第 {max_pages} 页")

    # 遍历每一页
    for page_num in range(1, max_pages + 1):
        # URL格式: /style-数字.html （第1页是 style.html）
        url = f"{BASE}/style-{page_num}.html" if page_num > 1 else f"{BASE}/style.html"
        print(f"\n========== 正在抓取第 {page_num}/{max_pages} 页 ==========")

        try:
            request_headers = headers.copy()
            request_headers["Referer"] = f"{BASE}/style.html"

            r = requests.get(url, headers=request_headers, timeout=15)
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, "lxml")
        except Exception as e:
            print(f"  获取页面失败: {e}")
            continue

        # 找到销量表格
        table = soup.find("table")
        if not table:
            print("  未找到销量表格")
            continue

        rows = table.find_all("tr")
        page_count = len(rows) - 1

        if page_count == 0:
            print(f"  本页没有数据，停止抓取")
            break

        print(f"  本页有 {page_count} 条销量记录")

        for row in rows[1:]:  # 跳过表头
            tds = row.find_all("td")
            if not tds or len(tds) < 6:
                continue

            # 提取销量信息
            rank = tds[0].get_text(strip=True)  # 排名
            model = tds[1].get_text(strip=True)  # 车型
            sales = tds[2].get_text(strip=True)  # 销量
            manufacturer = tds[3].get_text(strip=True)  # 厂商
            price = tds[4].get_text(strip=True)  # 售价

            # 保存数据
            sales_record = {
                "排名": rank,
                "车型": model,
                "销量": sales,
                "厂商": manufacturer,
                "售价（万元）": price,
            }

            sales_data.append(sales_record)

            # 每处理10条打印一次进度
            if len(sales_data) % 10 == 0:
                print(f"  已处理 {len(sales_data)} 条...")

        # 页面之间随机休眠
        if page_num < max_pages:
            sleep_time = random.uniform(0.5, 2.0)
            print(f"  休息 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)

    print(f"\n========== 抓取完成！==========")
    print(f"总共处理了 {len(sales_data)} 条销量记录")

    # 保存到 CSV 文件
    if sales_data:
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"销量排行_{date_str}.csv"

        os.makedirs("out", exist_ok=True)
        filepath = os.path.join("out", filename)

        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "排名", "车型", "销量", "厂商", "售价（万元）"
            ])
            writer.writeheader()
            writer.writerows(sales_data)

        print(f"数据已保存到 {filepath}")
        return True
    else:
        print("没有获取到任何数据")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='汽车销量爬虫 - 从车主之家抓取销量数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  # 查看所有品牌
  uv run .claude/skills/查询销量情况/crawler_16888_sales.py --brands

  # 查看指定品牌的厂商
  uv run .claude/skills/查询销量情况/crawler_16888_sales.py --facturers 57328

  # 查看指定厂商的车型
  uv run .claude/skills/查询销量情况/crawler_16888_sales.py --series 57329

  # 查询指定车型的历史销量
  uv run .claude/skills/查询销量情况/crawler_16888_sales.py --model 129054 --name "秦PLUS"

  # 抓取销量排行（默认5页）
  uv run .claude/skills/查询销量情况/crawler_16888_sales.py --sales

  # 抓取销量排行10页
  uv run .claude/skills/查询销量情况/crawler_16888_sales.py --sales --pages 10
        '''
    )

    parser.add_argument(
        '--brands',
        action='store_true',
        help='列出所有可用品牌及其ID'
    )

    parser.add_argument(
        '--facturers',
        type=str,
        metavar='BRAND_ID',
        help='列出指定品牌的厂商及其ID'
    )

    parser.add_argument(
        '--series',
        type=str,
        metavar='FACTURER_ID',
        help='列出指定厂商的车型及其ID'
    )

    parser.add_argument(
        '--model',
        type=str,
        metavar='SERIES_ID',
        help='查询指定车型的历史销量数据（需要配合 --name 使用）'
    )

    parser.add_argument(
        '--name',
        type=str,
        metavar='MODEL_NAME',
        help='车型名称（用于输出文件命名）'
    )

    parser.add_argument(
        '--sales',
        action='store_true',
        help='抓取车型销量排行数据'
    )

    parser.add_argument(
        '--pages',
        type=int,
        default=5,
        metavar='N',
        help='抓取页数（默认：5）'
    )

    args = parser.parse_args()

    # 如果指定了 --model，查询车型历史销量
    if args.model:
        if not args.name:
            print("错误: 使用 --model 时必须指定 --name 参数")
            return
        scrape_model_sales(args.model, args.name)
    # 如果指定了 --series，列出车型
    elif args.series:
        list_series(args.series)
    # 如果指定了 --facturers，列出厂商
    elif args.facturers:
        list_facturers(args.facturers)
    # 如果指定了 --brands，列出品牌
    elif args.brands:
        list_brands()
    # 如果指定了 --sales，抓取销量排行
    elif args.sales:
        scrape_sales(max_pages=args.pages)
    else:
        # 默认列出品牌
        print("默认列出可用品牌")
        list_brands()


if __name__ == "__main__":
    main()
