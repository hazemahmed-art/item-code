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
        height: 500px;
        border: 1px solid #e6e9ef;
        border-radius: 5px;
    }

    .dataframe-html {
        width: 100%;
        border-collapse: collapse;
        border: none;
    }

    .dataframe-html th {
        background-color: #4694f9;
        padding: 12px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: white;
        white-space: nowrap;
        position: sticky;
        top: 0;
        z-index: 10;
    }

    .dataframe-html td {
        padding: 10px;
        border: 1px solid #e6e9ef;
        text-align: center;
        font-size: 16px;
        font-weight: bold;
    }

    .dataframe-html tr:nth-child(even) {
        background-color: #fafafa;
    }

    .stAlert, .stButton>button {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== عرض اللوجو و العنوان ==================
col1, col2, col3 = st.columns([3, 3, 1])
with col1:
    st.title("📦 نظام عرض مكونات المنتجات")
with col3:
    # ملاحظة: تأكد من وجود ملف logo.png في نفس المجلد
    try:
        st.image("logo.png", width=220)
    except:
        pass

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
    family = df.iloc[0, col]
    product = df.iloc[2, col]
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

    # ================== اختيار المنتج الفردي ==================
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
        st.markdown(f"**عدد الأجزاء المطلوبة: {len(comp_df)}**")
        st.markdown("---")

    # ================== عرض الجدول المحول (Transposed) ==================
    if st.button("📊 عرض جدول المقارنة الأفقي للعائلة", type="primary", use_container_width=True):
        st.subheader(f"جدول مقارنة عائلة: {selected_family}")

        # 1. إنشاء مصفوفة القيم (المكونات هي الأعمدة)
        transposed_data = []
        for _, row in family_data.iterrows():
            entry = {
                "العائلة (Family)": row["Family"],
                "الوصف (Description)": row["Description"],
                "المنتج النهائي (Final Product)": row["Product"]
            }
            # إضافة المكونات كأعمدة
            for i, comp_name in enumerate(components):
                val = row["Values"][i]
                entry[comp_name] = val
            transposed_data.append(entry)

        final_pivot = pd.DataFrame(transposed_data)

        # 2. حذف أعمدة المكونات التي لا تستخدم في أي منتج من العائلة (كل قيمها 0)
        # نحدد أعمدة المكونات فقط (تجاهل أول 3 أعمدة)
        comp_cols = list(components)
        cols_to_keep = ["العائلة (Family)", "الوصف (Description)", "المنتج النهائي (Final Product)"]
        
        # تصفية المكونات التي تحتوي على قيم أكبر من صفر
        active_comps = [c for c in comp_cols if (final_pivot[c] > 0).any()]
        final_pivot = final_pivot[cols_to_keep + active_comps]

        # 3. تنسيق الأرقام (تغيير 0 إلى "-" وتنسيق الكسور)
        for col in active_comps:
            final_pivot[col] = final_pivot[col].apply(lambda x: f"{x:.3f}" if x != 0 else "-")

        # 4. عرض الجدول
        html_pivot = final_pivot.to_html(index=False, classes='dataframe-html')
        st.markdown(f'<div class="rtl-table-container">{html_pivot}</div>', unsafe_allow_html=True)
        st.caption(f"تم عرض {len(active_comps)} مكوناً مستخدماً في هذه العائلة.")

else:
    st.info("الرجاء اختيار العائلة لبدء العرض.")
