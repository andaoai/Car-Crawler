# 汽车投诉爬虫 - 列表页抓取并解析详情链接（requests + bs4）
import requests
from bs4 import BeautifulSoup
import time
import re
import csv
import random

BASE = "https://www.12365auto.com"
# URL模板，页码可变
LIST_URL_TEMPLATE = "https://www.12365auto.com/zlts/0-0-0-0-0-0_0-0-0-1-0-0-0-{page}.shtml"

# 设置要抓取的页数
START_PAGE = 1
MAX_PAGES = 5  # 抓取前5页

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.12365auto.com/",
})

# 存储所有投诉数据
complaints_data = []

# 投诉详情链接的格式: //www.12365auto.com/zlts/日期/ID.shtml
complaint_pattern = re.compile(r'//www\.12365auto\.com/zlts/\d{8}/\d+\.shtml$')

print(f"开始抓取投诉数据...")
print(f"将抓取第 {START_PAGE} 到第 {MAX_PAGES} 页")

# 遍历每一页
for page_num in range(START_PAGE, MAX_PAGES + 1):
    url = LIST_URL_TEMPLATE.format(page=page_num)
    print(f"\n========== 正在抓取第 {page_num}/{MAX_PAGES} 页: {url} ==========")

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
    print(f"  本页有 {page_count} 条投诉记录")

    for row in rows[1:]:  # 跳过表头
        tds = row.find_all("td")
        if not tds or len(tds) < 8:
            continue

        # 从列表页提取基本信息
        complaint_id = tds[0].get_text(strip=True)  # 投诉编号
        brand = tds[1].get_text(strip=True)  # 投诉品牌
        series = tds[2].get_text(strip=True)  # 投诉车系
        model = tds[3].get_text(strip=True)  # 投诉车型
        problem_summary = tds[4].get_text(strip=True)  # 问题简述
        typical_problem = tds[5].get_text(strip=True)  # 典型问题
        complaint_time = tds[6].get_text(strip=True)  # 投诉时间
        status = tds[7].get_text(strip=True)  # 投诉状态

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

    # 页面之间随机休眠，避免被反爬
    if page_num < MAX_PAGES:
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
else:
    print("没有获取到任何数据")
