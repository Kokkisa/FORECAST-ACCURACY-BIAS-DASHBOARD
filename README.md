# FORECAST-ACCURACY-BIAS-DASHBOARD
Build a Streamlit dashboard that tracks forecast accuracy, bias, and attainment by SKU, category, and month. The tool every demand planning team needs but most don't have.
[README_project11.md](https://github.com/user-attachments/files/25768635/README_project11.md)
# 📊 Forecast Accuracy & Bias Dashboard

## Overview
Interactive Streamlit dashboard that monitors demand forecast performance across products, categories, regions, and time periods. Tracks MAPE, Bias, Forecast Accuracy, Weighted MAPE, and Attainment — the five key metrics every demand planning organization needs.

**Built by:** Nithin Kumar Kokkisa — Senior Demand Planner with 12+ years at HPCL managing 180,000 MTPA facility.

---

## Business Problem
Demand planners create monthly forecasts, but without systematic monitoring, errors compound silently. Over-forecasting (positive bias) ties up capital in excess inventory. Under-forecasting (negative bias) causes stockouts and lost sales. This dashboard provides real-time visibility into forecast health so planners know WHERE to focus improvement efforts.

## Key Metrics Tracked

| Metric | Formula | What It Tells You |
|--------|---------|-------------------|
| **MAPE** | mean(\|Forecast - Actual\| / Actual) × 100 | How far off are we? (error magnitude) |
| **Bias** | mean((Forecast - Actual) / Actual) × 100 | Are we consistently over or under? |
| **FA%** | 100 - MAPE | Forecast accuracy (higher = better) |
| **WMAPE** | Σ\|Error\| / Σ\|Actual\| × 100 | Revenue-weighted accuracy |
| **Attainment** | % of SKUs within ±20% of actual | Portfolio reliability |

## Dashboard Features

- **6 KPI Cards**: MAPE, Bias, FA%, WMAPE, Attainment, Total Demand
- **Interactive Filters**: Category, Region, Month (sidebar)
- **Monthly Trend**: MAPE and Bias over 12 months with targets
- **MAPE Heatmap**: Category × Month — instantly spot accuracy hotspots
- **Calibration Scatter**: Actual vs Forecast with ±20% bands
- **Dimensional Drill-Down**: Tabs for Category, Region, Product-level detail
- **Color-Coded Tables**: Product performance ranked by MAPE

## Visualizations

| Chart | Business Insight |
|-------|-----------------|
| Monthly MAPE Trend | Are forecasts improving or degrading over time? |
| Monthly Bias Bars | Which months have systematic over/under-forecasting? |
| Category × Month Heatmap | Which category-month combinations need attention? |
| Actual vs Forecast Scatter | Overall calibration — are forecasts centered? |
| Top/Bottom Products | Where to focus improvement efforts |
| Attainment Distribution | What % of the portfolio is within acceptable range? |

## How to Run

```bash
pip install -r requirements.txt
streamlit run forecast_dashboard.py
```

## Tools & Technologies
- **Python** (Pandas, NumPy)
- **Streamlit** (Interactive dashboard framework)
- **Plotly** (Interactive charts)

## Domain Expertise Applied
- MAPE vs WMAPE distinction (volume-weighted accuracy for business impact)
- Bias decomposition by region reveals systematic planning errors
- Attainment metric provides portfolio-level reliability view
- Seasonal accuracy patterns inform model adjustment timing

---

## About
Part of a **30-project data analytics portfolio**. See [GitHub profile](https://github.com/Kokkisa) for the full portfolio.
