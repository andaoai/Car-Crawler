---
description: 交互式查询汽车投诉数据
---

# 查询汽车投诉数据

使用爬虫脚本查询车质网（12365auto.com）的汽车投诉数据。

## 使用流程

1. **列出所有品牌**（如果用户不确定品牌ID）：
   ```bash
   uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brands
   ```

2. **使用 AskUserQuestion 工具询问用户需求**：
   - 询问要查询哪个品牌（使用 AskUserQuestion，选项包括常见品牌或"其他"让用户输入）
   - 询问是否需要筛选特定车系（如果需要，先运行 `--series` 查询，再用 AskUserQuestion 让用户选择）
   - 询问是否需要筛选特定车型（如果需要，运行 `--models` 查询，再用 AskUserQuestion 让用户选择）
   - 询问需要抓取多少页（使用 AskUserQuestion，默认5页，选项：3页、5页、10页、20页）

3. **执行查询**：
   根据用户选择，运行对应的命令：
   ```bash
   # 全部品牌
   uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --pages N

   # 指定品牌
   uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brand BRAND_ID --pages N

   # 指定品牌+车系
   uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brand BRAND_ID --series-id SERIES_ID --pages N

   # 指定品牌+车系+车型
   uv run .claude/skills/查询投诉情况/crawler_12365_zlts.py --brand BRAND_ID --model-id MODEL_ID --pages N
   ```

## 输出文件

数据将保存到 `complaints.csv`，包含以下字段：
- 投诉编号
- 投诉品牌
- 投诉车系
- 投诉车型
- 问题简述
- 典型问题
- 投诉时间
- 投诉状态
- 详情链接

## 注意事项

- 如果用户不确定品牌、车系或车型ID，先运行对应的查询命令列出选项
- 抓取完成后，告知用户数据已保存到 complaints.csv
- 可以用 Python 读取 CSV 并做简单的数据统计（如投诉数量、最常见的故障类型等）
