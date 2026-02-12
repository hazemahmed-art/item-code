import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="نظام مكونات المنتجات", layout="wide")

# ===== RTL CSS الشامل =====
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

    div[data-baseweb="select"] > div { direction: rtl; text-align: right; }
    
    .rtl-table-container {
        direction: rtl;
        text-align: right;
        /* تفعيل التمرير العمودي فقط */
        overflow-y: auto; 
        overflow-x: auto;
        margin: 20px 0;
        /* تحديد الارتفاع ليظهر تقريباً 9 صفوف (Header + 9 rows) */
        height: 430px; 
        border: 1px solid #e6e9ef;
        border-radius: 5px;
    }
    
    .dataframe-html {
        width: 100%;
        border-collapse: collapse;
        border: none; /* إزالة الحدود الداخلية للجدول لتناسب الحاوية */
    }
    
    .dataframe-html th {
        background-color: #4694f9;
        padding: 12px;
        text-align: center;
        font-size: 23px;
        font-weight: bold;
        color: rgb(255, 255, 255);
        border-radius: 30px;
        position: sticky; 
        top: 0;
        z-index: 1;
    }
    
    .dataframe-html td {
        padding: 10px;
        border: 1px solid #e6e9ef;
        text-align: right;
        font-size: 20px;
        font-weight: bold;
    }
    
    .dataframe-html tr:nth-child(even) { background-color: #fafafa; }
    
    .stAlert, .stButton>button { direction: rtl; text-align: right; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📦 نظام عرض مكونات المنتجات")

# ================== قراءة الملف ==================
file_path = "V2.xlsx"
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
    if pd.isna(family) or pd.isna(product): continue
    records.append({
        "Family": str(family).strip(),
        "Product": str(product).strip(),
        "Description": str(df.iloc[1, col]).strip() if pd.notna(df.iloc[1, col]) else "لا يوجد وصف",
        "Values": pd.to_numeric(df.iloc[3:, col], errors='coerce').fillna(0).values
    })

structured_df = pd.DataFrame(records)

# ================== الواجهة ==================
family_list = sorted(structured_df["Family"].unique())
selected_family = st.selectbox("اختر اسم العائلة", options=["- اختر عائلة -"] + family_list)

if selected_family and selected_family != "- اختر عائلة -":
    family_data = structured_df[structured_df["Family"] == selected_family]
    
    st.subheader("1. اختيار المنتج")
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
        # إظهار الصفوف التي بها قيمة فقط للمنتج المختار
        comp_df = comp_df[comp_df["الكمية المطلوبة"] > 0].reset_index(drop=True)
        
        html_comp = comp_df.to_html(index=False, classes='dataframe-html')
        st.markdown(f'<div class="rtl-table-container">{html_comp}</div>', unsafe_allow_html=True)
        
        # --- عداد الأجزاء (الجدول الأول) ---
        st.markdown(f"**عدد الأجزاء المطلوبة: {len(comp_df)}**", unsafe_allow_html=True)

    st.markdown("---")
    # ──────────────────────────────── زر الجدول الكبير مع الفلترة ────────────────────────────────
    if st.button("📊 عرض جدول كل منتجات العائلة المختارة", type="primary", use_container_width=True):
        st.subheader(f"جدول منتجات عائلة: {selected_family}")
        
        # بناء الـ Pivot Table
        pivot_df = pd.DataFrame(index=components)
        for _, row in family_data.iterrows():
            pivot_df[row["Product"]] = row["Values"]
        
        # --- التعديل الجوهري: حذف الصفوف التي مجموعها صفر في كل الأعمدة ---
        # نقوم بجمع الصفوف عرضياً، وإبقاء الصفوف التي مجموعها أكبر من 0
        pivot_df = pivot_df[pivot_df.sum(axis=1) > 0]
        
        if pivot_df.empty:
            st.warning("لا توجد بيانات مسجلة لهذه العائلة")
        else:
            pivot_df = pivot_df.reset_index().rename(columns={"index": "المكون"})
            
            # ترتيب الأعمدة: المكون أولاً
            cols = ["المكون"] + sorted([c for c in pivot_df.columns if c != "المكون"])
            pivot_df = pivot_df[cols]

            # تنسيق الأرقام لتبدو نظيفة
            for col in pivot_df.columns[1:]:
                pivot_df[col] = pivot_df[col].apply(lambda x: f"{x:.3f}" if x != 0 else "-")

            html_pivot = pivot_df.to_html(index=False, classes='dataframe-html')
            st.markdown(f'<div class="rtl-table-container">{html_pivot}</div>', unsafe_allow_html=True)
            
            # --- عداد الأجزاء (الجدول الثاني) ---
            st.markdown(f"**عدد الأجزاء المطلوبة: {len(pivot_df)}**", unsafe_allow_html=True)

else:

    st.info("الرجاء اختيار العائلة لبدء العرض.")
