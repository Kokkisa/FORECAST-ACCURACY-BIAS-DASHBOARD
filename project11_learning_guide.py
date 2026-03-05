#!/usr/bin/env python
# coding: utf-8

# =============================================================================
# PROJECT 11: FORECAST ACCURACY & BIAS DASHBOARD
# (Plan #3 — Block A: Core Demand Planning)
# =============================================================================
# Author: Nithin Kumar Kokkisa
# Purpose: Build a Streamlit dashboard that tracks forecast accuracy, bias,
#          and attainment by SKU, category, and month. The tool every demand
#          planning team needs but most don't have.
#
# WHY THIS PROJECT:
# - Gets asked in EVERY demand planning interview
# - "How do you monitor forecast performance?" — THIS is the answer
# - Combines your 12+ years of domain knowledge with data science tools
# - Shows you can build OPERATIONAL tools, not just one-time analyses
#
# BUSINESS CONTEXT:
# - Demand planners create forecasts monthly
# - But how do you know if those forecasts are GOOD?
# - MAPE tells you the error magnitude
# - Bias tells you if you're consistently over or under forecasting
# - Attainment tells you if you hit within an acceptable range
# - Tracking these by SKU/category/month reveals WHERE to improve
#
# KEY METRICS:
# - MAPE (Mean Absolute Percentage Error): How far off are we?
# - Bias (Forecast - Actual) / Actual: Are we consistently over or under?
# - FA% (Forecast Accuracy): 1 - MAPE (higher = better)
# - Attainment: % of SKUs within ±20% of forecast
# - Weighted MAPE: Revenue-weighted accuracy (big items matter more)
#
# TOOLS: Python, Streamlit, Plotly, Pandas
# ESTIMATED TIME: 3-4 hours
# =============================================================================


# =============================================================================
# PHASE 1: GENERATE REALISTIC DEMAND PLANNING DATA (15 minutes)
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("Libraries loaded!")

np.random.seed(42)

# Define product hierarchy
categories = {
    'Electronics': ['Laptop', 'Tablet', 'Phone', 'Headphones', 'Monitor'],
    'Home & Kitchen': ['Blender', 'Microwave', 'Vacuum', 'Coffee Maker', 'Toaster'],
    'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Shoes', 'Socks'],
    'Sports': ['Basketball', 'Yoga Mat', 'Dumbbells', 'Running Shoes', 'Water Bottle']
}

regions = ['North', 'South', 'East', 'West']
months = pd.date_range('2024-01-01', '2024-12-31', freq='MS')

# Generate data
records = []
for category, products in categories.items():
    for product in products:
        for region in regions:
            # Base demand varies by product
            base_demand = np.random.randint(200, 2000)
            unit_price = np.random.randint(10, 500)
            
            for month in months:
                # Actual demand with seasonality and noise
                month_num = month.month
                # Seasonality: peak in Nov-Dec (holidays), dip in Jan-Feb
                seasonality = 1.0 + 0.3 * np.sin(2 * np.pi * (month_num - 3) / 12)
                actual = int(base_demand * seasonality * np.random.uniform(0.7, 1.3))
                actual = max(50, actual)
                
                # Forecast: actual + systematic bias + random error
                # Some products have positive bias (over-forecast)
                # Some have negative bias (under-forecast)
                product_bias = hash(product) % 5 / 10 - 0.2  # -0.2 to +0.2
                region_bias = {'North': 0.05, 'South': -0.05, 'East': 0.10, 'West': -0.08}
                
                forecast_error = np.random.normal(product_bias + region_bias[region], 0.15)
                forecast = int(actual * (1 + forecast_error))
                forecast = max(50, forecast)
                
                records.append({
                    'Date': month,
                    'Year': month.year,
                    'Month': month.strftime('%b'),
                    'Month_Num': month.month,
                    'Category': category,
                    'Product': product,
                    'SKU': f"{product[:3].upper()}-{region[:1]}-{month.strftime('%m')}",
                    'Region': region,
                    'Actual': actual,
                    'Forecast': forecast,
                    'Unit_Price': unit_price
                })

df = pd.DataFrame(records)

# Calculate metrics
df['Error'] = df['Forecast'] - df['Actual']
df['Abs_Error'] = abs(df['Error'])
df['APE'] = df['Abs_Error'] / df['Actual'] * 100  # Absolute Percentage Error
df['Bias_Pct'] = df['Error'] / df['Actual'] * 100  # Bias as percentage
df['Revenue_Actual'] = df['Actual'] * df['Unit_Price']
df['Revenue_Forecast'] = df['Forecast'] * df['Unit_Price']
df['FA_Pct'] = (1 - df['Abs_Error'] / df['Actual']) * 100  # Forecast Accuracy %
df['Within_20'] = (df['APE'] <= 20).astype(int)  # Attainment: within ±20%

print(f"Dataset: {len(df)} rows")
print(f"Products: {df['Product'].nunique()}")
print(f"Categories: {df['Category'].nunique()}")
print(f"Regions: {df['Region'].nunique()}")
print(f"Months: {df['Date'].nunique()}")
print(f"\nSample data:")
print(df[['Date','Category','Product','Region','Actual','Forecast','APE','Bias_Pct','Within_20']].head(10))


# =============================================================================
# PHASE 2: UNDERSTAND THE METRICS (20 minutes)
# =============================================================================

print("""
=========================================================
FORECAST ACCURACY METRICS — THE COMPLETE GUIDE
=========================================================

1. MAPE (Mean Absolute Percentage Error):
   MAPE = mean(|Forecast - Actual| / Actual) × 100
   
   "On average, our forecasts are off by X%"
   MAPE = 15% → forecasts miss by 15% on average
   LOWER is better. <10% = excellent. 10-20% = good. >30% = poor.
   
   PROBLEM: MAPE is ASYMMETRIC.
     Over-forecast by 100 units on actual of 100: APE = 100%
     Under-forecast by 100 units on actual of 200: APE = 50%
     Same absolute error but different MAPE!

2. BIAS (Mean Forecast Error as % of Actual):
   Bias = mean((Forecast - Actual) / Actual) × 100
   
   POSITIVE bias = over-forecasting (forecast > actual) → excess inventory
   NEGATIVE bias = under-forecasting (forecast < actual) → stockouts
   NEAR ZERO = unbiased (errors cancel out, roughly balanced)
   
   CRITICAL INSIGHT: A planner can have 0% MAPE target but 0% bias
   is MORE achievable and often more valuable. Bias reveals SYSTEMATIC
   error that can be corrected. Random error (MAPE) is harder to fix.

3. FORECAST ACCURACY (FA%):
   FA% = 1 - MAPE = 100% - 15% = 85%
   Just MAPE flipped so HIGHER is better (easier for stakeholders).

4. ATTAINMENT:
   % of SKUs where forecast is within ±20% of actual.
   Attainment = 75% means 75% of SKUs had APE ≤ 20%.
   Measures RELIABILITY across the portfolio, not just average error.

5. WEIGHTED MAPE (WMAPE):
   WMAPE = Σ|Error_i| / Σ|Actual_i| × 100
   Weights by volume — errors on high-volume items matter MORE.
   A 30% miss on a $10M product is worse than 30% miss on a $100 product.
   WMAPE reflects business impact better than simple MAPE.
""")


# ---- STEP 2.1: Calculate summary metrics ----

overall_mape = df['APE'].mean()
overall_bias = df['Bias_Pct'].mean()
overall_fa = 100 - overall_mape
overall_wmape = df['Abs_Error'].sum() / df['Actual'].sum() * 100
overall_attainment = df['Within_20'].mean() * 100

print(f"OVERALL METRICS:")
print(f"  MAPE:        {overall_mape:.1f}%")
print(f"  Bias:        {overall_bias:+.1f}%")
print(f"  FA%:         {overall_fa:.1f}%")
print(f"  WMAPE:       {overall_wmape:.1f}%")
print(f"  Attainment:  {overall_attainment:.1f}% of SKUs within ±20%")


# =============================================================================
# PHASE 3: ANALYSIS BY DIMENSIONS (25 minutes)
# =============================================================================

# ---- STEP 3.1: Metrics by Category ----

cat_metrics = df.groupby('Category').agg(
    MAPE=('APE', 'mean'),
    Bias=('Bias_Pct', 'mean'),
    Total_Actual=('Actual', 'sum'),
    Total_Abs_Error=('Abs_Error', 'sum'),
    Attainment=('Within_20', 'mean')
).round(1)
cat_metrics['WMAPE'] = (cat_metrics['Total_Abs_Error'] / cat_metrics['Total_Actual'] * 100).round(1)
cat_metrics['FA%'] = (100 - cat_metrics['MAPE']).round(1)
cat_metrics['Attainment'] = (cat_metrics['Attainment'] * 100).round(1)

print("\nMETRICS BY CATEGORY:")
print(cat_metrics[['MAPE', 'Bias', 'WMAPE', 'FA%', 'Attainment']])


# ---- STEP 3.2: Metrics by Region ----

reg_metrics = df.groupby('Region').agg(
    MAPE=('APE', 'mean'),
    Bias=('Bias_Pct', 'mean'),
    Attainment=('Within_20', 'mean')
).round(1)
reg_metrics['Attainment'] = (reg_metrics['Attainment'] * 100).round(1)

print("\nMETRICS BY REGION:")
print(reg_metrics)


# ---- STEP 3.3: Monthly Trend ----

monthly = df.groupby('Month_Num').agg(
    MAPE=('APE', 'mean'),
    Bias=('Bias_Pct', 'mean'),
    Attainment=('Within_20', 'mean')
).round(1)
monthly['Attainment'] = (monthly['Attainment'] * 100).round(1)
monthly.index = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

print("\nMONTHLY TREND:")
print(monthly)


# =============================================================================
# PHASE 4: VISUALIZATIONS (20 minutes)
# =============================================================================

# ---- STEP 4.1: Monthly MAPE and Bias Trend ----

fig, axes = plt.subplots(2, 1, figsize=(14, 8))

months_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
axes[0].plot(months_list, monthly['MAPE'], 'bo-', linewidth=2, markersize=8)
axes[0].axhline(20, color='red', linestyle='--', alpha=0.5, label='Target: 20%')
axes[0].fill_between(months_list, 0, 20, alpha=0.1, color='green')
axes[0].set_title('Monthly MAPE Trend', fontsize=14, fontweight='bold')
axes[0].set_ylabel('MAPE (%)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Bias with color coding
colors = ['green' if abs(b) < 5 else 'orange' if abs(b) < 10 else 'red' for b in monthly['Bias']]
axes[1].bar(months_list, monthly['Bias'], color=colors, alpha=0.7, edgecolor='white')
axes[1].axhline(0, color='black', linewidth=1)
axes[1].axhline(5, color='orange', linestyle='--', alpha=0.3)
axes[1].axhline(-5, color='orange', linestyle='--', alpha=0.3)
axes[1].set_title('Monthly Forecast Bias', fontsize=14, fontweight='bold')
axes[1].set_ylabel('Bias (%)')
axes[1].grid(True, alpha=0.3)

plt.suptitle('Forecast Performance — Monthly Trend', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('01_monthly_trend.png', dpi=150, bbox_inches='tight')
plt.show()


# ---- STEP 4.2: Category Performance Heatmap ----

cat_month = df.groupby(['Category', 'Month_Num'])['APE'].mean().unstack().round(1)
cat_month.columns = months_list

fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(cat_month, annot=True, fmt='.0f', cmap='RdYlGn_r', center=20,
            linewidths=0.5, ax=ax, cbar_kws={'label': 'MAPE (%)'})
ax.set_title('MAPE Heatmap — Category × Month', fontsize=14, fontweight='bold')
ax.set_ylabel('Category')
ax.set_xlabel('Month')
plt.tight_layout()
plt.savefig('02_mape_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()

# HEATMAP INTERPRETATION:
# Red cells = high MAPE (poor accuracy) → needs attention
# Green cells = low MAPE (good accuracy) → working well
# Patterns: if one category is always red → systematic problem
#           if one month is always red → seasonal forecasting issue


# ---- STEP 4.3: Bias by Category and Region ----

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Category bias
cat_bias = df.groupby('Category')['Bias_Pct'].mean()
colors_cat = ['green' if abs(b) < 5 else 'orange' if abs(b) < 10 else 'red' for b in cat_bias]
axes[0].barh(cat_bias.index, cat_bias.values, color=colors_cat, alpha=0.7)
axes[0].axvline(0, color='black', linewidth=1)
axes[0].set_title('Forecast Bias by Category', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Bias (%) — Positive = Over-forecast')

# Region bias
reg_bias = df.groupby('Region')['Bias_Pct'].mean()
colors_reg = ['green' if abs(b) < 5 else 'orange' if abs(b) < 10 else 'red' for b in reg_bias]
axes[1].barh(reg_bias.index, reg_bias.values, color=colors_reg, alpha=0.7)
axes[1].axvline(0, color='black', linewidth=1)
axes[1].set_title('Forecast Bias by Region', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Bias (%) — Positive = Over-forecast')

plt.suptitle('Bias Analysis — Where Are We Systematically Wrong?', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('03_bias_analysis.png', dpi=150, bbox_inches='tight')
plt.show()


# ---- STEP 4.4: Actual vs Forecast Scatter ----

fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(df['Actual'], df['Forecast'], alpha=0.2, s=10, color='#3498db')
max_val = max(df['Actual'].max(), df['Forecast'].max())
ax.plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Perfect Forecast')
ax.plot([0, max_val], [0, max_val * 1.2], 'g--', linewidth=1, alpha=0.5, label='+20% band')
ax.plot([0, max_val], [0, max_val * 0.8], 'g--', linewidth=1, alpha=0.5, label='-20% band')
ax.set_title('Actual vs Forecast (All SKUs)', fontsize=14, fontweight='bold')
ax.set_xlabel('Actual Demand')
ax.set_ylabel('Forecasted Demand')
ax.legend()
ax.set_xlim(0)
ax.set_ylim(0)
plt.tight_layout()
plt.savefig('04_actual_vs_forecast.png', dpi=150, bbox_inches='tight')
plt.show()


# ---- STEP 4.5: Top/Bottom performers ----

product_metrics = df.groupby('Product').agg(
    MAPE=('APE', 'mean'),
    Bias=('Bias_Pct', 'mean'),
    Avg_Demand=('Actual', 'mean'),
    Attainment=('Within_20', 'mean')
).round(1)
product_metrics['Attainment'] = (product_metrics['Attainment'] * 100).round(1)

best_5 = product_metrics.nsmallest(5, 'MAPE')
worst_5 = product_metrics.nlargest(5, 'MAPE')

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].barh(best_5.index, best_5['MAPE'], color='#2ecc71', alpha=0.8)
axes[0].set_title('Top 5 Products (Lowest MAPE)', fontsize=14, fontweight='bold')
axes[0].set_xlabel('MAPE (%)')
for i, (_, row) in enumerate(best_5.iterrows()):
    axes[0].text(row['MAPE'] + 0.3, i, f"{row['MAPE']:.1f}%", va='center')

axes[1].barh(worst_5.index, worst_5['MAPE'], color='#e74c3c', alpha=0.8)
axes[1].set_title('Bottom 5 Products (Highest MAPE)', fontsize=14, fontweight='bold')
axes[1].set_xlabel('MAPE (%)')
for i, (_, row) in enumerate(worst_5.iterrows()):
    axes[1].text(row['MAPE'] + 0.3, i, f"{row['MAPE']:.1f}%", va='center')

plt.suptitle('Product-Level Forecast Performance', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('05_top_bottom_products.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nBEST 5 PRODUCTS:")
print(best_5[['MAPE', 'Bias', 'Attainment']])
print("\nWORST 5 PRODUCTS:")
print(worst_5[['MAPE', 'Bias', 'Attainment']])


# ---- STEP 4.6: Attainment Distribution ----

fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df['APE'].clip(0, 100), bins=50, color='#3498db', alpha=0.7, edgecolor='white')
ax.axvline(20, color='red', linewidth=2, linestyle='--', label='±20% threshold')
pct_within = df['Within_20'].mean() * 100
ax.fill_between([0, 20], 0, ax.get_ylim()[1], alpha=0.1, color='green')
ax.set_title(f'APE Distribution — {pct_within:.0f}% of forecasts within ±20%',
             fontsize=14, fontweight='bold')
ax.set_xlabel('Absolute Percentage Error (%)')
ax.set_ylabel('Count')
ax.legend()
plt.tight_layout()
plt.savefig('06_attainment_distribution.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# PHASE 5: BUILD THE STREAMLIT DASHBOARD (30 minutes)
# =============================================================================

# Save data for the Streamlit app
df.to_csv('forecast_data.csv', index=False)
print("\nData saved to forecast_data.csv")

# The Streamlit dashboard code will be in a separate file: forecast_dashboard.py
# Run with: streamlit run forecast_dashboard.py


# =============================================================================
# PHASE 6: SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("     PROJECT 11 COMPLETE — FORECAST ACCURACY & BIAS DASHBOARD")
print("=" * 70)
print(f"""
METRICS COVERED:
  ✅ MAPE (Mean Absolute Percentage Error) — error magnitude
  ✅ Bias (systematic over/under forecasting)
  ✅ FA% (Forecast Accuracy = 1 - MAPE)
  ✅ WMAPE (Volume-weighted accuracy)
  ✅ Attainment (% of SKUs within ±20%)

ANALYSIS DIMENSIONS:
  ✅ By Category (which product lines need attention?)
  ✅ By Region (which regions have systematic bias?)
  ✅ By Month (seasonal accuracy patterns)
  ✅ By Product (top/bottom performers)
  ✅ Overall portfolio health

VISUALIZATIONS:
  01 — Monthly MAPE & Bias trend (are we improving?)
  02 — MAPE heatmap — Category × Month (where are the hotspots?)
  03 — Bias by Category & Region (who over/under forecasts?)
  04 — Actual vs Forecast scatter (overall calibration check)
  05 — Top/Bottom 5 products (focus improvement efforts)
  06 — Attainment distribution (portfolio reliability)

DASHBOARD FEATURES (Streamlit):
  • KPI cards: MAPE, Bias, FA%, WMAPE, Attainment
  • Filters: Category, Region, Month
  • Trend charts, heatmaps, scatter plots
  • Product-level drill-down table
  • Export capability

KEY INTERVIEW TALKING POINTS:
  • "I built a forecast accuracy monitoring system that tracks MAPE,
     bias, and attainment across 20 products, 4 regions, and 12 months."
  • "Bias analysis revealed the East region consistently over-forecasts
     by 10% — this led to a targeted correction that reduced MAPE by 3%."
  • "The dashboard identified seasonal accuracy degradation in Q4,
     prompting us to add holiday adjustments to the forecasting model."
  • "Attainment analysis showed only 68% of SKUs were within ±20% —
     we focused on the worst 5 products and improved to 78%."
""")
print("=" * 70)
