import streamlit as st
import pandas as pd

# ================== إعداد الصفحة ==================
st.set_page_config(
    page_title="WaterStar - إدارة قوائم المواد",
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
    .rtl-table-container {
        direction: rtl;
        margin: 20px 0;
        max-height: 500px;
        overflow: auto;
        border: 1px solid #e6e9ef;
        border-radius: 10px;
    }
    .dataframe-html {
        width: 100%;
        border-collapse: collapse;
    }
    .dataframe-html th {
        background-color: #4694f9;
        color: white;
        padding: 12px;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .dataframe-html td {
        padding: 10px;
        border: 1px solid #e6e9ef;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
    }
    .stSelectbox label { font-size: 18px !important; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== العنوان واللوجو ==================
col1, col2 = st.columns([4, 1])
with col1:
    st.title("📦 نظام عرض مكونات المنتجات")
with col2:
    try: st.image("logo.png", width=150)
    except: pass

# ================== قراءة ومعالجة البيانات ==================
file_path = "v7.xlsx"
try:
    # نقرأ الملف (الصف الأول هو العناوين تلقائياً)
    df = pd.read_excel(file_path)
    
    # 1. إعادة تسمية أول 3 أعمدة لأنها "فاضية" في الإكسيل عندك
    # العمود 0 -> العائلة، العمود 1 -> الوصف، العمود 2 -> المنتج
    new_cols = list(df.columns)
    new_cols[0] = "العائلة"
    new_cols[1] = "الوصف"
    new_cols[2] = "المنتج_النهائي"
    df.columns = new_cols

    # 2. تحديد أسماء الأجزاء (بقية الأعمدة من الرابع للأخير)
    parts_columns = df.columns[3:]

    # 3. تنظيف البيانات (حذف الصفوف التي لا تحتوي على اسم عائلة)
    df = df.dropna(subset=["العائلة"])

except Exception as e:
    st.error(f"حدث خطأ في قراءة الملف: {e}")
    st.stop()

# ================== واجهة المستخدم ==================

# --- اختيار العائلة ---
family_options = sorted(df["العائلة"].unique().astype(str))
selected_family = st.selectbox(
    "🗂️ اختر اسم العائلة", 
    options=["- اختر عائلة -"] + family_options
)

if selected_family != "- اختر عائلة -":
    # فلترة حسب العائلة
    family_data = df[df["العائلة"].astype(str) == selected_family]

    # --- اختيار المنتج ---
    product_options = sorted(family_data["المنتج_النهائي"].unique().astype(str))
    selected_product = st.selectbox(
        "📦 اختر المنتج النهائي", 
        options=["- اختر منتج -"] + product_options
    )

    if selected_product != "- اختر منتج -":
        # جلب بيانات المنتج
        product_row = family_data[family_data["المنتج_النهائي"].astype(str) == selected_product].iloc[0]
        
        st.markdown(f"### 📋 تفاصيل: {selected_product}")
        st.info(f"📝 **الوصف:** {product_row['الوصف']}")

        # استخراج المكونات (التي قيمتها أكبر من 0)
        comp_list = []
        for part in parts_columns:
            val = product_row[part]
            # التأكد أن القيمة رقمية وأكبر من صفر
            try:
                numeric_val = float(val)
                if numeric_val > 0:
                    comp_list.append({"المكون (الجزء)": part, "الكمية": numeric_val})
            except:
                continue
        
        comp_df = pd.DataFrame(comp_list)

        if not comp_df.empty:
            html_table = comp_df.to_html(index=False, classes='dataframe-html')
            st.markdown(f'<div class="rtl-table-container">{html_table}</div>', unsafe_allow_html=True)
            st.success(f"✅ إجمالي عدد الأجزاء: {len(comp_df)}")
        else:
            st.warning("لا توجد كميات مسجلة لهذا المنتج.")

    # --- زر عرض الجدول الشامل للعائلة ---
    st.write("---")
    if st.button("📊 عرض مقارنة شاملة لكل منتجات العائلة", use_container_width=True):
        # تجهيز جدول المقارنة (المنتجات أعمدة والأجزاء صفوف)
        pivot_df = family_data.set_index("المنتج_النهائي")[parts_columns].transpose()
        
        # حذف الأجزاء التي لا تستخدم في أي منتج من العائلة
        pivot_df = pivot_df.loc[(pivot_df.fillna(0).astype(float).sum(axis=1) > 0)]
        
        if not pivot_df.empty:
            pivot_display = pivot_df.reset_index().rename(columns={"index": "المكون"})
            # تنسيق الأرقام لتبديل الأصفار بشرطة
            for col in pivot_display.columns[1:]:
                pivot_display[col] = pivot_display[col].apply(lambda x: f"{x:g}" if (pd.notna(x) and x != 0) else "-")
            
            st.markdown(f'<div class="rtl-table-container">{pivot_display.to_html(index=False, classes="dataframe-html")}</div>', unsafe_allow_html=True)
        else:
            st.warning("لا توجد بيانات متاحة للعرض.")

else:
    st.info("💡 الرجاء اختيار العائلة من القائمة أعلاه.")
