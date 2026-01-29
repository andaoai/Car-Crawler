# 汽车投诉爬虫 - 支持命令行参数
import requests
from bs4 import BeautifulSoup
import time
import re
import csv
import random
import argparse

BASE = "https://www.12365auto.com"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.12365auto.com/",
})


def get_brands_from_complaints():
    """从车型大全页面中提取品牌信息"""
    print("正在从车型大全页面提取品牌信息...")
    # 车型大全页面URL
    URL = f"{BASE}/list/models-0-1-1-0-0-0-0-0-0-0-0-0-0.shtml"

    try:
        r = session.get(URL, timeout=15)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "lxml")

        # 查找所有品牌链接
        brand_links = soup.find_all("a", href=lambda x: x and "brand-" in x)

        brands_seen = {}
        for link in brand_links:
            href = link.get("href", "")
            brand_name = link.get_text(strip=True)

            # 从链接提取品牌ID
            if "brand-" in href:
                parts = href.split("brand-")
                if len(parts) > 1:
                    brand_id = parts[1].split("-")[0]
                    if brand_id.isdigit() and brand_name:
                        if brand_id not in brands_seen:
                            brands_seen[brand_id] = brand_name

        return brands_seen
    except Exception as e:
        print(f"提取品牌信息失败: {e}")
        return {}


def get_models_by_brand(brand_id):
    """根据品牌ID获取车型列表"""
    print(f"正在查询品牌ID {brand_id} 的车型...")
    URL = f"{BASE}/zlts/{brand_id}-0-0-0-0-0_0-0-0-0-0-0-0-1.shtml"

    try:
        r = session.get(URL, timeout=15)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "lxml")

        # 从投诉列表中提取车型
        tslb_div = soup.find("div", class_="tslb_b")
        if not tslb_div:
            return {}

        table = tslb_div.find("table")
        if not table:
            return {}

        rows = table.find_all("tr")
        models_seen = {}

        for row in rows[1:]:  # 跳过表头
            tds = row.find_all("td")
            if len(tds) >= 4:
                model = tds[3].get_text(strip=True)
                # 从车系列的 td 中提取 mid 属性
                series_td = tds[2]
                model_id = series_td.get("mid", "")

                if model_id.isdigit() and model:
                    if model_id not in models_seen:
                        models_seen[model_id] = model

        return models_seen
    except Exception as e:
        print(f"提取车型信息失败: {e}")
        return {}


def get_series_by_brand(brand_id):
    """根据品牌ID获取车系列表"""
    print(f"正在查询品牌ID {brand_id} 的车系...")
    URL = f"{BASE}/zlts/{brand_id}-0-0-0-0-0_0-0-0-0-0-0-0-1.shtml"

    try:
        r = session.get(URL, timeout=15)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "lxml")

        # 从投诉列表中提取车系
        tslb_div = soup.find("div", class_="tslb_b")
        if not tslb_div:
            return {}

        table = tslb_div.find("table")
        if not table:
            return {}

        rows = table.find_all("tr")
        series_seen = {}

        for row in rows[1:]:  # 跳过表头
            tds = row.find_all("td")
            if len(tds) >= 3:
                series = tds[2].get_text(strip=True)
                # 从链接中提取车系ID
                link = tds[2].find("a", href=True)
                if link:
                    href = link.get("href", "")
                    # 格式: //www.12365auto.com/series/{series_id}/index.shtml
                    if "/series/" in href:
                        parts = href.split("/series/")
                        if len(parts) > 1:
                            series_id = parts[1].split("/")[0]
                            if series_id.isdigit() and series:
                                if series_id not in series_seen:
                                    series_seen[series_id] = series

        return series_seen
    except Exception as e:
        print(f"提取车系信息失败: {e}")
        return {}


def list_brands():
    """列出所有可用品牌"""
    brands = get_brands_from_complaints()

    if brands:
        print(f"\n找到 {len(brands)} 个品牌:\n")
        print("品牌ID | 品牌名称")
        print("-" * 60)

        # 按ID排序
        for bid in sorted(brands.keys(), key=lambda x: int(x) if x.isdigit() else 0):
            print(f"{bid:>6} | {brands[bid]}")
    else:
        print("未能从页面提取品牌信息")
        print("\n常用品牌ID参考:")
        print("-" * 60)
        common_brands = [
            (0, "全部品牌"),
            (1, "北京奔驰"),
            (4, "一汽-大众"),
            (8, "东风日产"),
            (12, "一汽-大众捷达"),
            (15, "一汽丰田"),
            (19, "上汽大众"),
            (26, "一汽奥迪"),
            (43, "广汽本田"),
            (58, "一汽马自达"),
            (63, "一汽本田"),
            (68, "长安马自达"),
            (140, "吉利汽车"),
        ]
        for bid, name in common_brands:
            print(f"{bid:>6} | {name}")


def scrape_complaints(brand_id=0, max_pages=5):
    """抓取投诉数据

    Args:
        brand_id: 品牌ID，0表示全部品牌
        max_pages: 最大抓取页数
    """
    LIST_URL_TEMPLATE = f"{BASE}/zlts/{brand_id}-0-0-0-0-0_0-0-0-0-0-0-0-{{page}}.shtml"

    complaints_data = []
    complaint_pattern = re.compile(r'//www\.12365auto\.com/zlts/\d{8}/\d+\.shtml$')

    brand_name = "全部品牌" if brand_id == 0 else f"品牌ID={brand_id}"
    print(f"开始抓取投诉数据...")
    print(f"当前配置: {brand_name}")
    print(f"将抓取第 1 到第 {max_pages} 页")

    # 遍历每一页
    for page_num in range(1, max_pages + 1):
        url = LIST_URL_TEMPLATE.format(page=page_num)
        print(f"\n========== 正在抓取第 {page_num}/{max_pages} 页 ==========")

        try:
            r = session.get(url, timeout=15)
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, "lxml")
        except Exception as e:
            print(f"  获取页面失败: {e}")
            continue

        # 找到投诉列表的 table
        tslb_div = soup.find("div", class_="tslb_b")
        if not tslb_div:
            print("  未找到投诉列表区域")
            continue

        table = tslb_div.find("table")
        if not table:
            print("  未找到投诉列表表格")
            continue

        rows = table.find_all("tr")
        page_count = len(rows) - 1

        if page_count == 0:
            print(f"  本页没有数据，停止抓取")
            break

        print(f"  本页有 {page_count} 条投诉记录")

        for row in rows[1:]:  # 跳过表头
            tds = row.find_all("td")
            if not tds or len(tds) < 8:
                continue

            # 从列表页提取基本信息
            complaint_id = tds[0].get_text(strip=True)
            brand = tds[1].get_text(strip=True)
            series = tds[2].get_text(strip=True)
            model = tds[3].get_text(strip=True)
            problem_summary = tds[4].get_text(strip=True)
            typical_problem = tds[5].get_text(strip=True)
            complaint_time = tds[6].get_text(strip=True)
            status = tds[7].get_text(strip=True)

            # 查找详情链接
            complaint_link = None
            for td in tds:
                links = td.find_all("a", href=True)
                for link in links:
                    href = link.get("href")
                    if href and complaint_pattern.match(href):
                        complaint_link = href
                        break
                if complaint_link:
                    break

            if not complaint_link:
                continue

            # 构建完整 URL
            if complaint_link.startswith("//"):
                detail_url = "https:" + complaint_link
            elif complaint_link.startswith("/"):
                detail_url = BASE + complaint_link
            else:
                detail_url = complaint_link

            # 保存数据
            complaint_data = {
                "投诉编号": complaint_id,
                "投诉品牌": brand,
                "投诉车系": series,
                "投诉车型": model,
                "问题简述": problem_summary,
                "典型问题": typical_problem,
                "投诉时间": complaint_time,
                "投诉状态": status,
                "详情链接": detail_url,
            }

            complaints_data.append(complaint_data)

            # 每处理10条打印一次进度
            if len(complaints_data) % 10 == 0:
                print(f"  已处理 {len(complaints_data)} 条...")

        # 页面之间随机休眠
        if page_num < max_pages:
            sleep_time = random.uniform(0.5, 2.0)
            print(f"  休息 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)

    print(f"\n========== 抓取完成！==========")
    print(f"总共处理了 {len(complaints_data)} 条投诉")

    # 保存到 CSV 文件
    if complaints_data:
        filename = "complaints.csv"
        with open(filename, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "投诉编号", "投诉品牌", "投诉车系", "投诉车型",
                "问题简述", "典型问题", "投诉时间", "投诉状态", "详情链接"
            ])
            writer.writeheader()
            writer.writerows(complaints_data)
        print(f"数据已保存到 {filename}")
        return True
    else:
        print("没有获取到任何数据")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='汽车投诉爬虫 - 从车质网抓取投诉数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  uv run chezhiw.py --brands                    # 列出所有可用品牌
  uv run chezhiw.py --series 525               # 查询小鹏汽车的车系列表
  uv run chezhiw.py --models 525               # 查询小鹏汽车的具体车型列表
  uv run chezhiw.py                           # 抓取全部投诉（默认5页）
  uv run chezhiw.py --pages 10                # 抓取全部投诉10页
  uv run chezhiw.py --brand 43                # 抓取吉利汽车投诉
  uv run chezhiw.py --brand 4 --pages 20      # 抓取大众20页
        '''
    )

    parser.add_argument(
        '--brands',
        action='store_true',
        help='列出所有可用品牌及其ID'
    )

    parser.add_argument(
        '--brand',
        type=int,
        default=0,
        metavar='ID',
        help='指定品牌ID进行查询（0=全部品牌，默认：0）'
    )

    parser.add_argument(
        '--pages',
        type=int,
        default=5,
        metavar='N',
        help='抓取页数（默认：5）'
    )

    parser.add_argument(
        '--series',
        type=int,
        metavar='BRAND_ID',
        help='查询指定品牌的车系列表'
    )

    parser.add_argument(
        '--models',
        type=int,
        metavar='BRAND_ID',
        help='查询指定品牌的具体车型列表'
    )

    args = parser.parse_args()

    # 如果指定了 --brands，只列出品牌
    if args.brands:
        list_brands()
    elif args.series:
        # 查询车系列表
        series = get_series_by_brand(args.series)
        if series:
            print(f"\n找到 {len(series)} 个车系:\n")
            print("车系ID | 车系名称")
            print("-" * 60)
            for sid in sorted(series.keys(), key=lambda x: int(x) if x.isdigit() else 0):
                print(f"{sid:>6} | {series[sid]}")
        else:
            print(f"\n品牌ID {args.series} 没有找到车系信息")
    elif args.models:
        # 查询车型列表
        models = get_models_by_brand(args.models)
        if models:
            print(f"\n找到 {len(models)} 个车型:\n")
            print("车型ID | 车型名称")
            print("-" * 60)
            for mid in sorted(models.keys(), key=lambda x: int(x) if x.isdigit() else 0):
                print(f"{mid:>6} | {models[mid]}")
        else:
            print(f"\n品牌ID {args.models} 没有找到车型信息")
    else:
        # 否则抓取投诉数据
        scrape_complaints(brand_id=args.brand, max_pages=args.pages)


if __name__ == "__main__":
    main()
