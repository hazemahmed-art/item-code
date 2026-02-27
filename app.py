import streamlit as st
import pandas as pd

# ================== إعداد الصفحة ==================
st.set_page_config(
    page_title="WaterStar نظام إدارة قوائم المواد الصناعية",
    layout="wide",
    page_icon="logo.png",
    initial_sidebar_state="collapsed"
)

# ================== RTL CSS ==================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }

    h1, h2, h3, h4, h5, h6, p, span, label {
        text-align: right !important;
        direction: rtl !important;
    }

    .rtl-table-container {
        direction: rtl;
        text-align: right;
        overflow-y: auto;
        overflow-x: auto;
        margin: 20px 0;
        height: 430px;
        border: 1px solid #e6e9ef;
        border-radius: 5px;
    }

    .dataframe-html {
        width: 100%;
        border-collapse: collapse;
    }

    .dataframe-html th {
        background-color: #4694f9;
        padding: 8px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        color: white;
        position: sticky;
        top: 0;
        z-index: 1;
    }

    .dataframe-html td {
        padding: 8px;
        border: 1px solid #e6e9ef;
        font-size: 18px;
        font-weight: bold;
    }

    .dataframe-html tr:nth-child(even) {
        background-color: #fafafa;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== العنوان ==================
col1, col2, col3 = st.columns([3, 3, 1])
with col1:
    st.title("📦 نظام عرض مكونات المنتجات")
with col3:
    st.image("logo.png", width=220)

# ================== قراءة الملف ==================
file_path = "v7.xlsx"

try:
    df = pd.read_excel(file_path)
except Exception as e:
    st.error(f"خطأ في قراءة الملف: {e}")
    st.stop()

# ================== التأكد من وجود الأعمدة الأساسية ==================
required_columns = ["Family", "Description", "Product"]

for col in required_columns:
    if col not in df.columns:
        st.error(f"العمود {col} غير موجود في ملف الإكسل")
        st.stop()

# ================== تحديد المكونات ==================
component_columns = [col for col in df.columns if col not in required_columns]

# ================== اختيار العائلة ==================
family_list = sorted(df["Family"].dropna().unique())
selected_family = st.selectbox("اختر اسم العائلة", ["- اختر عائلة -"] + family_list)

if selected_family != "- اختر عائلة -":

    family_data = df[df["Family"] == selected_family]

    # ================== اختيار المنتج ==================
    st.subheader("🔸 اختيار المنتج")
    product_list = sorted(family_data["Product"].dropna().unique())
    selected_product = st.selectbox("اختر المنتج", ["- اختر منتج -"] + product_list)

    if selected_product != "- اختر منتج -":

        product_row = family_data[family_data["Product"] == selected_product].iloc[0]

        st.subheader("📋 تفاصيل المنتج")
        st.info(f"**الوصف:** {product_row['Description']}")

        # ================== جدول المكونات ==================
        comp_data = []

        for comp in component_columns:
            value = pd.to_numeric(product_row[comp], errors='coerce')
            if pd.notna(value) and value > 0:
                comp_data.append({
                    "المكون": comp,
                    "الكمية المطلوبة": f"{value:.3f}"
                })

        comp_df = pd.DataFrame(comp_data)

        if comp_df.empty:
            st.warning("لا توجد مكونات مسجلة لهذا المنتج")
        else:
            html_table = comp_df.to_html(index=False, classes="dataframe-html")
            st.markdown(f'<div class="rtl-table-container">{html_table}</div>', unsafe_allow_html=True)
            st.markdown(f"**عدد الأجزاء المطلوبة: {len(comp_df)}**")

    # ================== عرض جدول كامل للعائلة ==================
    if st.button("📊 عرض جدول كل منتجات العائلة المختارة", type="primary", use_container_width=True):

        pivot_df = family_data[["Product"] + component_columns].copy()
        pivot_df = pivot_df.set_index("Product")

        # حذف الأعمدة التي كلها صفر
        pivot_df = pivot_df.loc[:, (pivot_df != 0).any(axis=0)]

        if pivot_df.empty:
            st.warning("لا توجد بيانات لهذه العائلة")
        else:
            # تنسيق الأرقام
            for col in pivot_df.columns:
                pivot_df[col] = pivot_df[col].apply(
                    lambda x: f"{float(x):.3f}" if pd.notna(x) and float(x) != 0 else "-"
                )

            pivot_df = pivot_df.reset_index()

            html_table = pivot_df.to_html(index=False, classes="dataframe-html")
            st.markdown(f'<div class="rtl-table-container">{html_table}</div>', unsafe_allow_html=True)

else:
    st.info("الرجاء اختيار العائلة لبدء العرض.")
