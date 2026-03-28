import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="HR Management System", layout="wide")

# تنسيق الواجهة لتدعم اللغة العربية والخطوط واليمين
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    [data-testid="stSidebarNav"] { text-align: right; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; gap: 20px; }
    .stTabs [data-baseweb="tab"] { 
        padding: 10px 20px; 
        background-color: #f0f2f6; 
        border-radius: 10px;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #007bff !important; 
        color: white !important; 
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📂 نظام إدارة الموارد البشرية والرواتب الموحد")
st.divider()

# --- 2. إدارة البيانات (Session State) ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = None

# القائمة الجانبية لإعدادات الماستر داتا والشركة
with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    uploaded_file = st.file_uploader("ارفع ملف الماستر داتا (إكسل)", type=['xlsx'])
    if st.button("تحديث قاعدة البيانات الثابتة"):
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            # إضافة أعمدة المؤثرات الشهرية إذا لم تكن موجودة
            cols = ['مكافآت', 'حسومات', 'أيام غياب', 'الحالة']
            for col in cols:
                if col not in df.columns:
                    df[col] = 0.0 if col != 'الحالة' else 'نشط'
            st.session_state.master_data = df
            st.success("تم تحميل بيانات الموظفين بنجاح!")
    
    st.divider()
    if st.session_state.master_data is not None:
        companies = ["الكل"] + st.session_state.master_data['الشركة'].unique().tolist()
        selected_co = st.selectbox("🎯 اختر الشركة:", companies)

# --- 3. عرض التبويبات (أيقونات النظام) ---
if st.session_state.master_data is not None:
    
    tab1, tab2, tab3 = st.tabs(["👥 قائمة الموظفين", "✍️ المؤثرات الشهرية", "💰 سحب الرواتب"])

    # --- التبويب الأول: قائمة الموظفين بجميع تفاصيلهم ---
    with tab1:
        st.subheader("📋 تفاصيل بيانات الموظفين الثابتة")
        df_view = st.session_state.master_data
        if selected_co != "الكل":
            df_view = df_view[df_view['الشركة'] == selected_co]
        
        # محرك بحث سريع بالاسم
        search = st.text_input("🔍 ابحث عن موظف معين بالاسم...")
        if search:
            df_view = df_view[df_view['اسم الموظف'].str.contains(search, na=False)]
            
        st.dataframe(df_view, use_container_width=True, hide_index=True)

    # --- التبويب الثاني: المؤثرات الشهرية ---
    with tab2:
        st.subheader("📝 إضافة المؤثرات (مكافآت، حسومات، غياب)")
        
        # تصفية قائمة الأسماء حسب الشركة المختارة للتبسيط
        emp_filter = st.session_state.master_data
        if selected_co != "الكل":
            emp_filter = emp_filter[emp_filter['الشركة'] == selected_co]
            
        with st.form("effect_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                target_emp = st.selectbox("اسم الموظف المستهدف:", emp_filter['اسم الموظف'].unique())
                effect_type = st.selectbox("نوع المؤثر الشهري:", ["مكافأة", "حسم", "عدد أيام غياب", "تغيير حالة الموظف"])
            with c2:
                value = st.number_input("القيمة (بالريال أو بالأيام):", min_value=0.0, step=1.0)
                status_radio = st.radio("تعديل الحالة إلى:", ["نشط", "موقوف"], horizontal=True)
            
            if st.form_submit_button("إضافة المؤثر وحفظ"):
                idx = st.session_state.master_data.index[st.session_state.master_data['اسم الموظف'] == target_emp].tolist()[0]
                
                if effect_type == "مكافأة": st.session_state.master_data.at[idx, 'مكافآت'] = value
                elif effect_type == "حسم": st.session_state.master_data.at[idx, 'حسومات'] = value
                elif effect_type == "عدد أيام غياب": st.session_state.master_data.at[idx, 'أيام غياب'] = value
                
                st.session_state.master_data.at[idx, 'الحالة'] = status_radio
                st.success(f"تم تحديث بيانات الموظف: {target_emp}")
                st.rerun()

    # --- التبويب الثالث: سحب الرواتب والمسير ---
    with tab3:
        st.subheader("💵 كشف مسير الرواتب الشهري")
        
        # إنشاء نسخة للحسابات
        payroll_df = st.session_state.master_data.copy()
        if selected_co != "الكل":
            payroll_df = payroll_df[payroll_df['الشركة'] == selected_co]
            
        # عملية حساب صافي الراتب (الأساسي + المكافآت - الحسومات)
        if 'الراتب الأساسي' in payroll_df.columns:
            payroll_df['صافي المستحق'] = (
                payroll_df['الراتب الأساسي'] + 
                payroll_df['مكافآت'] - 
                payroll_df['حسومات']
            )
            
        st.dataframe(payroll_df, use_container_width=True, hide_index=True)
        
        # زر سحب المسير (Excel/CSV)
        st.divider()
        st.markdown("### 📥 سحب التقارير")
        csv_final = payroll_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label=f"📥 سحب مسير رواتب ({selected_co}) بصيغة Excel",
            data=csv_data, # ملاحظة: تأكد من تحويله لـ CSV متوافق مع الإكسل
            file_name=f"Payroll_Report_{selected_co}_{datetime.now().strftime('%Y-%m')}.csv",
            mime='text/csv'
        )

else:
    st.info("👋 مرحباً بك! يرجى رفع ملف الماستر داتا من القائمة الجانبية (Sidebar) لبدء العمل على النظام.")
