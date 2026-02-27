import streamlit as st
import pandas as pd

# ================== إعداد الصفحة ==================
st.set_page_config(
    page_title="WaterStar نظام إدارة قوائم المواد الصناعية",
    layout="wide",
    page_icon="logo.png",
    initial_sidebar_state="collapsed"
)

# ================== RTL CSS الشامل ==================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
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
        text-align: right;
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
    st.image("logo.png", width=200)

# ================== قراءة ملف Excel ==================
file_path = "v7.xlsx"
try:
    df = pd.read_excel(file_path)
except Exception as e:
    st.error(f"خطأ في قراءة ملف Excel: {e}")
    st.stop()

# ================== استخراج البيانات بعد Transpose ==================
# نفترض أن:
# العمود 0 = Family
# العمود 1 = Description
# العمود 2 = Product
# من العمود 3 حتى النهاية = المكونات

df.columns = df.columns.astype(str)

components = df.columns[3:]  # أسماء المكونات
records = []

for _, row in df.iterrows():
    family = row.iloc[0]
    description = row.iloc[1]
    product = row.iloc[2]

    if pd.isna(family) or pd.isna(product):
        continue

    values = pd.to_numeric(row.iloc[3:], errors="coerce").fillna(0).values

    records.append({
        "Family": str(family).strip(),
        "Product": str(product).strip(),
        "Description": str(description).strip() if pd.notna(description) else "لا يوجد وصف",
        "Values": values
    })

structured_df = pd.DataFrame(records)

# ================== اختيار العائلة ==================
family_list = sorted(structured_df["Family"].unique())
selected_family = st.selectbox("اختر اسم العائلة", ["- اختر عائلة -"] + family_list)

if selected_family != "- اختر عائلة -":

    family_data = structured_df[structured_df["Family"] == selected_family]

    # ================== اختيار المنتج ==================
    st.subheader("🔸 اختيار المنتج")
    product_list = sorted(family_data["Product"].unique())
    selected_product = st.selectbox("اختر المنتج", ["- اختر منتج -"] + product_list)

    if selected_product != "- اختر منتج -":

        product_row = family_data[family_data["Product"] == selected_product].iloc[0]

        st.subheader("📋 تفاصيل المنتج")
        st.info(f"**الوصف:** {product_row['Description']}")

        # ================== جدول المكونات ==================
        comp_df = pd.DataFrame({
            "المكون": components,
            "الكمية المطلوبة": product_row["Values"]
        })

        comp_df = comp_df[comp_df["الكمية المطلوبة"] > 0].reset_index(drop=True)

        html_comp = comp_df.to_html(index=False, classes='dataframe-html')
        st.markdown(f'<div class="rtl-table-container">{html_comp}</div>', unsafe_allow_html=True)

        st.markdown(f"**عدد الأجزاء المطلوبة: {len(comp_df)}**")

    # ================== عرض جدول كامل للعائلة ==================
    if st.button("📊 عرض جدول كل منتجات العائلة المختارة", use_container_width=True):

        pivot_df = pd.DataFrame(index=components)

        for _, row in family_data.iterrows():
            pivot_df[row["Product"]] = row["Values"]

        pivot_df = pivot_df[pivot_df.sum(axis=1) > 0]

        if pivot_df.empty:
            st.warning("لا توجد بيانات مسجلة لهذه العائلة")
        else:
            pivot_df = pivot_df.reset_index().rename(columns={"index": "المكون"})

            html_pivot = pivot_df.to_html(index=False, classes='dataframe-html')
            st.markdown(f'<div class="rtl-table-container">{html_pivot}</div>', unsafe_allow_html=True)

            st.markdown(f"**عدد الأجزاء المطلوبة: {len(pivot_df)}**")

else:
    st.info("الرجاء اختيار العائلة لبدء العرض.")
