import streamlit as st
import pandas as pd

# ================= إعداد الصفحة =================
st.set_page_config(
    page_title="WaterStar - نظام إدارة قوائم المواد الصناعية",
    layout="wide",
    page_icon="logo.png",  # رابط الصورة أو اسم الملف المحلي
    initial_sidebar_state="collapsed"
)

# ===== RTL CSS + تحسين الزر =====
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
        background-color: #f9f9f9;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
        text-align: right !important;
        direction: rtl !important;
    }

    div[data-baseweb="select"] > div { direction: rtl; text-align: right; }
    
    .rtl-table-container {
        direction: rtl;
        text-align: right;
        overflow-y: auto; 
        overflow-x: auto;
        margin: 20px 0;
        height: 430px; 
        border: 1px solid #e6e9ef;
        border-radius: 8px;
        background-color: #ffffff;
        padding: 5px;
    }
    
    .dataframe-html {
        width: 100%;
        border-collapse: collapse;
        border: none;
    }
    
    .dataframe-html th {
        background-color: #1f77b4;
        padding: 12px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        color: #ffffff;
        border-radius: 20px;
        position: sticky; 
        top: 0;
        z-index: 1;
    }
    
    .dataframe-html td {
        padding: 10px;
        border: 1px solid #e6e9ef;
        text-align: right;
        font-size: 18px;
        font-weight: bold;
    }
    
    .dataframe-html tr:nth-child(even) { background-color: #f2f6fa; }
    
    .stAlert, .stButton>button { direction: rtl; text-align: right; }

    /* تحسين الزر */
    .custom-button {
        background-color: #1f77b4;
        color: white;
        font-size: 20px;
        font-weight: bold;
        padding: 12px 20px;
        border-radius: 10px;
        border: none;
        width: 100%;
        cursor: pointer;
        text-align: center;
        transition: background-color 0.3s ease;
        display: inline-block;
    }
    .custom-button:hover {
        background-color: #105a8b;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===== Header مع اللوجو والاسم =====
col1, col2, col3 = st.columns([1,3,1])
with col1:
    st.write("")
with col2:
    st.image("logo.png", width=150)
with col3:
    st.markdown("<h1 style='color:#1f77b4;'>WaterStar</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#555;font-size:18px;'>نظام إدارة قوائم المواد الصناعية</p>", unsafe_allow_html=True)

st.markdown("---")

# ================= قراءة الملف ==================
file_path = "V2.xlsx"
try:
    df = pd.read_excel(file_path, header=None)
except Exception as e:
    st.error(f"خطأ في قراءة ملف Excel: {e}")
    st.stop()

# ================= استخراج البيانات ==================
components = df.iloc[3:, 0].fillna("غير محدد").astype(str).values
records = []
for col in range(1, df.shape[1]):
    family = df.iloc[0, col]
    product = df.iloc[2, col]
    if pd.isna(family) or pd.isna(product): continue
    records.append({
        "Family": str(family).strip(),
        "Product": str(product).strip(),
        "Description": str(df.iloc[1, col]).strip() if pd.notna(df.iloc[1, col]) else "لا يوجد وصف",
        "Values": pd.to_numeric(df.iloc[3:, col], errors='coerce').fillna(0).values
    })

structured_df = pd.DataFrame(records)

# ================= واجهة المستخدم =================
family_list = sorted(structured_df["Family"].unique())
selected_family = st.selectbox("اختر اسم العائلة", options=["- اختر عائلة -"] + family_list)

if selected_family and selected_family != "- اختر عائلة -":
    family_data = structured_df[structured_df["Family"] == selected_family]
    
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
        st.markdown(f"**عدد الأجزاء المطلوبة: {len(comp_df)}**", unsafe_allow_html=True)

    st.markdown("---")

    # ================= زر الجدول الكبير بتنسيق أفضل =================
    if st.form_submit_button(label="📊 عرض جدول كل منتجات العائلة المختارة"):
        st.subheader(f"جدول منتجات عائلة: {selected_family}")
        
        pivot_df = pd.DataFrame(index=components)
        for _, row in family_data.iterrows():
            pivot_df[row["Product"]] = row["Values"]
        pivot_df = pivot_df[pivot_df.sum(axis=1) > 0]
        
        if pivot_df.empty:
            st.warning("لا توجد بيانات مسجلة لهذه العائلة")
        else:
            pivot_df = pivot_df.reset_index().rename(columns={"index": "المكون"})
            cols = ["المكون"] + sorted([c for c in pivot_df.columns if c != "المكون"])
            pivot_df = pivot_df[cols]
            for col in pivot_df.columns[1:]:
                pivot_df[col] = pivot_df[col].apply(lambda x: f"{x:.3f}" if x != 0 else "-")
            html_pivot = pivot_df.to_html(index=False, classes='dataframe-html')
            st.markdown(f'<div class="rtl-table-container">{html_pivot}</div>', unsafe_allow_html=True)
            st.markdown(f"**عدد الأجزاء المطلوبة: {len(pivot_df)}**", unsafe_allow_html=True)

else:
    st.info("الرجاء اختيار العائلة لبدء العرض.")

st.markdown("---" * 2)
st.markdown("### الأجزاء الغير مستخدمة في أي منتج بالملف كله")

if st.button("عرض الأجزاء الغير موجودة في أي منتج نهائيًا", type="primary", use_container_width=True):
    all_pivot = pd.DataFrame(index=components)
    for _, row in structured_df.iterrows():
        all_pivot[row["Product"]] = row["Values"]
    completely_unused = all_pivot[all_pivot.sum(axis=1) == 0].index.tolist()

    if not completely_unused:
        st.success("كل الأجزاء الموجودة في القايمة مستخدمة في منتج واحد على الأقل ✓")
    else:
        unused_df = pd.DataFrame({"المكون غير المستخدم في أي منتج": completely_unused}).sort_values("المكون غير المستخدم في أي منتج")
        st.warning(f"عدد الأجزاء الغير مستخدمة نهائيًا: **{len(completely_unused)}** جزء")
        html_unused = unused_df.to_html(index=False, classes='dataframe-html')
        st.markdown(f'<div class="rtl-table-container">{html_unused}</div>', unsafe_allow_html=True)
        with st.expander("عرض كقائمة نصية (للنسخ السريع)"):
            st.code("\n".join(completely_unused), language="text")
