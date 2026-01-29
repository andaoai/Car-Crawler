# 汽车销量爬虫 - 从车主之家抓取销量数据
import requests
from bs4 import BeautifulSoup
import time
import csv
import random
import argparse
import sys
import io

# 设置输出编码为 UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

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


def get_brands_from_table():
    """从销量表格中提取品牌/厂商信息"""
    print("正在从销量表格中提取厂商信息...")
    URL = f"{BASE}/style.html"

    try:
        r = session.get(URL, timeout=15)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "lxml")

        # 查找销量表格
        table = soup.find("table")
        if not table:
            print("未找到销量表格")
            return {}

        # 提取厂商信息（第4列）
        rows = table.find_all("tr")
        manufacturers_seen = {}
        manufacturer_id = 1

        for row in rows[1:]:  # 跳过表头
            tds = row.find_all("td")
            if len(tds) >= 4:
                manufacturer = tds[3].get_text(strip=True)  # 第4列是厂商
                if manufacturer and manufacturer not in manufacturers_seen:
                    manufacturers_seen[str(manufacturer_id)] = manufacturer
                    manufacturer_id += 1

        return manufacturers_seen

    except Exception as e:
        print(f"提取厂商信息失败: {e}")
        import traceback
        traceback.print_exc()
        return {}


def get_brands():
    """从车型销量页面提取品牌信息"""
    print("正在从车型销量页面提取品牌信息...")
    URL = f"{BASE}/style.html"

    try:
        r = session.get(URL, timeout=15)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "lxml")

        # 查找品牌选择器
        brand_select = soup.find("div", class_="i-select i-select-brand J_c_brand")

        if not brand_select:
            print("未找到品牌选择器，使用销量表格中的厂商信息...")
            return get_brands_from_table()

        # 查找所有品牌选项（可能是 a 标签或 li 标签）
        brands_seen = {}

        # 尝试查找链接
        brand_items = brand_select.find_all("a", href=True)
        if not brand_items:
            # 如果没有链接，尝试查找 li 标签
            brand_items = brand_select.find_all("li")

        for item in brand_items:
            href = item.get("href", "")
            brand_name = item.get_text(strip=True)

            # 从链接提取品牌ID
            # 格式可能是: /style/b123-0-0-0-0-0-1.html 或类似
            if href and ("/style/" in href or "b" in href):
                # 尝试提取品牌ID
                import re
                match = re.search(r'b(\d+)', href)

                if match:
                    brand_id = match.group(1)
                    if brand_id.isdigit() and brand_name:
                        if brand_id not in brands_seen:
                            brands_seen[brand_id] = brand_name

            # 如果没有链接但有品牌名称，可能使用 data-id 属性
            elif brand_name:
                brand_id = item.get("data-id", "")
                value_attr = item.get("value", "")
                if brand_id.isdigit():
                    if brand_id not in brands_seen:
                        brands_seen[brand_id] = brand_name
                elif value_attr.isdigit():
                    if value_attr not in brands_seen:
                        brands_seen[value_attr] = brand_name

        if brands_seen:
            return brands_seen
        else:
            print("品牌选择器为空，使用销量表格中的厂商信息...")
            return get_brands_from_table()

    except Exception as e:
        print(f"提取品牌信息失败: {e}")
        import traceback
        traceback.print_exc()
        return {}


def list_brands():
    """列出所有可用品牌"""
    brands = get_brands()

    if brands:
        print(f"\n找到 {len(brands)} 个厂商:\n")
        print("厂商ID | 厂商名称")
        print("-" * 60)

        # 按ID排序
        for bid in sorted(brands.keys(), key=lambda x: int(x) if x.isdigit() else 0):
            print(f"{bid:>6} | {brands[bid]}")
    else:
        print("未能从页面提取厂商信息")


def scrape_sales(max_pages=5):
    """抓取销量数据

    Args:
        max_pages: 最大抓取页数
    """
    sales_data = []

    print(f"开始抓取销量数据...")
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
        # 生成有意义的文件名
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"销量排行_{date_str}.csv"

        with open(filename, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "排名", "车型", "销量", "厂商", "售价（万元）"
            ])
            writer.writeheader()
            writer.writerows(sales_data)
        print(f"数据已保存到 {filename}")
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
  uv run crawler_16888_sales.py --brands              # 列出所有可用厂商
  uv run crawler_16888_sales.py --sales               # 抓取销量数据（默认5页）
  uv run crawler_16888_sales.py --sales --pages 10    # 抓取销量数据10页
        '''
    )

    parser.add_argument(
        '--brands',
        action='store_true',
        help='列出所有可用厂商及其ID'
    )

    parser.add_argument(
        '--sales',
        action='store_true',
        help='抓取销量数据'
    )

    parser.add_argument(
        '--pages',
        type=int,
        default=5,
        metavar='N',
        help='抓取页数（默认：5）'
    )

    args = parser.parse_args()

    # 如果指定了 --brands，只列出厂商
    if args.brands:
        list_brands()
    elif args.sales:
        # 抓取销量数据
        scrape_sales(max_pages=args.pages)
    else:
        # 默认列出厂商
        print("默认列出可用厂商")
        list_brands()


if __name__ == "__main__":
    main()
