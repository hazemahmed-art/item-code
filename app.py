import streamlit as st
import pandas as pd

# ================== إعداد الصفحة ==================
st.set_page_config(
    page_title="WaterStar - نظام إدارة المكونات",
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
        max-height: 500px;
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
        font-weight: bold;
    }

    .dataframe-html tr:nth-child(even) {
        background-color: #f8f9fa;
    }

    .stSelectbox label { font-size: 18px !important; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== عرض اللوجو و العنوان ==================
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title("📦 نظام عرض مكونات المنتجات (الهيكل الأفقي)")
with col3:
    try:
        st.image("logo.png", width=180)
    except:
        pass

# ================== قراءة ملف Excel ==================
file_path = "v7.xlsx"
try:
    # نقرأ الملف مع اعتبار الصف الأول هو رأس الجدول (Headers)
    df = pd.read_excel(file_path)
    
    # أسماء الأعمدة الأساسية بناءً على وصفك
    family_col = df.columns[0]   # العمود 1: العائلة
    desc_col = df.columns[1]     # العمود 2: الوصف
    product_col = df.columns[2]  # العمود 3: اسم المنتج النهائي
    parts_columns = df.columns[3:] # من العمود 4 فصاعداً: الأجزاء

except Exception as e:
    st.error(f"خطأ في قراءة ملف Excel: {e}")
    st.stop()

# ================== اختيار العائلة ==================
family_list = sorted(df[family_col].dropna().unique())
selected_family = st.selectbox("🗂️ اختر اسم العائلة", options=["- اختر عائلة -"] + list(family_list))

if selected_family != "- اختر عائلة -":
    family_data = df[df[family_col] == selected_family]

    # ================== اختيار المنتج ==================
    st.subheader("🔹 اختيار المنتج النهائي")
    product_list = sorted(family_data[product_col].dropna().unique())
    selected_product = st.selectbox("📦 اختر المنتج", options=["- اختر منتج -"] + list(product_list))

    if selected_product != "- اختر منتج -":
        # الحصول على صف المنتج المختار
        product_row = family_data[family_data[product_col] == selected_product].iloc[0]
        
        st.markdown(f"### 📋 تفاصيل المنتج: {selected_product}")
        st.info(f"**الوصف:** {product_row[desc_col]}")

        # --- استخراج المكونات لهذا المنتج ---
        # ننشئ DataFrame من أجزاء هذا الصف فقط
        comp_df = pd.DataFrame({
            "المكون (الجزء)": parts_columns,
            "الكمية المطلوبة": product_row[parts_columns].values
        })
        
        # تنظيف البيانات: تحويل لأرقام، حذف الأصفار، وحذف الـ NaN
        comp_df["الكمية المطلوبة"] = pd.to_numeric(comp_df["الكمية المطلوبة"], errors='coerce').fillna(0)
        comp_df = comp_df[comp_df["الكمية المطلوبة"] > 0].reset_index(drop=True)

        # عرض الجدول
        html_comp = comp_df.to_html(index=False, classes='dataframe-html')
        st.markdown(f'<div class="rtl-table-container">{html_comp}</div>', unsafe_allow_html=True)
        st.success(f"✅ عدد الأجزاء المطلوبة لهذا المنتج: {len(comp_df)}")

    st.markdown("---")
    
    # ================== عرض جدول العائلة كاملة (مقارنة) ==================
    if st.button("📊 عرض جدول مقارنة كافة منتجات العائلة", type="primary", use_container_width=True):
        st.subheader(f"جدول منتجات عائلة: {selected_family}")
        
        # نقوم بعمل Pivot لعرض المنتجات كأعمدة والأجزاء كصفوف للسهولة
        comparison_df = family_data.set_index(product_col)[parts_columns].transpose()
        
        # حذف الأجزاء التي لا تستخدم في أي منتج من هذه العائلة (قيمها كلها صفر)
        comparison_df = comparison_df.loc[(comparison_df.fillna(0).sum(axis=1) > 0)]
        
        if comparison_df.empty:
            st.warning("لا توجد بيانات كميات مسجلة لهذه العائلة")
        else:
            # إعادة الترتيب للعرض
            comparison_display = comparison_df.reset_index().rename(columns={"index": "المكون / الجزء"})
            
            # تنسيق القيم (تبديل الصفر بشرطة)
            for col in comparison_display.columns[1:]:
                comparison_display[col] = comparison_display[col].apply(
                    lambda x: f"{x:g}" if (pd.notna(x) and x != 0) else "-"
                )

            html_pivot = comparison_display.to_html(index=False, classes='dataframe-html')
            st.markdown(f'<div class="rtl-table-container">{html_pivot}</div>', unsafe_allow_html=True)
            st.caption(f"عدد الأجزاء المختلفة المستخدمة في هذه العائلة: {len(comparison_display)}")

else:
    st.info("💡 الرجاء اختيار العائلة لبدء العرض.")
