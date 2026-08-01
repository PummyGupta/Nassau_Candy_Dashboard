# ==========================================
# Nassau Candy Profitability Dashboard
# Developed by Pummy Gupta
# ==========================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="Nassau Candy Dashboard",
    page_icon="🍫",
    layout="wide"
)

# -----------------------------
# TITLE
# -----------------------------

st.title("🍫 Nassau Candy Profitability Dashboard")

st.markdown("""
### Product Line Profitability & Margin Performance Analysis

Interactive dashboard for analyzing:

- Product Profitability
- Division Performance
- Margin Analysis
- Factory Analysis
- Pareto Analysis
- Executive Insights
""")

st.markdown("---")

# -----------------------------
# LOAD DATA
# -----------------------------

@st.cache_data
def load_data():

    df = pd.read_csv("Nassau Candy Distributor.csv")

    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        dayfirst=True,
        errors="coerce"
    )

    df["Ship Date"] = pd.to_datetime(
        df["Ship Date"],
        dayfirst=True,
        errors="coerce"
    )

    df["Gross Margin %"] = (
        df["Gross Profit"] /
        df["Sales"]
    ) * 100

    return df


df = load_data()

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("Dashboard Filters")

division = st.sidebar.multiselect(
    "Division",
    sorted(df["Division"].unique()),
    default=sorted(df["Division"].unique())
)

region = st.sidebar.multiselect(
    "Region",
    sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

ship = st.sidebar.multiselect(
    "Ship Mode",
    sorted(df["Ship Mode"].unique()),
    default=sorted(df["Ship Mode"].unique())
)

product = st.sidebar.text_input(
    "Search Product"
)

margin_filter = st.sidebar.slider(
    "Minimum Margin %",
    0,
    100,
    0
)

start = st.sidebar.date_input(
    "Start Date",
    value=df["Order Date"].min()
)

end = st.sidebar.date_input(
    "End Date",
    value=df["Order Date"].max()
)

# -----------------------------
# FILTER DATA
# -----------------------------

filtered = df.copy()

filtered = filtered[
    filtered["Division"].isin(division)
]

filtered = filtered[
    filtered["Region"].isin(region)
]

filtered = filtered[
    filtered["Ship Mode"].isin(ship)
]

filtered = filtered[
    (filtered["Order Date"] >= pd.to_datetime(start))
    &
    (filtered["Order Date"] <= pd.to_datetime(end))
]

if product != "":
    filtered = filtered[
        filtered["Product Name"].str.contains(
            product,
            case=False,
            na=False
        )
    ]

filtered = filtered[
    filtered["Gross Margin %"] >= margin_filter
]

# -----------------------------
# KPI
# -----------------------------

sales = filtered["Sales"].sum()

profit = filtered["Gross Profit"].sum()

cost = filtered["Cost"].sum()

units = filtered["Units"].sum()

margin = (
    profit / sales * 100
    if sales != 0
    else 0
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("💰 Sales", f"${sales:,.0f}")

c2.metric("📈 Profit", f"${profit:,.0f}")

c3.metric("💸 Cost", f"${cost:,.0f}")

c4.metric("📦 Units", f"{units:,}")

c5.metric("📊 Margin", f"{margin:.2f}%")

st.markdown("---")

# ==========================================
# PRODUCT PROFITABILITY ANALYSIS
# ==========================================

st.subheader("🏆 Product Profitability Leaderboard")

product_summary = (
    filtered.groupby("Product Name")
    .agg({
        "Sales": "sum",
        "Gross Profit": "sum",
        "Cost": "sum",
        "Units": "sum"
    })
    .reset_index()
)

product_summary["Margin %"] = (
    product_summary["Gross Profit"]
    / product_summary["Sales"]
) * 100

product_summary["Profit Per Unit"] = (
    product_summary["Gross Profit"]
    / product_summary["Units"]
)

product_summary = product_summary.sort_values(
    "Gross Profit",
    ascending=False
)

st.dataframe(
    product_summary,
    use_container_width=True
)

st.markdown("---")

# ==========================================
# TOP 10 PRODUCTS
# ==========================================

st.subheader("📈 Top 10 Products by Gross Profit")

fig1 = px.bar(
    product_summary.head(10),
    x="Gross Profit",
    y="Product Name",
    orientation="h",
    color="Margin %",
    text="Gross Profit",
    title="Top 10 Most Profitable Products"
)

fig1.update_layout(
    height=500,
    yaxis=dict(categoryorder="total ascending")
)

st.plotly_chart(
    fig1,
    use_container_width=True,
    key="top10_products"
)

st.markdown("---")

# ==========================================
# DIVISION PERFORMANCE
# ==========================================

st.subheader("📊 Division Performance")

division_summary = (
    filtered.groupby("Division")
    .agg({
        "Sales": "sum",
        "Gross Profit": "sum",
        "Cost": "sum"
    })
    .reset_index()
)

fig2 = px.bar(
    division_summary,
    x="Division",
    y=["Sales", "Gross Profit"],
    barmode="group",
    title="Revenue vs Gross Profit by Division"
)

st.plotly_chart(
    fig2,
    use_container_width=True,
    key="division_chart"
)

st.dataframe(
    division_summary,
    use_container_width=True
)

st.markdown("---")

# ==========================================
# REGIONAL SALES DISTRIBUTION
# ==========================================

st.subheader("🌍 Regional Sales Distribution")

region_summary = (
    filtered.groupby("Region")["Sales"]
    .sum()
    .reset_index()
)

fig3 = px.pie(
    region_summary,
    values="Sales",
    names="Region",
    hole=0.45,
    title="Sales Distribution by Region"
)

st.plotly_chart(
    fig3,
    use_container_width=True,
    key="region_pie"
)

st.markdown("---")

# ==========================================
# MONTHLY SALES & PROFIT TREND
# ==========================================

st.subheader("📈 Monthly Sales & Profit Trend")

monthly = filtered.copy()

monthly["Month"] = (
    monthly["Order Date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_summary = (
    monthly.groupby("Month")
    .agg({
        "Sales": "sum",
        "Gross Profit": "sum"
    })
    .reset_index()
)

fig4 = px.line(
    monthly_summary,
    x="Month",
    y=["Sales", "Gross Profit"],
    markers=True,
    title="Monthly Sales & Gross Profit"
)

st.plotly_chart(
    fig4,
    use_container_width=True,
    key="monthly_trend"
)

st.markdown("---")

# ==========================================
# COST VS SALES DIAGNOSTICS
# ==========================================

st.subheader("⚠️ Cost vs Sales Analysis")

fig5 = px.scatter(
    product_summary,
    x="Cost",
    y="Sales",
    size="Gross Profit",
    color="Margin %",
    hover_name="Product Name",
    title="Cost vs Sales Diagnostic"
)

st.plotly_chart(
    fig5,
    use_container_width=True,
    key="cost_sales"
)

st.markdown("---")

# ==========================================
# PARETO ANALYSIS
# ==========================================

st.subheader("📊 Pareto Analysis (80-20 Rule)")

pareto = product_summary.copy()

pareto = pareto.sort_values(
    "Gross Profit",
    ascending=False
)

pareto["Profit Contribution %"] = (
    pareto["Gross Profit"]
    / pareto["Gross Profit"].sum()
) * 100

pareto["Cumulative Profit %"] = (
    pareto["Profit Contribution %"]
).cumsum()

fig6 = go.Figure()

fig6.add_trace(
    go.Bar(
        x=pareto["Product Name"],
        y=pareto["Profit Contribution %"],
        name="Profit %"
    )
)

fig6.add_trace(
    go.Scatter(
        x=pareto["Product Name"],
        y=pareto["Cumulative Profit %"],
        mode="lines+markers",
        name="Cumulative %",
        yaxis="y2"
    )
)

fig6.update_layout(
    title="Pareto Analysis",
    yaxis=dict(title="Profit %"),
    yaxis2=dict(
        overlaying="y",
        side="right",
        range=[0, 105]
    ),
    height=600
)

st.plotly_chart(
    fig6,
    use_container_width=True,
    key="pareto_chart"
)

st.dataframe(
    pareto,
    use_container_width=True
)

st.markdown("---")

# ==========================================
# FACTORY-WISE ANALYSIS
# ==========================================

st.subheader("🏭 Factory-wise Product Analysis")

factory_map = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Hair Toffee": "The Other Factory",
    "Kazookles": "The Other Factory"
}

factory_df = filtered.copy()
factory_df["Factory"] = factory_df["Product Name"].map(factory_map)

factory_summary = (
    factory_df.groupby("Factory")
    .agg({
        "Sales": "sum",
        "Gross Profit": "sum",
        "Cost": "sum",
        "Units": "sum"
    })
    .reset_index()
)

fig7 = px.bar(
    factory_summary,
    x="Factory",
    y="Gross Profit",
    color="Factory",
    text_auto=".2s",
    title="Gross Profit by Factory"
)

st.plotly_chart(
    fig7,
    use_container_width=True,
    key="factory_chart"
)

st.dataframe(
    factory_summary,
    use_container_width=True
)

st.markdown("---")

# ==========================================
# DATASET PREVIEW
# ==========================================

st.subheader("📋 Dataset Preview")

st.dataframe(
    filtered.head(20),
    use_container_width=True
)

st.markdown("---")

# ==========================================
# EXECUTIVE INSIGHTS
# ==========================================

st.subheader("📌 Executive Insights")

top_product = product_summary.iloc[0]["Product Name"]
top_profit = product_summary.iloc[0]["Gross Profit"]

best_division = (
    filtered.groupby("Division")["Gross Profit"]
    .sum()
    .idxmax()
)

avg_margin = product_summary["Margin %"].mean()

st.info(f"""
🏆 Highest Profit Product: **{top_product}**

💰 Profit Generated: **${top_profit:,.2f}**

📈 Best Performing Division: **{best_division}**

📊 Average Product Margin: **{avg_margin:.2f}%**

✅ This dashboard helps identify high-profit products, margin risks, cost-heavy items, and supports pricing and product portfolio decisions.
""")

st.markdown("---")

# ==========================================
# FOOTER
# ==========================================

st.success("✅ Dashboard Completed Successfully")

st.caption(
    "Developed by Pummy Gupta | B.Tech Artificial Intelligence & Data Science | Nassau Candy Profitability Dashboard | Streamlit + Plotly + Pandas"
)

