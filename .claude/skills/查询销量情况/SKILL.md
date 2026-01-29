---
description: 交互式查询汽车销量数据
---

# 查询汽车销量数据

使用爬虫脚本查询车主之家（16888.com）的汽车销量数据。

## 使用流程

1. **列出所有厂商**（如果用户不确定厂商ID）：
   ```bash
   uv run .claude/skills/查询销量情况/crawler_16888_sales.py --brands
   ```

2. **使用 AskUserQuestion 工具询问用户需求**：
   - 询问要查询哪个厂商（使用 AskUserQuestion，选项包括常见厂商或"其他"让用户输入）
   - 询问需要抓取多少页（使用 AskUserQuestion，默认5页，选项：3页、5页、10页、20页）

3. **执行查询**：
   根据用户选择，运行对应的命令：
   ```bash
   # 全部厂商
   uv run .claude/skills/查询销量情况/crawler_16888_sales.py --sales --pages N

   # 指定厂商（当前版本不支持厂商筛选，可以后续扩展）
   ```

## 输出文件

数据将保存到 `sales.csv`，包含以下字段：
- 厂商
- 品牌
- 车系
- 车型
- 销量
- 排名
- 时间

## 注意事项

- 如果用户不确定厂商ID，先运行 `--brands` 命令列出选项
- 抓取完成后，告知用户数据已保存到 sales.csv
- 可以用 Python 读取 CSV 并做简单的数据统计（如总销量、平均销量、排名等）
