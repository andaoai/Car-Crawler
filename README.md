# 汽车数据爬虫工具集

一个用于查询和抓取汽车相关数据的 Python 命令行工具集，支持汽车投诉情况和销量数据的采集与分析。

## 项目概述

CarCrawler 是一个专注于汽车领域的数据爬虫工具，旨在帮助用户快速获取和分析汽车投诉、销量等相关数据。所有数据均导出为 CSV 格式，方便进行后续的数据分析和可视化处理。

## 主要功能

### 1. 汽车投诉情况查询

- 支持按品牌、车系、车型抓取投诉数据
- 支持自定义抓取页数
- 数据来源：车质网（12365auto.com）
- 包含完整的投诉信息（编号、品牌、车系、车型、问题简述、时间、状态等）

### 2. 汽车销量情况查询

- 支持查询品牌销量排行
- 支持查询车型销量排行
- 数据来源：车主之家（16888.com）
- 包含销量、排名、厂商、品牌等详细信息

### 数据分析应用

采集的数据可用于：
- 汽车品牌投诉率分析
- 车型质量趋势研究
- 销量与投诉关联性分析
- 市场竞争力评估
- 消费者购买决策参考

## 环境要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) 包管理器

## 安装

```bash
# 安装依赖
uv sync
```

## 快速开始

### 汽车投诉查询

```bash
# 1. 列出所有品牌
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brands

# 2. 查询指定品牌的车系
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --series 525

# 3. 抓取投诉数据（小鹏P7，5页）
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brand 525 --series-id 2820 --pages 5
```

### 汽车销量查询

```bash
# 1. 查询销量排行
uv run .claude/skills/查询销量情况/crawler_16888_sales.py --sales --pages 5
```

## 详细使用方法

### 汽车投诉数据查询

#### 1. 查看帮助

```bash
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --help
```

#### 2. 列出所有可用品牌

```bash
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brands
```

### 2. 列出所有可用品牌

```bash
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brands
```

输出示例：
```
品牌ID | 品牌名称
---------------------
     1 | 北京奔驰
     4 | 一汽-大众
     8 | 东风日产
    19 | 上汽大众
    26 | 一汽奥迪
    43 | 吉利汽车
   525 | 小鹏汽车
```

### 3. 查询车系和车型

#### 查询指定品牌的车系列表

```bash
# 查询小鹏汽车的车系
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --series 525
```

输出示例：
```
车系ID | 车系名称
---------------------
  3178 | 小鹏P7
  3179 | 小鹏P5
  3180 | 小鹏G3
  3181 | 小鹏G9
  3182 | 小鹏G6
  ...
```

#### 查询指定车系的具体车型

```bash
# 查询小鹏P7车系的具体车型（需要品牌ID和车系ID两个参数）
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --models 525 3178
```

输出示例：
```
车型ID | 车型名称
---------------------
 12345 | 2020款 670E
 12346 | 2020款 706G
 12347 | 2021款 480E
 12348 | 2022款 480 标准续航 智行版
 ...
```

### 4. 抓取投诉数据

#### 抓取全部品牌（默认5页）

```bash
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py
```

#### 抓取全部品牌10页

```bash
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --pages 10
```

#### 抓取指定品牌

```bash
# 抓取吉利汽车（品牌ID=43）
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brand 43

# 抓取一汽-大众（品牌ID=4）20页
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brand 4 --pages 20
```

#### 按车系筛选

```bash
# 抓取小鹏汽车P7车系（品牌ID=525，车系ID=2820）的投诉
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brand 525 --series-id 2820
```

#### 按车型筛选

```bash
# 抓取小鹏汽车2020款 670E车型（品牌ID=525，车型ID=46068）的投诉
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brand 525 --model-id 46068
```

### 5. 使用流程示例

完整的查询流程示例：

```bash
# 1. 首先列出所有品牌，找到小鹏汽车的ID
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brands
# 输出：525 | 小鹏汽车

# 2. 查询小鹏汽车的所有车系
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --series 525
# 输出：2820 | 小鹏P7
#      3660 | 小鹏G6
#      ...

# 3. 查询小鹏P7车系的具体车型
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --models 525 2820
# 输出：46068 | 2020款 670E
#      78226 | 2025款 702 长续航 Ultra
#      ...

# 4. 抓取小鹏P7车系的所有投诉
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brand 525 --series-id 2820 --pages 5

# 5. 抓取特定车型（2020款 670E）的投诉
uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brand 525 --model-id 46068 --pages 3
```

> ⚠️ **重要提示**：使用 `--series-id` 或 `--model-id` 时，请确保使用正确的ID。可以先通过 `--series` 和 `--models` 命令查询真实的ID值。

### 汽车销量数据查询

#### 查询销量排行

```bash
# 查询销量数据（默认5页）
uv run .claude/skills/查询销量情况/crawler_16888_sales.py --sales

# 查询销量数据（指定页数）
uv run .claude/skills/查询销量情况/crawler_16888_sales.py --sales --pages 10
```

## 数据分析应用示例

采集的 CSV 数据可用于以下分析场景：

```python
import pandas as pd

# 读取投诉数据（使用实际的文件名）
df_complaints = pd.read_csv('投诉_小鹏汽车_小鹏P7_20250129.csv')

# 分析示例
print(f"总投诉数: {len(df_complaints)}")
print(f"投诉状态分布:\n{df_complaints['投诉状态'].value_counts()}")
print(f"最常见的5个问题:\n{df_complaints['典型问题'].value_counts().head(5)}")

# 读取销量数据（使用实际的文件名）
df_sales = pd.read_csv('销量排行_20250129.csv')
print(f"销量统计:\n{df_sales.describe()}")
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--brands` | 列出所有可用品牌及其ID |
| `--series BRAND_ID` | 查询指定品牌的车系列表 |
| `--models BRAND_ID SERIES_ID` | 查询指定品牌和车系的具体车型列表（需要两个参数） |
| `--brand ID` | 指定品牌ID进行查询（0=全部品牌，默认：0） |
| `--series-id ID` | 指定车系ID进行筛选（0=全部车系，默认：0） |
| `--model-id ID` | 指定车型ID进行筛选（0=全部车型，默认：0） |
| `--pages N` | 抓取页数（默认：5） |

## 输出文件

### 投诉数据

文件名格式：`投诉_[品牌]_[车系]_[日期].csv`

示例：
- 全部品牌：`投诉_20250129.csv`
- 特定品牌：`投诉_小鹏汽车_20250129.csv`
- 特定车系：`投诉_小鹏汽车_小鹏P7_20250129.csv`

包含以下字段：

| 字段 | 说明 |
|------|------|
| 投诉编号 | 唯一投诉ID |
| 投诉品牌 | 汽车品牌 |
| 投诉车系 | 具体车系 |
| 投诉车型 | 年款和配置 |
| 问题简述 | 投诉问题概述 |
| 典型问题 | 典型问题标签 |
| 投诉时间 | 投诉提交时间 |
| 投诉状态 | 处理状态 |
| 详情链接 | 投诉详情页URL |

### 销量数据

文件名格式：`销量排行_[日期].csv`

示例：
- `销量排行_20250129.csv`

包含以下字段：

| 字段 | 说明 |
|------|------|
| 厂商 | 汽车厂商 |
| 品牌 | 汽车品牌 |
| 车系 | 具体车系 |
| 车型 | 年款和配置 |
| 销量 | 销售数量 |
| 排名 | 销量排名 |
| 时间 | 统计时间 |

## 常见品牌ID参考

```
品牌ID  | 品牌名称
--------|------------------
 0      | 全部品牌
 1      | 奔驰
 4      | 大众
 8      | 本田
 15     | 丰田
 19     | 大众
 26     | 福特
 43     | 吉利汽车
 68     | 马自达
 140    | 领克
 525    | 小鹏汽车
```

> 💡 提示：运行 `uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brands` 可以获取完整的 381 个品牌列表

## 注意事项

1. **遵守网站规则**：请遵守目标网站的 robots.txt 协议和使用条款
2. **合理使用频率**：建议在抓取时添加适当的延迟，避免对服务器造成过大压力
3. **数据使用规范**：此工具仅供学习交流使用，数据请勿用于商业用途
4. **数据验证**：建议对爬取的数据进行验证和清洗后再用于分析
5. **版权声明**：数据来源于车质网（12365auto.com）和车主之家（16888.com）

## 技术栈

- **运行环境**：Python 3.10+
- **包管理器**：uv - 快速的 Python 包管理器
- **网络请求**：requests - HTTP 请求库
- **HTML 解析**：BeautifulSoup4 + lxml - 高效的 HTML 解析
- **数据处理**：pandas（可选）- 数据分析和处理
- **命令行工具**：argparse - 命令行参数解析

## 项目结构

```
CarCrawler/
├── .claude/
│   └── skills/
│       ├── 查询投诉情况/
│       │   ├── SKILL.md
│       │   └── crawler_12365_zlts.py
│       └── 查询销量情况/
│           ├── SKILL.md
│           ├── SKILL.yaml
│           └── crawler_16888_sales.py
├── .venv/                 # uv 创建的虚拟环境
├── pyproject.toml         # 项目配置和依赖
├── uv.lock               # 锁定的依赖版本
├── CLAUDE.md             # Claude Code 项目说明
├── 投诉_*.csv           # 投诉数据输出（自动生成文件名）
├── 销量排行_*.csv       # 销量数据输出（自动生成文件名）
└── README.md            # 项目文档
```

## License

MIT License

## 相关资源

- [车质网](https://www.12365auto.com/) - 汽车投诉数据来源
- [车主之家](https://www.16888.com/) - 汽车销量数据来源
- [uv 文档](https://github.com/astral-sh/uv) - Python 包管理器

## 未来规划

- [ ] 支持更多数据源（汽车评测、价格等）
- [ ] 添加数据可视化功能
- [ ] 支持导出为其他格式（JSON、Excel）
- [ ] 提供 Web 界面
- [ ] 添加数据分析报告自动生成功能
