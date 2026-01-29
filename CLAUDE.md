# CarCrawler - 汽车数据爬虫查询工具

本项目是一个用于查询汽车相关数据的爬虫工具集，使用 **uv** 作为包管理器和运行环境。

## 环境管理

本项目使用 [uv](https://github.com/astral-sh/uv) 进行依赖管理和环境隔离。

### 重要：运行方式

**所有 Python 脚本都必须使用 `uv run` 前缀来运行：**

```bash
# ✅ 正确的运行方式
uv run script.py

# ❌ 错误的运行方式（会导致依赖缺失）
python script.py
```

### 安装依赖

```bash
uv sync
```

## 项目功能

本项目包含两个主要的数据查询功能：

### 1. 汽车投诉情况查询

- **数据源**: 车质网 (12365auto.com)
- **爬虫脚本**: [`.claude/skills/查询投诉情况/crawler_12365_zlts.py`](.claude/skills/查询投诉情况/crawler_12365_zlts.py)
- **输出文件**: `complaints.csv`

**支持的操作：**
- 查询所有品牌的投诉数据
- 按品牌筛选
- 按车系筛选
- 按车型筛选
- 自定义抓取页数

**交互式查询：**
使用 Skill 工具调用 `查询投诉情况` 可进行交互式查询。

### 2. 汽车销量情况查询

- **数据源**: 16888.com
- **爬虫脚本**: [`.claude/skills/查询销量情况/crawler_16888_sales.py`](.claude/skills/查询销量情况/crawler_16888_sales.py)
- **输出文件**: `sales.csv`

**支持的操作：**
- 查询品牌销量排行
- 查询车型销量排行
- 按时间周期筛选

**交互式查询：**
使用 Skill 工具调用 `查询销量情况` 可进行交互式查询。

## 开发指南

### 添加新的爬虫脚本

1. 将爬虫脚本放在 `.claude/skills/` 目录下的对应功能文件夹中
2. 确保脚本可以直接通过 `uv run` 运行
3. 在 `pyproject.toml` 中添加所需的依赖
4. 运行 `uv sync` 安装新依赖

### 依赖管理

所有依赖都在 [`pyproject.toml`](pyproject.toml) 中定义：

```toml
[project]
name = "car-crawler"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "beautifulsoup4>=4.14.3",
    "lxml>=6.0.2",
    "requests>=2.32.5",
]
```

添加新依赖后，运行：
```bash
uv sync
```

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
├── complaints.csv        # 投诉数据输出
├── sales.csv            # 销量数据输出
└── README.md            # 项目文档
```

## 注意事项

1. **始终使用 `uv run`**：运行任何 Python 脚本前都要加上 `uv run`
2. **遵守网站规则**：爬虫应遵守目标网站的 robots.txt 和使用条款
3. **合理使用频率**：避免过于频繁的请求，以免对目标服务器造成压力
4. **数据使用规范**：爬取的数据仅供学习交流使用，请勿用于商业用途
