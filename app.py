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
    div[data-baseweb="select"] > div {
        direction: rtl;
        text-align: right;
    }
    .rtl-table-container {
        direction: rtl;
        text-align: right;
        overflow-y: auto;
        overflow-x: auto;
        margin: 20px 0;
        max-height: 520px;
        border: 1px solid #e6e9ef;
        border-radius: 8px;
    }
    .dataframe-html {
        width: 100%;
        border-collapse: collapse;
        border: none;
        font-size: 19px;
    }
    .dataframe-html th {
        background-color: #4694f9;
        padding: 10px 8px;
        text-align: center;
        font-size: 21px;
        font-weight: bold;
        color: white;
        position: sticky;
        top: 0;
        z-index: 2;
        min-width: 120px;
    }
    .dataframe-html td {
        padding: 9px 10px;
        border: 1px solid #e0e0e0;
        text-align: center;
        font-size: 19px;
        min-width: 110px;
    }
    .dataframe-html tr:nth-child(even) {
        background-color: #f8fbff;
    }
    .dataframe-html .component-col {
        background-color: #e6f0ff !important;
        font-weight: bold;
        position: sticky;
        left: 0;
        z-index: 1;
        min-width: 220px;
    }
    .stAlert, .stButton>button {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== عرض اللوجو والعنوان ==================
col1, col2, col3 = st.columns([4, 4, 1])
with col1:
    st.title("📦 نظام عرض مكونات المنتجات")
with col3:
    st.image("logo.png", width=200)

# ================== قراءة ملف Excel ==================
file_path = "v8.xlsx"
try:
    df = pd.read_excel(file_path, header=None)
except Exception as e:
    st.error(f"خطأ في قراءة ملف Excel: {e}")
    st.stop()

# ================== استخراج البيانات ==================
components = df.iloc[3:, 0].fillna("غير محدد").astype(str).values

records = []
for col in range(1, df.shape[1]):
    family   = df.iloc[0, col]
    product  = df.iloc[2, col]
    if pd.isna(family) or pd.isna(product):
        continue
    records.append({
        "Family": str(family).strip(),
        "Product": str(product).strip(),
        "Description": str(df.iloc[1, col]).strip() if pd.notna(df.iloc[1, col]) else "لا يوجد وصف",
        "Values": pd.to_numeric(df.iloc[3:, col], errors='coerce').fillna(0).values
    })

structured_df = pd.DataFrame(records)

# ================== اختيار العائلة ==================
family_list = sorted(structured_df["Family"].unique())
selected_family = st.selectbox("اختر اسم العائلة", options=["- اختر عائلة -"] + family_list)

if selected_family and selected_family != "- اختر عائلة -":

    family_data = structured_df[structured_df["Family"] == selected_family]

    # ================== اختيار المنتج (تفاصيل منتج واحد) ==================
    st.subheader("🔸 اختيار المنتج")
    product_list = sorted(family_data["Product"].unique())
    selected_product = st.selectbox("اختر المنتج", options=["- اختر منتج -"] + product_list)

    if selected_product and selected_product != "- اختر منتج -":
        st.subheader("📋 تفاصيل المنتج")
        product_row = family_data[family_data["Product"] == selected_product].iloc[0]
        st.info(f"**الوصف:** {product_row['Description']}")

        comp_df = pd.DataFrame({
            "المكون": components,
            "الكمية المطلوبة": product_row["Values"]
        })
        comp_df = comp_df[comp_df["الكمية المطلوبة"] > 0].reset_index(drop=True)

        html_comp = comp_df.to_html(index=False, classes='dataframe-html')
        st.markdown(f'<div class="rtl-table-container">{html_comp}</div>', unsafe_allow_html=True)
        st.markdown(f"**عدد المكونات المطلوبة: {len(comp_df)}**")
        st.markdown("---")

    # ================== عرض الجدول المنقول لكل المنتجات ==================
    if st.button("📊 عرض جدول كل منتجات العائلة (منقول)", type="primary", use_container_width=True):

        st.subheader(f"جدول مكونات عائلة: {selected_family}")

        # بناء الجدول المنقول
        pivot_df = pd.DataFrame(index=components)
        for _, row in family_data.iterrows():
            pivot_df[row["Product"]] = row["Values"]

        # حذف الصفوف التي كلها صفر
        pivot_df = pivot_df.loc[pivot_df.sum(axis=1) > 0]

        if pivot_df.empty:
            st.warning("لا توجد بيانات صالحة لهذه العائلة")
        else:
            # إعادة ترتيب الأعمدة
            product_columns = sorted(pivot_df.columns)
            pivot_df = pivot_df[product_columns]

            # تحويل إلى تنسيق جميل + استبدال 0 بـ "-"
            styled_df = pivot_df.reset_index().rename(columns={"index": "المكون"})

            for col in product_columns:
                styled_df[col] = styled_df[col].apply(
                    lambda x: f"{float(x):.3f}" if float(x) > 0 else "—"
                )

            # إضافة class لعمود المكون ليبقى مثبت
            html_pivot = styled_df.to_html(
                index=False,
                classes='dataframe-html',
                escape=False
            )

            # لتثبيت عمود المكون يمكن إضافة class يدوياً
            html_pivot = html_pivot.replace(
                '<th>المكون</th>',
                '<th class="component-col">المكون</th>'
            ).replace(
                '<td>المكون</td>',
                '<td class="component-col">المكون</td>'
            )

            st.markdown(f'<div class="rtl-table-container">{html_pivot}</div>', unsafe_allow_html=True)
            st.markdown(f"**عدد المكونات المستخدمة: {len(styled_df)}**")

else:
    st.info("الرجاء اختيار العائلة لبدء العرض.")
