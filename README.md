# Personal Finance Analysis — 2023–2024

## Overview
End-to-end data analysis project analyzing 2 years of personal
finance transactions across 10 spending categories.

**Tools used:** Python · SQL (SQLite) · Power BI · Excel

## Key findings
- Average savings rate of 26.7% over 24 months
- March 2024 was the only negative-savings month (–$477)
  due to a double housing payment — flagged as an anomaly
- Transportation costs grew 17% YOY — largest category increase
- 42% of all spending used credit cards

## Project structure
| File | Description |
|------|-------------|
| `data/finance_transactions.csv` | 765-row synthetic dataset |
| `sql/finance_analysis.sql` | 8 analytical SQL queries |
| `python/finance_data_generation.py` | Data generation + 3 charts |
| `images/` | Chart exports and dashboard screenshots |

## SQL skills demonstrated
- GROUP BY, aggregations, CASE WHEN
- JOIN across multiple tables
- HAVING to filter aggregated results
- Window functions: SUM() OVER(), AVG() OVER(ROWS PRECEDING)
- CTEs for rolling averages

## Power BI dashboard
[View live dashboard →](https://app.powerbi.com/your-link-here)

![Dashboard preview](images/powerbi_dashboard.png)

## How to run the Python script
```bash
pip install pandas numpy matplotlib
python python/finance_data_generation.py
```
