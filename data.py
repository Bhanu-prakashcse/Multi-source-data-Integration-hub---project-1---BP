import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="🛍️ Retail Analytics Dashboard",
    layout="wide",
)

# -------------------------------
# LOAD DATA FROM BIGQUERY
# -------------------------------
from google.cloud import bigquery
client = bigquery.Client(project="trim-plexus-396409")


query = """
SELECT *
FROM `trim-plexus-396409.Silver_layer_BP.retail_silver`
"""

df = client.query(query).to_dataframe()

# --- FILTER SECTION ---
st.sidebar.markdown("## 🧭 Filter Options")

# Add collapsible dropdowns using Streamlit's expander
with st.sidebar.expander("🏙️ Select Cities"):
    selected_cities = st.multiselect(
        "Cities",
        df['City'].dropna().unique().tolist(),
        default=df['City'].dropna().unique().tolist()
    )

st.sidebar.markdown("")  # add a small space

with st.sidebar.expander("👥 Select Customer Categories"):
    selected_categories = st.multiselect(
        "Customer Categories",
        df['Customer_Category'].dropna().unique().tolist(),
        default=df['Customer_Category'].dropna().unique().tolist()
    )

st.sidebar.markdown("")  # small space

with st.sidebar.expander("❄️ Select Seasons"):
    selected_seasons = st.multiselect(
        "Seasons",
        df['Season'].dropna().unique().tolist(),
        default=df['Season'].dropna().unique().tolist()
    )

# Apply filters
filtered_df = df[
    (df['City'].isin(selected_cities)) &
    (df['Customer_Category'].isin(selected_categories)) &
    (df['Season'].isin(selected_seasons))
]

# -------------------------------
# CLEAN DATA TYPES
# -------------------------------
df['Total_Cost'] = df['Total_Cost'].astype(float)
df['Total_Items'] = df['Total_Items'].astype(int)
df['City'] = df['City'].astype(str)
df['Customer_Category'] = df['Customer_Category'].astype(str)
df['Product'] = df['Product'].astype(str)
df['Payment_Method'] = df['Payment_Method'].astype(str)
df['Store_Type'] = df['Store_Type'].astype(str)
df['Season'] = df['Season'].astype(str)
df['Discount_Applied'] = df['Discount_Applied'].astype(bool)

# -------------------------------
# DASHBOARD TITLE
# -------------------------------
st.markdown("<h1 style='text-align: center;'>🛍️ Title : Multi-source Retail Data Integration Hub</h1>", unsafe_allow_html=True)
st.subheader("📊 Retail Performance & Sales Insights Dashboard")

# -------------------------------
# KPIs SECTION
# -------------------------------
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("🧾 Total Transactions", f"{len(df):,}")
with col2:
    st.metric("📦 Unique Products", f"{df['Product'].nunique():,}")
with col3:
    st.metric("💰 Total Revenue", f"{df['Total_Cost'].sum():,.2f}")
with col4:
    st.metric("🌆 Total Cities", f"{df['City'].nunique():,}")
with col5:
    st.metric("👥 Total Customers", f"{df['Customer_Name'].nunique():,}")
with col6:
    st.metric("🏷️ Customer Categories", f"{df['Customer_Category'].nunique():,}")

st.markdown("---")


# -------------------------------
# CHARTS SECTION
# -------------------------------

# Sales by City
# -------------------------------
# SIDE-BY-SIDE BAR CHARTS SECTION
# -------------------------------

st.markdown("<h2 style='text-align: center;'>📊 Sales Analysis</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏙️ Sales by City")
    city_sales = filtered_df.groupby("City")["Total_Cost"].sum().reset_index().sort_values(by="Total_Cost", ascending=False)
    fig1 = px.bar(city_sales, x="City", y="Total_Cost", color="City",
                  title="Total Revenue by City")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🏆 Top Products by Revenue")
    top_products = filtered_df.groupby("Product")["Total_Cost"].sum().reset_index().sort_values(by="Total_Cost", ascending=False).head(10)
    fig2 = px.bar(top_products, x="Product", y="Total_Cost", color="Product",
                  title="Top 10 Products")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# -------------------------------
# COMBINED PIE CHARTS SECTION
# -------------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("💳 Sales by Payment Method")
    payment_sales = filtered_df.groupby("Payment_Method")["Total_Cost"].sum().reset_index()
    fig3 = px.pie(payment_sales, names="Payment_Method", values="Total_Cost",
                  title="Revenue Share by Payment Method")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("🏬 Sales by Store Type")
    store_sales = filtered_df.groupby("Store_Type")["Total_Cost"].sum().reset_index()
    fig4 = px.pie(store_sales, names="Store_Type", values="Total_Cost",
                  title="Revenue Share by Store Type")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# Customer Category Performance
st.subheader("👤 Revenue by Customer Category")
cat_sales = filtered_df.groupby("Customer_Category")["Total_Cost"].sum().reset_index()
fig4 = px.bar(cat_sales, x="Customer_Category", y="Total_Cost", color="Customer_Category",
              title="Customer Category Revenue", text_auto=True)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")


# Seasonal Revenue Trend
st.subheader("📈 Seasonal Revenue Trend")
season_sales = filtered_df.groupby("Season")["Total_Cost"].sum().reset_index()
fig_season = px.line(season_sales, x="Season", y="Total_Cost", markers=True, title="Revenue Trend by Season")
st.plotly_chart(fig_season, use_container_width=True)

# Discount Impact Analysis
st.subheader("💸 Discount Impact on Revenue")

# Convert Discount_Applied column safely to standard bool or string
filtered_df["Discount_Applied"] = filtered_df["Discount_Applied"].astype(str)

discount_impact = (
    filtered_df.groupby("Discount_Applied")["Total_Cost"]
    .mean()
    .reset_index()
)

# Clean up the labels for better readability
discount_impact["Discount_Applied"] = discount_impact["Discount_Applied"].replace(
    {"True": "Discount Applied", "False": "No Discount"}
)

fig_discount = px.bar(
    discount_impact,
    x="Discount_Applied",
    y="Total_Cost",
    color="Discount_Applied",
    title="Average Revenue by Discount Status",
    text_auto=True
)

st.plotly_chart(fig_discount, use_container_width=True)


st.success(" Dashboard loaded successfully!")
