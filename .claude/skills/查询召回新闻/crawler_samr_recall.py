# -*- coding: utf-8 -*-
# 汽车召回新闻爬虫 - 从国家市场监督管理总局抓取召回新闻
import requests
import time
import csv
import random
import argparse
import sys
import io
import os
import base64
from datetime import datetime

# 修复 Windows 控制台中文乱码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# API 基础配置
API_BASE = "https://qxzh.samr.gov.cn"
API_URL = f"{API_BASE}/qxzh/frame/car/siteNews"

# 全局headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://qxzh.samr.gov.cn",
    "Referer": "https://qxzh.samr.gov.cn/qxzh/qxxxcx/web.jsp",
    "X-Requested-With": "XMLHttpRequest",
}


def base16_encode(text):
    """使用Base16编码（实际上是Base64编码）"""
    # 转换为bytes
    text_bytes = text.encode('utf-8')
    # Base64编码
    encoded = base64.b64encode(text_bytes)
    # 转回字符串
    return encoded.decode('utf-8')


def api_request_recall(keyword="", page_no=1, page_size=20):
    """封装召回新闻API请求

    Args:
        keyword: 搜索关键词（品牌名、车型等）
        page_no: 页码（从1开始）
        page_size: 每页数量（默认20）

    Returns:
        dict: API响应JSON数据，失败返回None
    """
    # 使用Base16（Base64）编码每个参数值
    data = {
        "keyword": base16_encode(keyword),
        "pageNo": base16_encode(str(page_no)),
        "pageSize": base16_encode(str(page_size)),
    }

    try:
        response = requests.post(API_URL, headers=headers, data=data, timeout=15)
        response.encoding = response.apparent_encoding
        result = response.json()

        # 检查响应状态
        if result.get("successful"):
            return result
        else:
            print(f"API返回错误: {result.get('message', '未知错误')}")
            return None

    except requests.exceptions.Timeout:
        print(f"  请求超时")
        return None
    except requests.exceptions.ConnectionError:
        print(f"  网络连接失败")
        return None
    except Exception as e:
        print(f"  API请求失败: {e}")
        return None


def parse_recall_item(item):
    """解析单条召回新闻数据

    Args:
        item: API返回的单条数据（dict）

    Returns:
        dict: 标准化的召回新闻记录
    """
    # 处理详情链接
    docpuburl = item.get("docpuburl", "")
    if docpuburl and not docpuburl.startswith("http"):
        if docpuburl.startswith("/"):
            docpuburl = f"{API_BASE}{docpuburl}"
        else:
            docpuburl = f"{API_BASE}/{docpuburl}"

    return {
        "新闻标题": item.get("doctitle", ""),
        "发布时间": item.get("docreltime", ""),
        "涉及品牌": item.get("brandname", ""),
        "一级总成": item.get("dicdesc", ""),
        "详情链接": docpuburl,
    }


def filter_by_date(recall_data, start_date=None, end_date=None):
    """按日期筛选召回新闻

    Args:
        recall_data: 召回新闻列表
        start_date: 起始日期（格式：YYYY-MM-DD）
        end_date: 结束日期（格式：YYYY-MM-DD）

    Returns:
        list: 筛选后的召回新闻列表
    """
    if not start_date and not end_date:
        return recall_data

    filtered_data = []
    for item in recall_data:
        pub_time = item.get("发布时间", "")
        if not pub_time:
            continue

        try:
            # 解析日期（假设格式为 "2024-01-15" 或 "2024-01-15 10:30:00"）
            item_date = pub_time.split(" ")[0]

            if start_date and item_date < start_date:
                continue
            if end_date and item_date > end_date:
                continue

            filtered_data.append(item)
        except Exception:
            continue

    return filtered_data


def scrape_recall_news(keyword="", max_pages=5, page_size=20):
    """抓取召回新闻数据

    Args:
        keyword: 搜索关键词，空字符串表示全部
        max_pages: 最大抓取页数
        page_size: 每页数量

    Returns:
        list: 召回新闻记录列表
    """
    recall_data = []

    # 生成查询描述
    query_desc = f"关键词='{keyword}'" if keyword else "全部召回新闻"
    print(f"开始抓取召回新闻...")
    print(f"查询条件: {query_desc}")
    print(f"将抓取第 1 到第 {max_pages} 页")

    for page_num in range(1, max_pages + 1):
        print(f"\n========== 正在抓取第 {page_num}/{max_pages} 页 ==========")

        # 调用API
        result = api_request_recall(keyword=keyword, page_no=page_num, page_size=page_size)

        if not result:
            print(f"  第 {page_num} 页请求失败，跳过")
            continue

        # 解析响应
        rows = result.get("rows", [])
        total = int(result.get("total", 0))
        total_page = int(result.get("totalpage", 0))

        if not rows:
            print(f"  本页没有数据，停止抓取")
            break

        print(f"  本页有 {len(rows)} 条记录")
        if total_page > 0:
            print(f"  总共 {total} 条记录，共 {total_page} 页")

        # 解析每条记录
        for item in rows:
            recall_record = parse_recall_item(item)
            recall_data.append(recall_record)

        # 进度报告
        if len(recall_data) % 10 == 0:
            print(f"  已处理 {len(recall_data)} 条...")

        # 页面间随机休眠
        if page_num < max_pages:
            # 如果已经超过总页数，停止抓取
            if total_page > 0 and page_num >= total_page:
                print(f"  已到达最后一页，停止抓取")
                break

            sleep_time = random.uniform(0.5, 2.0)
            print(f"  休息 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)

    print(f"\n========== 抓取完成！==========")
    print(f"总共处理了 {len(recall_data)} 条召回新闻")

    return recall_data


def generate_filename(keyword="", date_str=None):
    """生成输出文件名

    Args:
        keyword: 搜索关键词
        date_str: 日期字符串（YYYYMMDD）

    Returns:
        str: 文件名
    """
    if not date_str:
        date_str = datetime.now().strftime("%Y%m%d")

    # 构建文件名：召回新闻_[关键词]_[日期].csv
    filename_parts = ["召回新闻"]
    if keyword:
        # 清理关键词中的非法字符
        clean_keyword = keyword.replace("/", "-").replace("\\", "-").replace(":", "").replace("?", "").replace("*", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "")
        filename_parts.append(clean_keyword)
    filename_parts.append(date_str)

    return "_".join(filename_parts) + ".csv"


def save_to_csv(recall_data, filename):
    """保存召回新闻到CSV文件

    Args:
        recall_data: 召回新闻列表
        filename: 输出文件名

    Returns:
        bool: 成功返回True，失败返回False
    """
    if not recall_data:
        print("没有数据需要保存")
        return False

    # 创建out目录
    os.makedirs("out", exist_ok=True)

    # 完整路径
    filepath = os.path.join("out", filename)

    try:
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "新闻标题", "发布时间", "涉及品牌", "一级总成", "详情链接"
            ])
            writer.writeheader()
            writer.writerows(recall_data)

        print(f"\n数据已保存到 {filepath}")
        print(f"共 {len(recall_data)} 条记录")
        return True

    except Exception as e:
        print(f"保存文件失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='汽车召回新闻爬虫 - 从国家市场监督管理总局抓取召回新闻',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  # 抓取全部召回新闻（默认5页）
  uv run .claude/skills/查询召回新闻/crawler_samr_recall.py

  # 按关键词搜索召回新闻
  uv run .claude/skills/查询召回新闻/crawler_samr_recall.py --keyword "奔驰"

  # 抓取更多页数
  uv run .claude/skills/查询召回新闻/crawler_samr_recall.py --keyword "特斯拉" --pages 10

  # 指定每页数量
  uv run .claude/skills/查询召回新闻/crawler_samr_recall.py --page-size 50

  # 按日期筛选
  uv run .claude/skills/查询召回新闻/crawler_samr_recall.py --start-date "2024-01-01" --end-date "2024-12-31"

  # 组合使用
  uv run .claude/skills/查询召回新闻/crawler_samr_recall.py --keyword "比亚迪" --pages 20 --start-date "2024-01-01"
        '''
    )

    parser.add_argument(
        '--keyword',
        type=str,
        default="",
        metavar='KEYWORD',
        help='搜索关键词（品牌名、车型等，默认：全部）'
    )

    parser.add_argument(
        '--pages',
        type=int,
        default=5,
        metavar='N',
        help='抓取页数（默认：5）'
    )

    parser.add_argument(
        '--page-size',
        type=int,
        default=20,
        metavar='N',
        help='每页数量（默认：20）'
    )

    parser.add_argument(
        '--start-date',
        type=str,
        metavar='YYYY-MM-DD',
        help='起始日期（格式：YYYY-MM-DD）'
    )

    parser.add_argument(
        '--end-date',
        type=str,
        metavar='YYYY-MM-DD',
        help='结束日期（格式：YYYY-MM-DD）'
    )

    args = parser.parse_args()

    # 抓取召回新闻
    recall_data = scrape_recall_news(
        keyword=args.keyword,
        max_pages=args.pages,
        page_size=args.page_size
    )

    # 按日期筛选（如果指定）
    if args.start_date or args.end_date:
        print(f"\n正在按日期筛选...")
        recall_data = filter_by_date(recall_data, args.start_date, args.end_date)
        print(f"日期筛选后剩余 {len(recall_data)} 条记录")

    # 保存到CSV
    if recall_data:
        date_str = datetime.now().strftime("%Y%m%d")
        filename = generate_filename(keyword=args.keyword, date_str=date_str)
        save_to_csv(recall_data, filename)
    else:
        print("\n没有获取到任何召回新闻数据")
        print("可能原因:")
        print("  1. 关键词没有匹配结果")
        print("  2. 网络连接问题")
        print("  3. API接口暂时不可用")
        print("\n建议:")
        print("  - 尝试使用更通用的关键词")
        print("  - 检查网络连接")
        print("  - 稍后再试")


if __name__ == "__main__":
    main()
