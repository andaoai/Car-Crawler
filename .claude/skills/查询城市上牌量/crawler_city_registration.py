# -*- coding: utf-8 -*-
# 城市汽车上牌量爬虫 - 从车主之家抓取城市上牌数据
import requests
from bs4 import BeautifulSoup
import time
import csv
import random
import argparse
import sys
import io
import os
from urllib.parse import urlencode

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

# 省份列表（从页面提取）
PROVINCES = {
    "0": "不限",
    "2": "北京",
    "32": "重庆",
    "25": "上海",
    "27": "天津",
    "3": "安徽",
    "4": "福建",
    "5": "甘肃",
    "6": "广东",
    "7": "广西",
    "8": "贵州",
    "9": "海南",
    "10": "河北",
    "11": "河南",
    "12": "黑龙江",
    "13": "湖北",
    "14": "湖南",
    "15": "吉林",
    "16": "江苏",
    "17": "江西",
    "18": "辽宁",
    "19": "内蒙古",
    "20": "宁夏",
    "21": "青海",
    "22": "山东",
    "23": "山西",
    "24": "陕西",
    "26": "四川",
    "28": "西藏",
    "29": "新疆",
    "30": "云南",
    "31": "浙江",
}

# 级别列表
LEVELS = {
    "0": "不限",
    "1": "微型车",
    "2": "小型车",
    "3": "紧凑型车",
    "4": "中型车",
    "5": "中大型车",
    "8": "大型车",
    "6": "MPV",
    "7": "SUV",
    "9": "跑车",
    "10": "电动车",
}


def list_provinces():
    """列出所有省份"""
    print(f"\n找到 {len(PROVINCES)} 个省份/直辖市:\n")
    print("省份ID  | 省份名称")
    print("-" * 80)
    for pid in sorted(PROVINCES.keys(), key=lambda x: PROVINCES[x]):
        print(f"{pid:>8} | {PROVINCES[pid]}")


def list_levels():
    """列出所有级别"""
    print(f"\n找到 {len(LEVELS)} 个级别:\n")
    print("级别ID  | 级别名称")
    print("-" * 80)
    for lid in sorted(LEVELS.keys(), key=lambda x: x if x.isdigit() else 0):
        print(f"{lid:>8} | {LEVELS[lid]}")


def list_cities(province_id):
    """列出指定省份的所有城市"""
    if province_id not in PROVINCES:
        print(f"省份ID {province_id} 不存在")
        print("请使用 --provinces 查看所有省份ID")
        return

    province_name = PROVINCES[province_id]
    print(f"\n正在获取 {province_name} 的城市列表...\n")

    # 访问省份的城市上牌量页面
    url = f"{BASE}/city-2024-01-{province_id}-0-0-0-0-1.html"

    try:
        request_headers = headers.copy()
        request_headers["Referer"] = f"{BASE}/city.html"

        r = requests.get(url, headers=request_headers, timeout=15)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "lxml")

        # 查找mod-nav区域（筛选区域）
        mod_nav = soup.find("div", class_="mod-nav")
        if not mod_nav:
            print("未找到筛选区域")
            return

        # 解析所有城市链接
        import re
        cities = {}
        # 查找所有包含data-id的链接
        pattern = r'<a[^>]*data-id="(\d+)"[^>]*data-title="([^"]+)"'
        matches = re.findall(pattern, str(mod_nav))

        # 过滤出属于该省份的城市
        for city_id, city_name in matches:
            # 直辖市（北京2、上海25、重庆32、天津27）的特殊处理
            if province_id in ["2", "25", "32", "27"]:
                # 对于直辖市，城市ID就是省份ID
                if city_id == province_id:
                    cities[city_name] = city_id
            else:
                # 其他省份，根据实际的城市ID范围过滤
                try:
                    city_id_num = int(city_id)
                    # 浙江省的城市ID从383开始（383-393）
                    if province_id == "31" and 383 <= city_id_num <= 400:
                        cities[city_name] = city_id
                    # 广东省的城市ID从76开始
                    elif province_id == "6" and 70 <= city_id_num <= 100:
                        cities[city_name] = city_id
                    # 江苏省等省份，city_id可能在province*100附近
                    elif city_id_num >= int(province_id) * 100 and city_id_num < int(province_id) * 100 + 100:
                        cities[city_name] = city_id
                except ValueError:
                    pass

        if cities:
            print(f"找到 {len(cities)} 个城市:\n")
            print("城市ID  | 城市名称")
            print("-" * 80)
            for city_name in sorted(cities.keys()):
                print(f"{cities[city_name]:>8} | {city_name}")

            print(f"\n使用示例:")
            print(f"  查询{province_name}全省: --province {province_id} --city 0")
            if cities:
                first_city = list(cities.items())[0]
                print(f"  查询{first_city[0]}: --province {province_id} --city {first_city[1]}")
        else:
            # 如果是直辖市
            if province_id in ["2", "25", "32", "27"]:
                print(f"{province_name}是直辖市，不需要选择城市")
                print(f"使用示例: --province {province_id} --city 0")
            else:
                print("未找到城市数据")

    except Exception as e:
        print(f"获取城市列表失败: {e}")


def scrape_city_registration(max_pages=5, province_id=None, city_id=None, brand_id=None,
                            factory_id=None, model_id=None, date_id=None):
    """抓取城市上牌量数据

    Args:
        max_pages: 最大抓取页数
        province_id: 省份ID（可选）
        city_id: 城市ID（可选）
        brand_id: 品牌ID（可选）
        factory_id: 厂商ID（可选）
        model_id: 车型ID（可选）
        date_id: 月份ID（可选，格式：YYYY-MM）
    """
    registration_data = []

    # 设置默认值
    if not date_id:
        date_id = "2025-12"  # 默认最新月份
    if not province_id:
        province_id = "0"
    if not city_id:
        city_id = "0"
    if not brand_id:
        brand_id = "0"
    if not factory_id:
        factory_id = "0"
    if not model_id:
        model_id = "0"

    # 生成筛选描述
    filter_desc = []
    filter_desc.append(f"月份={date_id}")
    if province_id != "0":
        filter_desc.append(f"省份={PROVINCES.get(province_id, province_id)}")
    if brand_id != "0":
        filter_desc.append(f"品牌ID={brand_id}")
    if factory_id != "0":
        filter_desc.append(f"厂商ID={factory_id}")
    if model_id != "0":
        filter_desc.append(f"车型ID={model_id}")
    filter_desc_str = " | ".join(filter_desc)

    print(f"开始抓取城市上牌量数据...")
    print(f"筛选条件: {filter_desc_str}")
    print(f"将抓取第 1 到第 {max_pages} 页")

    # 遍历每一页
    # 正确的URL格式: /city-{年月}-{省份ID}-{城市ID}-{品牌ID}-{厂商ID}-{车型ID}-{页码}.html
    for page_num in range(1, max_pages + 1):
        # 构建URL（使用正确的参数格式）
        url = f"{BASE}/city-{date_id}-{province_id}-{city_id}-{brand_id}-{factory_id}-{model_id}-{page_num}.html"

        print(f"\n========== 正在抓取第 {page_num}/{max_pages} 页 ==========")
        print(f"URL: {url}")

        try:
            request_headers = headers.copy()
            request_headers["Referer"] = f"{BASE}/city.html"

            r = requests.get(url, headers=request_headers, timeout=15)
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, "lxml")
        except Exception as e:
            print(f"  获取页面失败: {e}")
            continue

        # 找到上牌量表格
        table = soup.find("table")
        if not table:
            print("  未找到上牌量表格")
            continue

        rows = table.find_all("tr")
        page_count = len(rows) - 1

        if page_count == 0:
            print(f"  本页没有数据，停止抓取")
            break

        print(f"  本页有 {page_count} 条上牌记录")

        for row in rows[1:]:  # 跳过表头
            tds = row.find_all("td")
            if not tds or len(tds) < 6:
                continue

            # 提取上牌量信息
            rank = tds[0].get_text(strip=True)  # 排名
            model = tds[1].get_text(strip=True)  # 车型
            city = tds[2].get_text(strip=True)  # 城市
            registration = tds[3].get_text(strip=True)  # 上牌量
            level = tds[4].get_text(strip=True)  # 级别
            price = tds[5].get_text(strip=True)  # 指导价

            # 保存数据
            record = {
                "排名": rank,
                "车型": model,
                "城市": city,
                "上牌量": registration,
                "级别": level,
                "指导价（万元）": price,
            }

            registration_data.append(record)

            # 每处理10条打印一次进度
            if len(registration_data) % 10 == 0:
                print(f"  已处理 {len(registration_data)} 条...")

        # 页面之间随机休眠
        if page_num < max_pages:
            sleep_time = random.uniform(0.5, 2.0)
            print(f"  休息 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)

    print(f"\n========== 抓取完成！==========")
    print(f"总共处理了 {len(registration_data)} 条上牌记录")

    # 保存到 CSV 文件
    if registration_data:
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")

        # 生成文件名
        filename_parts = ["城市上牌量"]
        if date_id:
            filename_parts.append(date_id)
        if province_id and province_id != "0":
            filename_parts.append(PROVINCES.get(province_id, province_id))
        if brand_id and brand_id != "0":
            filename_parts.append(f"品牌{brand_id}")
        if factory_id and factory_id != "0":
            filename_parts.append(f"厂商{factory_id}")
        if model_id and model_id != "0":
            filename_parts.append(f"车型{model_id}")
        filename_parts.append(date_str)
        filename = "_".join(filename_parts) + ".csv"

        os.makedirs("out", exist_ok=True)
        filepath = os.path.join("out", filename)

        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "排名", "车型", "城市", "上牌量", "级别", "指导价（万元）"
            ])
            writer.writeheader()
            writer.writerows(registration_data)

        print(f"数据已保存到 {filepath}")
        return True
    else:
        print("没有获取到任何数据")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='城市汽车上牌量爬虫 - 从车主之家抓取城市上牌数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  # 查看所有省份
  uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --provinces

  # 查看指定省份的城市列表（例如：浙江）
  uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --cities 31

  # 查看所有级别
  uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --levels

  # 抓取全国城市上牌量（默认5页）
  uv run .claude/skills/查询城市上牌量/crawler_city_registration.py

  # 抓取指定月份的上牌量
  uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --date 2025-12

  # 抓取指定省份的上牌量
  uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --province 2

  # 抓取指定品牌的上牌量（需要先从销量爬虫获取品牌ID）
  uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --brand 127959

  # 抓取指定品牌和厂商的上牌量
  uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --brand 127959 --factory 127960

  # 抓取指定车型的上牌量（例如：小鹏P7）
  uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --province 2 --brand 127959 --factory 127960 --model 128729

  # 抓取指定月份、省份和车型的上牌量，10页
  uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --date 2025-12 --province 2 --model 128729 --pages 10
        '''
    )

    parser.add_argument(
        '--provinces',
        action='store_true',
        help='列出所有可用省份及其ID'
    )

    parser.add_argument(
        '--cities',
        type=str,
        metavar='PROVINCE_ID',
        help='列出指定省份的所有城市'
    )

    parser.add_argument(
        '--levels',
        action='store_true',
        help='列出所有可用级别及其ID'
    )

    parser.add_argument(
        '--province',
        type=str,
        metavar='PROVINCE_ID',
        help='按省份筛选（省份ID）'
    )

    parser.add_argument(
        '--date',
        type=str,
        metavar='DATE_ID',
        help='按月份筛选（格式：YYYY-MM，如 2025-12）'
    )

    parser.add_argument(
        '--city',
        type=str,
        metavar='CITY_ID',
        help='按城市筛选（城市ID）'
    )

    parser.add_argument(
        '--brand',
        type=str,
        metavar='BRAND_ID',
        help='按品牌筛选（品牌ID）'
    )

    parser.add_argument(
        '--factory',
        type=str,
        metavar='FACTORY_ID',
        help='按厂商筛选（厂商ID）'
    )

    parser.add_argument(
        '--model',
        type=str,
        metavar='MODEL_ID',
        help='按车型筛选（车型ID）'
    )

    parser.add_argument(
        '--pages',
        type=int,
        default=5,
        metavar='N',
        help='抓取页数（默认：5）'
    )

    args = parser.parse_args()

    # 如果指定了 --provinces，列出省份
    if args.provinces:
        list_provinces()
    # 如果指定了 --cities，列出城市
    elif args.cities:
        list_cities(args.cities)
    # 如果指定了 --levels，列出级别
    elif args.levels:
        list_levels()
    # 否则抓取数据
    else:
        scrape_city_registration(
            max_pages=args.pages,
            province_id=args.province,
            city_id=args.city,
            brand_id=args.brand,
            factory_id=args.factory,
            model_id=args.model,
            date_id=args.date
        )


if __name__ == "__main__":
    main()
