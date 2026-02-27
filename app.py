import streamlit as st
import pandas as pd

# ================== إعداد الصفحة ==================
st.set_page_config(
    page_title="WaterStar - نظام إدارة قوائم المواد",
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
        z-index: 10;
    }

    .dataframe-html td {
        padding: 10px;
        border: 1px solid #e6e9ef;
        text-align: center;
        font-size: 17px;
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
col1, col2 = st.columns([4, 1])
with col1:
    st.title("📦 نظام إدارة وعرض مكونات المنتجات")
with col2:
    try:
        st.image("logo.png", width=180)
    except:
        pass

# ================== معالجة ملف Excel الذكية ==================
file_path = "v8.xlsx"

@st.cache_data
def load_and_structure_data(path):
    # قراءة الملف بدون عناوين لرؤية الهيكل الخام
    raw_df = pd.read_excel(path, header=None)
    
    # 1. استخراج أسماء الأجزاء من الصف الأول (من العمود الرابع فصاعداً)
    # iloc[0, 3:] تعني الصف الأول، من العمود رقم 4 للنهاية
    parts_list = raw_df.iloc[0, 3:].values
    
    # 2. استخراج البيانات الفعلية (من الصف الثاني فصاعداً)
    data_df = raw_df.iloc[1:].copy()
    
    # 3. إعادة تسمية الأعمدة برمجياً
    # أول 3 أعمدة (العائلة، الوصف، المنتج) والباقي أسماء الأجزاء
    custom_columns = ["Family", "Description", "Product"] + list(parts_list)
    data_df.columns = custom_columns
    
    # 4. تنظيف البيانات من القيم الفارغة في الأعمدة الأساسية
    data_df['Family'] = data_df['Family'].astype(str).str.strip()
    data_df['Product'] = data_df['Product'].astype(str).str.strip()
    data_df = data_df[data_df['Family'] != "nan"] # حذف الصفوف الفارغة
    
    return data_df, list(parts_list)

try:
    df, all_parts = load_and_structure_data(file_path)
except Exception as e:
    st.error(f"خطأ في معالجة الملف: {e}")
    st.stop()

# ================== واجهة اختيار المنتج ==================

# اختيار العائلة
family_list = sorted(df["Family"].unique())
selected_family = st.selectbox("🗂️ اختر اسم العائلة", options=["- اختر عائلة -"] + family_list)

if selected_family != "- اختر عائلة -":
    family_data = df[df["Family"] == selected_family]

    # اختيار المنتج
    product_list = sorted(family_data["Product"].unique())
    selected_product = st.selectbox("📦 اختر المنتج النهائي", options=["- اختر منتج -"] + product_list)

    if selected_product != "- اختر product -":
        # جلب صف المنتج المختار
        product_row = family_data[family_data["Product"] == selected_product].iloc[0]
        
        st.markdown(f"### 📋 تفاصيل: {selected_product}")
        st.info(f"**الوصف:** {product_row['Description']}")

        # تجميع المجزاء التي كميتها أكبر من صفر لهذا المنتج
        comp_items = []
        for p_name in all_parts:
            val = product_row[p_name]
            try:
                num_val = float(val)
                if num_val > 0:
                    comp_items.append({"المكون (الجزء)": p_name, "الكمية المطلوبة": num_val})
            except:
                continue
        
        if comp_items:
            comp_df = pd.DataFrame(comp_items)
            html_comp = comp_df.to_html(index=False, classes='dataframe-html')
            st.markdown(f'<div class="rtl-table-container">{html_comp}</div>', unsafe_allow_html=True)
            st.success(f"✅ إجمالي الأجزاء المطلوبة: {len(comp_df)}")
        else:
            st.warning("لا توجد كميات مسجلة لهذا المنتج.")

    # ================== جدول مقارنة العائلة ==================
    st.markdown("---")
    if st.button("📊 عرض جدول مقارنة كافة منتجات العائلة", type="primary", use_container_width=True):
        st.subheader(f"مقارنة منتجات عائلة: {selected_family}")
        
        # قلب الجدول: الأجزاء تصبح صفوف والمنتجات تصبح أعمدة
        pivot_df = family_data.set_index("Product")[all_parts].transpose()
        
        # حذف المكونات التي لا تستخدم نهائياً في هذه العائلة (مجموعها صفر)
        pivot_df = pivot_df.loc[(pivot_df.fillna(0).astype(float).sum(axis=1) > 0)]
        
        if not pivot_df.empty:
            pivot_display = pivot_df.reset_index().rename(columns={"index": "المكون / الجزء"})
            
            # تنسيق الأرقام: استبدال 0 أو NaN بشرطة لسهولة القراءة
            for col in pivot_display.columns[1:]:
                pivot_display[col] = pivot_display[col].apply(
                    lambda x: f"{x:g}" if (pd.notna(x) and x != 0) else "-"
                )
            
            html_pivot = pivot_display.to_html(index=False, classes='dataframe-html')
            st.markdown(f'<div class="rtl-table-container">{html_pivot}</div>', unsafe_allow_html=True)
        else:
            st.warning("لا توجد بيانات كميات لهذه العائلة.")

else:
    st.info("💡 يرجى اختيار اسم العائلة لعرض المنتجات المتاحة.")

