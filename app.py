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
        height: 450px;
        border: 1px solid #e6e9ef;
        border-radius: 10px;
    }

    .dataframe-html {
        width: 100%;
        border-collapse: collapse;
    }

    .dataframe-html th {
        background-color: #4694f9;
        padding: 12px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: white;
        position: sticky;
        top: 0;
        z-index: 1;
    }

    .dataframe-html td {
        padding: 10px;
        border: 1px solid #e6e9ef;
        text-align: center;
        font-size: 16px;
    }

    .dataframe-html tr:nth-child(even) {
        background-color: #f8f9fa;
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
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title("📦 نظام عرض مكونات المنتجات (المطور)")
with col3:
    try:
        st.image("logo.png", width=180)
    except:
        st.warning("لوجو غير موجود")

# ================== قراءة ملف Excel (الهيكل الجديد) ==================
file_path = "v7.xlsx"
try:
    # نقرأ الملف، بافتراض أن الصف الأول هو أسماء الأعمدة (المكونات)
    # والعمود الأول هو العائلة، الثاني الوصف، الثالث اسم المنتج
    df_raw = pd.read_excel(file_path)
    
    # تنظيف البيانات الأساسية
    # سنفترض الترتيب التالي للأعمدة بعد الـ Transpose:
    # العمود 0: العائلة (Family)
    # العمود 1: الوصف (Description)
    # العمود 2: اسم المنتج (Product)
    # باقي الأعمدة: المكونات
    
    family_col = df_raw.columns[0]
    desc_col = df_raw.columns[1]
    product_col = df_raw.columns[2]
    components_list = df_raw.columns[3:] # أسماء المكونات هي رؤوس الأعمدة

except Exception as e:
    st.error(f"خطأ في قراءة ملف Excel: {e}")
    st.info("تأكد أن الملف يحتوي على (العائلة، الوصف، المنتج) في أول 3 أعمدة.")
    st.stop()

# ================== اختيار العائلة ==================
family_list = sorted(df_raw[family_col].dropna().unique())
selected_family = st.selectbox("🗂️ اختر اسم العائلة", options=["- اختر عائلة -"] + list(family_list))

if selected_family != "- اختر عائلة -":
    family_data = df_raw[df_raw[family_col] == selected_family]

    # ================== اختيار المنتج ==================
    st.subheader("🔹 اختيار المنتج")
    product_list = sorted(family_data[product_col].dropna().unique())
    selected_product = st.selectbox("📦 اختر المنتج", options=["- اختر منتج -"] + list(product_list))

    if selected_product != "- اختر منتج -":
        product_row = family_data[family_data[product_col] == selected_product].iloc[0]
        
        st.markdown(f"### 📋 تفاصيل المنتج: {selected_product}")
        st.info(f"**الوصف:** {product_row[desc_col]}")

        # =============== استخراج المكونات لهذا المنتج فقط ===============
        # نأخذ المكونات التي قيمتها أكبر من صفر
        comp_values = product_row[components_list]
        comp_df = pd.DataFrame({
            "المكون": components_list,
            "الكمية المطلوبة": comp_values.values
        })
        
        # تحويل الكميات لأرقام وحذف الأصفار
        comp_df["الكمية المطلوبة"] = pd.to_numeric(comp_df["الكمية المطلوبة"], errors='coerce').fillna(0)
        comp_df = comp_df[comp_df["الكمية المطلوبة"] > 0].reset_index(drop=True)

        # عرض الجدول
        html_comp = comp_df.to_html(index=False, classes='dataframe-html')
        st.markdown(f'<div class="rtl-table-container">{html_comp}</div>', unsafe_allow_html=True)
        st.success(f"✅ عدد الأجزاء المطلوبة لهذا المنتج: {len(comp_df)}")

    st.markdown("---")
    
    # ================== عرض جدول مقارنة العائلة كاملة ==================
    if st.button("📊 عرض جدول مقارنة كافة منتجات العائلة", type="primary", use_container_width=True):
        st.subheader(f"جدول منتجات عائلة: {selected_family}")
        
        # نجهز البيانات: المكونات كصفوف والمنتجات كأعمدة (Pivot)
        # نأخذ الأعمدة من المنتج فصاعداً
        pivot_data = family_data.set_index(product_col)[components_list].transpose()
        
        # حذف الصفوف (المكونات) التي لا تستخدم في أي من منتجات هذه العائلة
        pivot_data = pivot_data.loc[(pivot_data.sum(axis=1) > 0)]
        
        if pivot_data.empty:
            st.warning("لا توجد بيانات كميات لهذه العائلة")
        else:
            # إعادة الضبط للعرض
            pivot_display = pivot_data.reset_index().rename(columns={"index": "المكون"})
            
            # تنسيق الأرقام (تبديل الصفر بشرطة للوضوح)
            for col in pivot_display.columns[1:]:
                pivot_display[col] = pivot_display[col].apply(lambda x: f"{x:g}" if (pd.notna(x) and x != 0) else "-")

            html_pivot = pivot_display.to_html(index=False, classes='dataframe-html')
            st.markdown(f'<div class="rtl-table-container">{html_pivot}</div>', unsafe_allow_html=True)
            st.caption(f"إجمالي عدد المكونات المستخدمة في العائلة: {len(pivot_display)}")

else:
    st.info("💡 الرجاء اختيار العائلة من القائمة أعلاه لعرض البيانات.")
