import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Forecast Accuracy Dashboard", layout="wide")

@st.cache_data
def load_data():
    np.random.seed(42)
    categories = {
        'Electronics': ['Laptop', 'Tablet', 'Phone', 'Headphones', 'Monitor'],
        'Home & Kitchen': ['Blender', 'Microwave', 'Vacuum', 'Coffee Maker', 'Toaster'],
        'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Shoes', 'Socks'],
        'Sports': ['Basketball', 'Yoga Mat', 'Dumbbells', 'Running Shoes', 'Water Bottle']
    }
    regions = ['North', 'South', 'East', 'West']
    months = pd.date_range('2024-01-01', '2024-12-31', freq='MS')
    records = []
    for category, products in categories.items():
        for product in products:
            for region in regions:
                base_demand = np.random.randint(200, 2000)
                unit_price = np.random.randint(10, 500)
                for month in months:
                    month_num = month.month
                    seasonality = 1.0 + 0.3 * np.sin(2 * np.pi * (month_num - 3) / 12)
                    actual = int(base_demand * seasonality * np.random.uniform(0.7, 1.3))
                    actual = max(50, actual)
                    product_bias = hash(product) % 5 / 10 - 0.2
                    region_bias = {'North': 0.05, 'South': -0.05, 'East': 0.10, 'West': -0.08}
                    forecast_error = np.random.normal(product_bias + region_bias[region], 0.15)
                    forecast = int(actual * (1 + forecast_error))
                    forecast = max(50, forecast)
                    records.append({
                        'Date': month, 'Month': month.strftime('%b'), 'Month_Num': month.month,
                        'Category': category, 'Product': product, 'Region': region,
                        'Actual': actual, 'Forecast': forecast, 'Unit_Price': unit_price
                    })
    df = pd.DataFrame(records)
    df['Error'] = df['Forecast'] - df['Actual']
    df['Abs_Error'] = abs(df['Error'])
    df['APE'] = df['Abs_Error'] / df['Actual'] * 100
    df['Bias_Pct'] = df['Error'] / df['Actual'] * 100
    df['FA_Pct'] = (1 - df['Abs_Error'] / df['Actual']) * 100
    df['Within_20'] = (df['APE'] <= 20).astype(int)
    df['Revenue_Actual'] = df['Actual'] * df['Unit_Price']
    return df

df = load_data()

st.sidebar.title("Filters")
sel_categories = st.sidebar.multiselect("Category", df['Category'].unique(), default=df['Category'].unique())
sel_regions = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())
sel_months = st.sidebar.multiselect("Month", df['Month'].unique(), default=df['Month'].unique())

filtered = df[
    (df['Category'].isin(sel_categories)) &
    (df['Region'].isin(sel_regions)) &
    (df['Month'].isin(sel_months))
]

st.title("Forecast Accuracy and Bias Dashboard")
st.markdown("*Monitor demand forecast performance across products, regions, and time periods*")
st.markdown("---")

mape = filtered['APE'].mean()
bias = filtered['Bias_Pct'].mean()
fa = 100 - mape
wmape = filtered['Abs_Error'].sum() / filtered['Actual'].sum() * 100
attainment = filtered['Within_20'].mean() * 100
total_actual = filtered['Actual'].sum()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("MAPE", f"{mape:.1f}%", delta=f"{'Good' if mape < 20 else 'Needs Work'}", delta_color="inverse")
col2.metric("Bias", f"{bias:+.1f}%", delta="Over" if bias > 0 else "Under", delta_color="inverse")
col3.metric("FA%", f"{fa:.1f}%", delta=f"{'On Track' if fa > 80 else 'Below Target'}")
col4.metric("WMAPE", f"{wmape:.1f}%")
col5.metric("Attainment", f"{attainment:.0f}%", delta="within 20% band")
col6.metric("Total Demand", f"{total_actual:,.0f}")

st.markdown("---")

st.header("Monthly Performance Trend")
col_left, col_right = st.columns(2)

with col_left:
    monthly = filtered.groupby('Month_Num').agg(
        MAPE=('APE', 'mean'), Bias=('Bias_Pct', 'mean')
    ).reset_index()
    monthly['Month'] = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][:len(monthly)]
    fig_mape = go.Figure()
    fig_mape.add_trace(go.Scatter(x=monthly['Month'], y=monthly['MAPE'], mode='lines+markers',
                                   name='MAPE', line=dict(color='#3498db', width=3)))
    fig_mape.add_hline(y=20, line_dash="dash", line_color="red", annotation_text="Target: 20%")
    fig_mape.update_layout(title="Monthly MAPE Trend", yaxis_title="MAPE (%)",
                           height=350, plot_bgcolor='white')
    st.plotly_chart(fig_mape, use_container_width=True)

with col_right:
    colors = ['#2ecc71' if abs(b) < 5 else '#e67e22' if abs(b) < 10 else '#e74c3c' for b in monthly['Bias']]
    fig_bias = go.Figure()
    fig_bias.add_trace(go.Bar(x=monthly['Month'], y=monthly['Bias'], marker_color=colors))
    fig_bias.add_hline(y=0, line_color="black", line_width=2)
    fig_bias.add_hline(y=5, line_dash="dot", line_color="orange", annotation_text="+5%")
    fig_bias.add_hline(y=-5, line_dash="dot", line_color="orange", annotation_text="-5%")
    fig_bias.update_layout(title="Monthly Forecast Bias", yaxis_title="Bias (%)",
                           height=350, plot_bgcolor='white')
    st.plotly_chart(fig_bias, use_container_width=True)

st.header("Accuracy Heatmap and Calibration")
col_left2, col_right2 = st.columns(2)

with col_left2:
    pivot = filtered.groupby(['Category', 'Month_Num'])['APE'].mean().reset_index()
    pivot_table = pivot.pivot(index='Category', columns='Month_Num', values='APE')
    pivot_table.columns = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][:len(pivot_table.columns)]
    fig_heat = px.imshow(pivot_table, color_continuous_scale='RdYlGn_r',
                          color_continuous_midpoint=20,
                          labels=dict(color="MAPE (%)"),
                          text_auto='.0f')
    fig_heat.update_layout(title="MAPE Heatmap - Category x Month", height=350)
    st.plotly_chart(fig_heat, use_container_width=True)

with col_right2:
    sample = filtered.sample(min(500, len(filtered)), random_state=42)
    fig_scatter = go.Figure()
    fig_scatter.add_trace(go.Scatter(x=sample['Actual'], y=sample['Forecast'],
                                      mode='markers', marker=dict(size=4, color='#3498db', opacity=0.4),
                                      name='SKUs'))
    max_val = max(sample['Actual'].max(), sample['Forecast'].max())
    fig_scatter.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val],
                                      mode='lines', line=dict(color='red', dash='dash'), name='Perfect'))
    fig_scatter.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val*1.2],
                                      mode='lines', line=dict(color='green', dash='dot', width=1), name='+20%'))
    fig_scatter.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val*0.8],
                                      mode='lines', line=dict(color='green', dash='dot', width=1), name='-20%'))
    fig_scatter.update_layout(title="Actual vs Forecast", xaxis_title="Actual",
                               yaxis_title="Forecast", height=350, plot_bgcolor='white')
    st.plotly_chart(fig_scatter, use_container_width=True)

st.header("Performance by Dimension")
tab1, tab2, tab3 = st.tabs(["By Category", "By Region", "By Product"])

with tab1:
    cat_m = filtered.groupby('Category').agg(
        MAPE=('APE','mean'), Bias=('Bias_Pct','mean'),
        Attainment=('Within_20','mean'), Demand=('Actual','sum')
    ).reset_index()
    cat_m['Attainment'] = (cat_m['Attainment'] * 100).round(1)
    col_a, col_b = st.columns(2)
    with col_a:
        fig_cat = px.bar(cat_m, x='Category', y='MAPE', color='MAPE',
                          color_continuous_scale='RdYlGn_r', color_continuous_midpoint=20,
                          text_auto='.1f')
        fig_cat.update_layout(title="MAPE by Category", height=350, plot_bgcolor='white')
        st.plotly_chart(fig_cat, use_container_width=True)
    with col_b:
        fig_att = px.bar(cat_m, x='Category', y='Attainment', color='Attainment',
                          color_continuous_scale='RdYlGn', text_auto='.0f')
        fig_att.update_layout(title="Attainment by Category (% within 20%)", height=350, plot_bgcolor='white')
        st.plotly_chart(fig_att, use_container_width=True)

with tab2:
    reg_m = filtered.groupby('Region').agg(
        MAPE=('APE','mean'), Bias=('Bias_Pct','mean'),
        Attainment=('Within_20','mean')
    ).reset_index()
    reg_m['Attainment'] = (reg_m['Attainment'] * 100).round(1)
    col_c, col_d = st.columns(2)
    with col_c:
        fig_reg = px.bar(reg_m, x='Region', y='MAPE', color='MAPE',
                          color_continuous_scale='RdYlGn_r', color_continuous_midpoint=20, text_auto='.1f')
        fig_reg.update_layout(title="MAPE by Region", height=350, plot_bgcolor='white')
        st.plotly_chart(fig_reg, use_container_width=True)
    with col_d:
        fig_rbias = px.bar(reg_m, x='Region', y='Bias', color='Bias',
                            color_continuous_scale='RdBu_r', color_continuous_midpoint=0, text_auto='.1f')
        fig_rbias.update_layout(title="Bias by Region", height=350, plot_bgcolor='white')
        st.plotly_chart(fig_rbias, use_container_width=True)

with tab3:
    prod_m = filtered.groupby('Product').agg(
        MAPE=('APE','mean'), Bias=('Bias_Pct','mean'),
        Attainment=('Within_20','mean'), Avg_Demand=('Actual','mean')
    ).reset_index().round(1)
    prod_m['Attainment'] = (prod_m['Attainment'] * 100).round(1)
    prod_m = prod_m.sort_values('MAPE')
    st.dataframe(
        prod_m.style.background_gradient(subset=['MAPE'], cmap='RdYlGn_r')
              .background_gradient(subset=['Attainment'], cmap='RdYlGn')
              .format({'MAPE': '{:.1f}%', 'Bias': '{:+.1f}%', 'Attainment': '{:.0f}%', 'Avg_Demand': '{:,.0f}'}),
        use_container_width=True,
        height=500
    )

st.markdown("---")
st.markdown("*Built by Nithin Kumar Kokkisa | Demand Planning Analytics | March 2026*")
