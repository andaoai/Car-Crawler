---
description: 交互式查询城市汽车上牌量数据
---

# 查询城市汽车上牌量数据

使用爬虫脚本查询车主之家（16888.com）的城市汽车上牌量数据，支持按省份、城市、品牌、厂商、车型等多维度筛选。

## 功能特点

- 🔍 **多维度筛选**：支持按省份、城市、品牌、厂商、车型、月份筛选
- 📊 **灵活查询**：可查询全国、指定省份、指定城市的上牌量数据
- 🏢 **品牌查询**：支持查询特定品牌/厂商/车型的上牌量
- 📅 **历史数据**：支持查询不同月份的历史上牌量数据

## 使用流程

### 方式一：交互式查询（推荐）

使用 **AskUserQuestion** 工具与用户交互，逐步明确查询需求。

#### 步骤1：询问查询范围

**使用 AskUserQuestion 工具询问：**

```python
AskUserQuestion(questions=[
    {
        "question": "您想查询哪个范围的上牌量数据？",
        "header": "查询范围",
        "options": [
            {"label": "全国", "description": "查询全国所有城市的上牌量排行"},
            {"label": "指定省份", "description": "查询某个省份的上牌量数据"},
            {"label": "指定城市", "description": "查询某个城市的上牌量数据"},
            {"label": "指定品牌/车型", "description": "查询特定品牌或车型的上牌量"}
        ],
        "multiSelect": false
    }
])
```

#### 步骤2：根据用户选择继续询问

**如果用户选择"指定省份"：**
```python
AskUserQuestion(questions=[
    {
        "question": "请选择要查询的省份",
        "header": "省份选择",
        "options": [
            {"label": "广东", "description": "省份ID: 6"},
            {"label": "浙江", "description": "省份ID: 31"},
            {"label": "上海", "description": "直辖市ID: 25"},
            {"label": "江苏", "description": "省份ID: 16"},
            {"label": "北京", "description": "直辖市ID: 2"}
        ],
        "multiSelect": false
    }
])
```

**如果用户选择"指定城市"：**
```python
# 先询问省份
AskUserQuestion(questions=[{"question": "请选择城市所在的省份", ...}])

# 再询问具体城市
AskUserQuestion(questions=[
    {
        "question": "请选择要查询的城市",
        "header": "城市选择",
        "options": [
            {"label": "深圳", "description": "城市ID: 77"},
            {"label": "广州", "description": "城市ID: 76"},
            {"label": "杭州", "description": "城市ID: 383"},
            {"label": "宁波", "description": "城市ID: 388"}
        ],
        "multiSelect": false
    }
])
```

**如果用户选择"指定品牌/车型"：**
- ⚠️ **需要询问用户是否已知道品牌ID**
- 如果不知道，提示用户先使用"查询销量情况"获取品牌ID
- 如果知道，询问具体的品牌ID、厂商ID、车型ID

```python
AskUserQuestion(questions=[
    {
        "question": "您是否已知道要查询的品牌ID？",
        "header": "品牌ID",
        "options": [
            {"label": "已知", "description": "我已经知道品牌ID，可以直接输入"},
            {"label": "未知", "description": "需要先查询获取品牌ID"}
        ],
        "multiSelect": false
    }
])
```

#### 步骤3：询问查询月份

```python
AskUserQuestion(questions=[
    {
        "question": "请选择要查询的月份",
        "header": "月份选择",
        "options": [
            {"label": "2025-12（最新）", "description": "最新月份的数据"},
            {"label": "2025-11", "description": "上个月的数据"},
            {"label": "2024-12", "description": "去年12月的数据"},
            {"label": "其他月份", "description": "手动输入月份（YYYY-MM格式）"}
        ],
        "multiSelect": false
    }
])
```

#### 步骤4：询问抓取页数

```python
AskUserQuestion(questions=[
    {
        "question": "要抓取多少页数据？（每页约50条记录）",
        "header": "页数",
        "options": [
            {"label": "1页", "description": "约50条记录，快速查看"},
            {"label": "3页", "description": "约150条记录"},
            {"label": "5页", "description": "约250条记录（推荐）"},
            {"label": "10页", "description": "约500条记录，数据更全面"}
        ],
        "multiSelect": false
    }
])
```

#### 步骤5：执行查询

根据用户选择，构建并执行命令。

**⚠️ 不确定时，使用 AskUserQuestion 再次确认：**

- 如果用户提供的参数不明确（如省份名称不标准）
- 如果用户选择了"其他"需要手动输入
- 如果执行可能需要较长时间（超过10页）
- 如果查询条件可能导致没有数据

---

### 方式二：命令行查询（高级用户）

如果用户直接提供了具体的查询参数（省份ID、城市ID等），可以直接执行，无需询问。

## 常用命令示例

### 查看列表

```bash
# 查看所有省份
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --provinces

# 查看指定省份的城市（例如：浙江）
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --cities 31

# 查看所有级别
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --levels
```

### 基础查询

```bash
# 查询全国上牌量（默认5页）
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py

# 查询指定月份的上牌量
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --date 2024-12

# 查询指定省份的上牌量（例如：广东）
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --province 6 --pages 5

# 查询指定城市的上牌量（例如：深圳）
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --province 6 --city 77 --pages 5
```

### 品牌/车型查询

```bash
# 查询指定品牌的上牌量（需要先从销量查询获取品牌ID）
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --brand 127959 --pages 5

# 查询指定品牌和厂商的上牌量
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py --brand 127959 --factory 127960 --pages 5

# 查询指定车型的上牌量（例如：小鹏P7）
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py \
  --province 2 --brand 127959 --factory 127960 --model 128729 --pages 1

# 查询指定城市+品牌+车型的上牌量
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py \
  --province 6 --city 76 \
  --brand 127959 --factory 127960 --model 128729 \
  --date 2024-12 --pages 1
```

## 常用城市ID参考

| 直辖市 | 省份ID | 城市ID |
|--------|--------|--------|
| 北京 | 2 | 2 |
| 上海 | 25 | 25 |
| 天津 | 27 | 27 |
| 重庆 | 32 | 32 |

| 广东省城市 | 省份ID | 城市ID |
|-----------|--------|--------|
| 深圳 | 6 | 77 |
| 广州 | 6 | 76 |

| 浙江省城市 | 省份ID | 城市ID |
|-----------|--------|--------|
| 杭州 | 31 | 383 |
| 宁波 | 31 | 388 |
| 温州 | 31 | 391 |
| 嘉兴 | 31 | 385 |

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--provinces` | 列出所有省份 | `--provinces` |
| `--cities <省份ID>` | 列出指定省份的所有城市 | `--cities 31` |
| `--levels` | 列出所有级别 | `--levels` |
| `--province <省份ID>` | 按省份筛选 | `--province 6` |
| `--city <城市ID>` | 按城市筛选 | `--city 77` |
| `--brand <品牌ID>` | 按品牌筛选 | `--brand 127959` |
| `--factory <厂商ID>` | 按厂商筛选 | `--factory 127960` |
| `--model <车型ID>` | 按车型筛选 | `--model 128729` |
| `--date <年月>` | 按月份筛选（格式：YYYY-MM） | `--date 2024-12` |
| `--pages <页数>` | 抓取页数（默认：5） | `--pages 10` |

## 输出文件

数据将保存到 `out` 目录下的 CSV 文件，文件名格式：

```
城市上牌量_[月份]_[省份]_[筛选条件]_[日期].csv
```

示例：
- `out/城市上牌量_2024-12.csv`
- `out/城市上牌量_2024-12_广东.csv`
- `out/城市上牌量_2024-12_广东_品牌127959.csv`
- `out/城市上牌量_2024-12_广东_品牌127959_厂商127960_车型128729_20260130.csv`

### CSV 字段说明

- **排名**：该车型在指定区域的上牌量排名
- **车型**：汽车型号名称
- **城市**：城市名称
- **上牌量**：上牌数量
- **级别**：车型级别（如：中型车、SUV、MPV等）
- **指导价（万元）**：官方指导价格

## 获取品牌/厂商/车型ID

品牌、厂商、车型的ID需要从销量查询脚本获取：

```bash
# 1. 查看所有品牌
uv run .claude/skills/查询销量情况/crawler_16888_sales.py --brands

# 2. 查看指定品牌的厂商
uv run .claude/skills/查询销量情况/crawler_16888_sales.py --facturers 127959

# 3. 查看指定厂商的车型
uv run .claude/skills/查询销量情况/crawler_16888_sales.py --series 127960
```

## 实际应用案例

### 案例1：对比小鹏P7在广州和宁波的上牌量

```bash
# 查询广州2024年小鹏P7上牌量
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py \
  --province 6 --city 76 \
  --brand 127959 --factory 127960 --model 128729 \
  --date 2024-12 --pages 1

# 查询宁波2024年小鹏P7上牌量
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py \
  --province 31 --city 388 \
  --brand 127959 --factory 127960 --model 128729 \
  --date 2024-12 --pages 1
```

### 案例2：查询浙江省所有品牌上牌量排行

```bash
uv run .claude/skills/查询城市上牌量/crawler_city_registration.py \
  --province 31 \
  --date 2024-12 \
  --pages 10
```

## 何时使用 AskUserQuestion

### ✅ 必须询问的情况

1. **用户需求不明确时**
   - 用户只说"查询上牌量"，没有指定具体范围
   - 用户说"查询广东"，但不清楚是要全省还是某个城市
   - 用户说"查询小鹏"，但不清楚是品牌还是具体车型

2. **需要用户做出选择时**
   - 选择省份、城市、月份、页数等
   - 选择查询维度（全国/省份/城市/品牌）

3. **用户可能缺少必要信息时**
   - 用户要查品牌车型，但可能不知道品牌ID
   - 用户选择"其他"选项，需要手动输入

4. **执行前需要确认时**
   - 查询范围很大（如全国10页，可能需要较长时间）
   - 查询条件可能导致没有数据（如过时的月份）

### ❌ 不需要询问的情况

1. **用户需求明确时**
   - 用户直接说"查询深圳2024年12月小鹏P7上牌量"
   - 用户提供了具体的省份ID、城市ID等参数

2. **简单明确的查询**
   - 只查询1页数据
   - 常见城市（深圳、广州、杭州、宁波等）

3. **用户已经表现出明确意图**
   - "帮我查一下浙江省"
   - "看看小鹏P7在广州的表现"

### 💡 使用技巧

**询问前，先提供信息：**
```python
# 先列出选项，让用户看到可用范围
print("可查询的省份包括：")
print("- 广东（ID: 6）")
print("- 浙江（ID: 31）")
print("- 上海（ID: 25）")
print("- ...")

# 然后再使用 AskUserQuestion 询问
```

**询问时，提供清晰的描述：**
```python
{
    "question": "请选择要查询的省份",
    "header": "省份选择",
    "options": [
        {"label": "广东", "description": "经济大省，包含深圳、广州等城市"},
        {"label": "浙江", "description": "包含杭州、宁波等城市"}
    ]
}
```

**不确定用户意图时，主动提供帮助：**
```python
# 如果用户说"查询小鹏"
AskUserQuestion(questions=[{
    "question": "您想查询小鹏的什么数据？",
    "header": "查询范围",
    "options": [
        {"label": "小鹏品牌所有车型", "description": "查询小鹏品牌全部车型的上牌量"},
        {"label": "特定车型", "description": "查询指定车型（如小鹏P7）的上牌量"}
    ]
}])
```

---

## 注意事项

1. **获取城市ID**：
   - 使用 `--provinces` 查看所有省份
   - 使用 `--cities <省份ID>` 查看该省的城市列表
   - 直辖市（北京、上海、天津、重庆）的城市ID与省份ID相同

2. **品牌ID获取**：
   - 需要先使用销量查询脚本获取品牌/厂商/车型ID
   - 不要随意编造ID，否则可能查询不到数据

3. **月份格式**：
   - 必须使用 `YYYY-MM` 格式
   - 例如：`2024-12`、`2025-01`

4. **数据时效性**：
   - 网站数据更新可能有一定延迟
   - 最新月份的数据可能不完整

5. **合理使用频率**：
   - 避免过于频繁的请求
   - 建议每次查询间隔至少1-2秒
   - 大量数据查询时分批次进行

## 数据分析建议

获取数据后，可以使用Python进行进一步分析：

```python
import pandas as pd

# 读取CSV文件
df = pd.read_csv('out/城市上牌量_2024-12_广东.csv', encoding='utf-8-sig')

# 查看前10名
print(df.head(10))

# 统计总上牌量
print(f"总上牌量: {df['上牌量'].sum()}")

# 按级别分组统计
print(df.groupby('级别')['上牌量'].sum().sort_values(ascending=False))
```
