import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery
from datetime import datetime

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="🛍️ Retail Analytics Dashboard",
    layout="wide",
)

# -------------------------------
# BIGQUERY CLIENT
# -------------------------------
client = bigquery.Client(project="sharedproject2025")

# -------------------------------
# HELPERS
# -------------------------------
def safe_cast(series, dtype, default=None):
    try:
        return series.astype(dtype)
    except Exception:
        if dtype in [float, 'float', 'float64']:
            return pd.to_numeric(series, errors='coerce').fillna(0.0).astype(float)
        if dtype in [int, 'int', 'int64']:
            return pd.to_numeric(series, errors='coerce').fillna(0).astype(int)
        return series.fillna(default).astype(str)

def run_query_to_df(sql: str) -> pd.DataFrame:
    """Run a BigQuery SQL and return a pandas DataFrame (with error handling)."""
    try:
        return client.query(sql).to_dataframe()
    except Exception as e:
        st.error(f"BigQuery error: {e}")
        return pd.DataFrame()

def escape_quotes(s: str) -> str:
    """Escape double quotes for embedding into SQL string literals."""
    if s is None:
        return ""
    return s.replace('"', '\\"').replace("'", "\\'")

# -------------------------------
# LOAD DATA FROM BIGQUERY (Silver layer)
# -------------------------------
query = """
SELECT *
FROM `sharedproject2025.Data_Integration_Hub_BP.Silver_layer-retail_enriched`
"""
df = run_query_to_df(query)

# If bigquery failed, df will be empty — show helpful message
if df.empty:
    st.warning("Silver layer returned no data or BigQuery query failed. Confirm dataset & permissions.")

# --- Ensure unified 'Product' column for dashboard ---
product_col = None
for possible_col in ["Product", "product_name_retail", "product_name_catalog", "product_name"]:
    if possible_col in df.columns:
        product_col = possible_col
        break

if product_col and product_col != "Product":
    df.rename(columns={product_col: "Product"}, inplace=True)
else:
    if "Product" not in df.columns:
        st.warning("⚠️ No product column found — using placeholder.")
        df["Product"] = "Unknown Product"

# -------------------------------
# CLEAN DATA TYPES (do this BEFORE filters)
# -------------------------------
df = df.copy()

if 'Total_Cost' in df.columns:
    df['Total_Cost'] = safe_cast(df['Total_Cost'], float, 0.0)
if 'Total_Items' in df.columns:
    df['Total_Items'] = safe_cast(df['Total_Items'], int, 0)

for col in ['City', 'Customer_Category', 'Product', 'Payment_Method', 'Store_Type', 'Season', 'Customer_Name']:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown").astype(str)

if 'Discount_Applied' in df.columns:
    df['Discount_Applied'] = df['Discount_Applied'].map(
        lambda x: True if str(x).strip().lower() in ['true', '1', 'yes'] else (False if str(x).strip().lower() in ['false', '0', 'no'] else False)
    )

# -------------------------------
# FILTER SECTION (sidebar, collapsible)
# -------------------------------
st.sidebar.markdown("## 🧭 Filter Options")

city_options = df['City'].dropna().unique().tolist() if 'City' in df.columns else []
cat_options = df['Customer_Category'].dropna().unique().tolist() if 'Customer_Category' in df.columns else []
season_options = df['Season'].dropna().unique().tolist() if 'Season' in df.columns else []
product_options = df['Product'].dropna().unique().tolist() if 'Product' in df.columns else []

with st.sidebar.expander("🏙️ Select Cities", expanded=True):
    selected_cities = st.multiselect(
        "Cities",
        city_options,
        default=city_options
    )

st.sidebar.markdown("")  # small space

with st.sidebar.expander("👥 Select Customer Categories", expanded=True):
    selected_categories = st.multiselect(
        "Customer Categories",
        cat_options,
        default=cat_options
    )

st.sidebar.markdown("")  # small space

with st.sidebar.expander("❄️ Select Seasons", expanded=False):
    selected_seasons = st.multiselect(
        "Seasons",
        season_options,
        default=season_options
    )

# product filter (optional)
with st.sidebar.expander("🛒 Product (optional)", expanded=False):
    selected_products = st.multiselect(
        "Products",
        product_options,
        default=[]
    )

# show SCD2 widget toggle
show_scd = st.sidebar.checkbox("Show Product Version History (SCD2)", value=False)

# -------------------------------
# APPLY FILTERS to create filtered_df
# -------------------------------
if not selected_cities:
    selected_cities = city_options
if not selected_categories:
    selected_categories = cat_options
if not selected_seasons:
    selected_seasons = season_options

filtered_df = df[
    (df['City'].isin(selected_cities)) &
    (df['Customer_Category'].isin(selected_categories)) &
    (df['Season'].isin(selected_seasons))
].copy()

if selected_products:
    filtered_df = filtered_df[filtered_df['Product'].isin(selected_products)].copy()

# -------------------------------
# DASHBOARD TITLE
# -------------------------------
st.markdown("<h1 style='text-align: center;'>🛍️ Title : Multi-source Retail Data Integration Hub</h1>", unsafe_allow_html=True)
st.subheader("📊 Retail Performance & Sales Insights Dashboard")

# -------------------------------
# KPIs SECTION (use filtered_df)
# -------------------------------
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("🧾 Total Transactions", f"{len(filtered_df):,}")
with col2:
    st.metric("📦 Unique Products", f"{filtered_df['Product'].nunique():,}")
with col3:
    st.metric("💰 Total Revenue", f"{filtered_df['Total_Cost'].sum():,.2f}")
with col4:
    st.metric("🌆 Total Cities", f"{filtered_df['City'].nunique():,}")
with col5:
    st.metric("👥 Total Customers", f"{filtered_df['Customer_Name'].nunique():,}")
with col6:
    st.metric("🏷️ Customer Categories", f"{filtered_df['Customer_Category'].nunique():,}")

st.markdown("---")

# -------------------------------
# CHARTS SECTION (same as before)
# -------------------------------
st.markdown("<h2 style='text-align: center;'>📊 Sales Analysis</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏙️ Sales by City")
    city_sales = filtered_df.groupby("City")["Total_Cost"].sum().reset_index().sort_values(by="Total_Cost", ascending=False)
    fig1 = px.bar(city_sales, x="City", y="Total_Cost", color="City", title="Total Revenue by City")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🏆 Top Products by Revenue")
    top_products = filtered_df.groupby("Product")["Total_Cost"].sum().reset_index().sort_values(by="Total_Cost", ascending=False).head(10)
    fig2 = px.bar(top_products, x="Product", y="Total_Cost", color="Product", title="Top 10 Products")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("💳 Sales by Payment Method")
    payment_sales = filtered_df.groupby("Payment_Method")["Total_Cost"].sum().reset_index()
    fig3 = px.pie(payment_sales, names="Payment_Method", values="Total_Cost", title="Revenue Share by Payment Method")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("🏬 Sales by Store Type")
    store_sales = filtered_df.groupby("Store_Type")["Total_Cost"].sum().reset_index()
    fig4 = px.pie(store_sales, names="Store_Type", values="Total_Cost", title="Revenue Share by Store Type")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

st.subheader("👤 Revenue by Customer Category")
cat_sales = filtered_df.groupby("Customer_Category")["Total_Cost"].sum().reset_index()
fig_cat = px.bar(cat_sales, x="Customer_Category", y="Total_Cost", color="Customer_Category", title="Customer Category Revenue", text_auto=True)
st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")

st.subheader("📈 Seasonal Revenue Trend")
season_sales = filtered_df.groupby("Season")["Total_Cost"].sum().reset_index()
fig_season = px.line(season_sales, x="Season", y="Total_Cost", markers=True, title="Revenue Trend by Season")
st.plotly_chart(fig_season, use_container_width=True)

st.markdown("---")

# -------------------------------
# Discount Impact Analysis (safe handling)
# -------------------------------
st.subheader("💸 Discount Impact on Revenue")
discount_df = filtered_df.copy()
if 'Discount_Applied' in discount_df.columns:
    discount_df['Discount_Applied_Label'] = discount_df['Discount_Applied'].map({True: "Discount Applied", False: "No Discount"})
else:
    discount_df['Discount_Applied_Label'] = "No Discount"

discount_impact = (
    discount_df.groupby("Discount_Applied_Label")["Total_Cost"]
    .mean()
    .reset_index()
)
fig_discount = px.bar(discount_impact, x="Discount_Applied_Label", y="Total_Cost", color="Discount_Applied_Label", title="Average Revenue by Discount Status", text_auto=True)
st.plotly_chart(fig_discount, use_container_width=True)

st.markdown("---")

# -------------------------------
# SCD2 / Product Version History Section
# -------------------------------
if show_scd:
    st.markdown("<h2 style='text-align: center;'>🕒 Product Version History (SCD Type 2)</h2>", unsafe_allow_html=True)

    # Load product list from the Gold dim_product table (preferred source for SCD products)
    prod_list_query = """
    SELECT DISTINCT product_name
    FROM `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product`
    WHERE product_name IS NOT NULL
    ORDER BY product_name
    """
    prod_df = run_query_to_df(prod_list_query)
    prod_names = prod_df['product_name'].dropna().unique().tolist() if not prod_df.empty else []

    # product selector (use gold product names)
    selected_product = st.selectbox("Select product for SCD2 history", ["-- select --"] + prod_names)

    if selected_product and selected_product != "-- select --":
        # show current versions for the selected product
        scd_query = f"""
        SELECT product_id, product_name, category, product_price,
               product_description, valid_from, valid_to, is_current
        FROM `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
        WHERE product_name = "{escape_quotes(selected_product)}"
        ORDER BY valid_from DESC
        """
        scd_df = run_query_to_df(scd_query)

        if scd_df.empty:
            st.info("No SCD history found for this product (maybe it's not yet tracked).")
        else:
            st.subheader("Version history (most recent first)")
            st.dataframe(scd_df)

            # simple line chart for price over versions (x=valid_from)
            try:
                price_df = scd_df.copy()
                price_df['valid_from'] = pd.to_datetime(price_df['valid_from'])
                fig_price = px.line(price_df.sort_values('valid_from'), x='valid_from', y='product_price', markers=True,
                                    title=f"Price timeline: {selected_product}")
                st.plotly_chart(fig_price, use_container_width=True)
            except Exception:
                # fallback if plotting fails
                st.write("Price timeline plotting failed for this product.")

        st.markdown("---")
        st.subheader("🔁 Simulate / Apply an SCD2 Update (Expire + Insert)")

        # input for update
        col_a, col_b = st.columns(2)
        with col_a:
            new_price = st.number_input("New price (float)", min_value=0.0, value=0.0, format="%.2f")
        with col_b:
            new_desc = st.text_input("New product description", value="")

        # button to apply safe SCD2 update
        if st.button("Apply SCD2 Update"):
            if new_price <= 0:
                st.error("Enter a valid new price (> 0).")
            else:
                # step A: fetch current product row to get product_id and category (if exists)
                fetch_sql = f"""
                SELECT product_id, category
                FROM `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
                WHERE product_name = "{escape_quotes(selected_product)}"
                ORDER BY valid_from DESC
                LIMIT 1
                """
                try:
                    current_row = client.query(fetch_sql).to_dataframe()
                except Exception as e:
                    st.error(f"Failed to fetch current product row: {e}")
                    current_row = pd.DataFrame()

                # determine product_id and category
                if not current_row.empty:
                    product_id_val = int(current_row.loc[0, 'product_id']) if current_row.loc[0, 'product_id'] is not None else None
                    category_val = current_row.loc[0, 'category']
                else:
                    product_id_val = None
                    category_val = "Unknown"

                # Step 1: expire existing current row (if exists)
                expire_sql = f"""
                UPDATE `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
                SET valid_to = CURRENT_TIMESTAMP(), is_current = FALSE
                WHERE product_name = "{escape_quotes(selected_product)}" AND is_current = TRUE
                """
                try:
                    q = client.query(expire_sql)
                    q.result()  # wait
                    st.info("Expired existing current record (if present).")
                except Exception as e:
                    st.error(f"Failed to expire existing record: {e}")

                # Step 2: insert new version
                # If we don't have product_id (rare), try to fetch from Gold_Layer-dim_product table
                if product_id_val is None:
                    fetch_id_sql = f"""
                    SELECT product_id
                    FROM `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product`
                    WHERE product_name = "{escape_quotes(selected_product)}"
                    LIMIT 1
                    """
                    try:
                        id_df = client.query(fetch_id_sql).to_dataframe()
                        if not id_df.empty:
                            product_id_val = int(id_df.loc[0, 'product_id'])
                    except Exception:
                        product_id_val = None

                # prepare insert values (nulls where not available)
                product_id_sql_val = "NULL" if product_id_val is None else str(product_id_val)
                product_desc_escaped = escape_quotes(new_desc)

                insert_sql = f"""
                INSERT INTO `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
                (product_id, product_name, category, product_price, product_description, valid_from, valid_to, is_current)
                VALUES (
                  {product_id_sql_val},
                  "{escape_quotes(selected_product)}",
                  "{escape_quotes(category_val)}",
                  {float(new_price)},
                  "{product_desc_escaped}",
                  CURRENT_TIMESTAMP(),
                  TIMESTAMP('9999-12-31 00:00:00'),
                  TRUE
                )
                """
                try:
                    client.query(insert_sql).result()
                    st.success("SCD2 update applied: new version inserted.")
                    # refresh scd_df for immediate view
                    scd_df = run_query_to_df(scd_query)
                    st.dataframe(scd_df)
                except Exception as e:
                    st.error(f"Failed to insert new version: {e}")

# -------------------------------
# END OF DASHBOARD
# -------------------------------
st.markdown("---")
st.caption("© 2025 Multi-source Retail Data Integration Hub | Developed by Dandu Bhanu Prakash")