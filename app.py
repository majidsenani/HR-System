import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="نظام رواتب أمنكو ومبرد", layout="wide")

st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    [data-testid="stSidebarNav"] { text-align: right; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; gap: 15px; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #dee2e6; }
    </style>
    """, unsafe_allow_html=True)

st.title("📂 نظام إدارة المسيرات والبيانات الأساسية")

if 'master_data' not in st.session_state:
    st.session_state.master_data = None

# --- 2. القائمة الجانبية (رفع البيانات) ---
with st.sidebar:
    st.header("⚙️ إعدادات قاعدة البيانات")
    uploaded_file = st.file_uploader("ارفع ملف (ماستر داتا.xlsx)", type=['xlsx', 'csv'])
    
    if st.button("تحديث النظام بالبيانات الجديدة"):
        if uploaded_file:
            df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
            df.columns = df.columns.str.strip() # تنظيف المسافات من أسماء الأعمدة
            
            # إضافة أعمدة المؤثرات الشهرية إذا لم تكن موجودة في ملفك الأصلي
            for col in ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب', 'حالة القيد']:
                if col not in df.columns:
                    df[col] = 0.0 if col != 'حالة القيد' else 'نشط'
            
            st.session_state.master_data = df
            st.success("✅ تم ربط البيانات بنجاح")

# --- 3. تبويبات النظام ---
if st.session_state.master_data is not None:
    
    # فلتر الشركة والفرع (موجودين في ملفك)
    st.sidebar.divider()
    all_cos = ["الكل"] + st.session_state.master_data['الشركة'].unique().tolist()
    selected_co = st.sidebar.selectbox("تصفية حسب الشركة:", all_cos)
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 قائمة الموظفين الشاملة", "✍️ المؤثرات الشهرية", "⚙️ تعديل بيانات موظف", "💰 إنشاء المسير النهائي"])

    # --- التبويب الأول: عرض كامل البيانات ---
    with tab1:
        st.subheader("📋 سجل الموظفين التفصيلي")
        display_df = st.session_state.master_data
        if selected_co != "الكل":
            display_df = display_df[display_df['الشركة'] == selected_co]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    # --- التبويب الثاني: المؤثرات (بالرقم الوظيفي أمنكو) ---
    with tab2:
        st.subheader("📝 رصد المتغيرات الشهرية")
        col_find, col_act = st.columns([1, 2])
        
        with col_find:
            search_id = st.text_input("🔍 ادخل الرقم الوظيفي أمنكو:")
            # البحث في عمود "الرقم الوظيفي امنكو" كما ورد في ملفك
            target = st.session_state.master_data[st.session_state.master_data['الرقم الوظيفي امنكو'].astype(str) == search_id]
            
            if not target.empty:
                st.success(f"الموظف: {target.iloc[0]['اسم الموظف']}")
                st.write(f"المشروع: {target.iloc[0]['المشروع']}")
            elif search_id:
                st.error("الرقم الوظيفي غير موجود")

        if not target.empty:
            with col_act:
                with st.form("eff_form"):
                    type_e = st.selectbox("نوع المؤثر:", ["مكافأة", "حسم", "غياب (تاريخ)"])
                    
                    if type_e == "غياب (تاريخ)":
                        d_from = st.date_input("من تاريخ:")
                        d_to = st.date_input("إلى تاريخ:")
                        calc_days = (d_to - d_from).days + 1
                        st.info(f"عدد الأيام: {calc_days}")
                        val = float(calc_days)
                    else:
                        val = st.number_input("القيمة بالريال:", min_value=0.0)
                    
                    if st.form_submit_button("حفظ المؤثر"):
                        idx = target.index[0]
                        col_target = 'مكافآت شهرية' if type_e == "مكافأة" else ('حسومات شهرية' if type_e == "حسم" else 'أيام غياب')
                        st.session_state.master_data.at[idx, col_target] = val
                        st.success("تم الحفظ")
                        st.rerun()

    # --- التبويب الثالث: تعديل البيانات الثابتة ---
    with tab3:
        st.subheader("⚙️ تعديل (الراتب، المشروع، المسمى، البنك)")
        emp_name = st.selectbox("اختر اسم الموظف للتعديل:", st.session_state.master_data['اسم الموظف'].unique())
        row = st.session_state.master_data[st.session_state.master_data['اسم الموظف'] == emp_name].iloc[0]
        
        with st.form("edit_master"):
            c1, c2, c3 = st.columns(3)
            with c1:
                new_basic = st.number_input("الراتب الأساسي:", value=float(row['الراتب الأساسي ']))
                new_housing = st.number_input("بدل السكن:", value=float(row['بدل السكن']))
            with c2:
                new_project = st.text_input("المشروع:", value=str(row['المشروع']))
                new_job = st.text_input("المسمى الوظيفي:", value=str(row['المسمي الوظيفي ']))
            with c3:
                new_iban = st.text_input("الآيبان:", value=str(row['الايبان']))
                new_status = st.radio("حالة القيد:", ["نشط", "موقوف"], index=0 if row['حالة القيد'] == 'نشط' else 1)
            
            if st.form_submit_button("تحديث البيانات الأساسية"):
                idx = st.session_state.master_data.index[st.session_state.master_data['اسم الموظف'] == emp_name][0]
                # تحديث القيم في الجدول الرئيسي
                st.session_state.master_data.at[idx, 'الراتب الأساسي '] = new_basic
                st.session_state.master_data.at[idx, 'بدل السكن'] = new_housing
                st.session_state.master_data.at[idx, 'المشروع'] = new_project
                st.session_state.master_data.at[idx, 'الايبان'] = new_iban
                st.session_state.master_data.at[idx, 'حالة القيد'] = new_status
                st.success("تم التحديث")
                st.rerun()

    # --- التبويب الرابع: سحب الرواتب ---
    with tab3:
        st.subheader("💰 استخراج مسير الرواتب النهائي")
        pay_df = st.session_state.master_data.copy()
        if selected_co != "الكل":
            pay_df = pay_df[pay_df['الشركة'] == selected_co]
            
        # الحسابات بناءً على أعمدة ملفك
        pay_df['إجمالي المستحق'] = (
            pay_df['الراتب الأساسي '] + 
            pay_df['بدل السكن'] + 
            pay_df[' بدل مواصلات'] + 
            pay_df['بدل اعاشة '] + 
            pay_df['علاوة '] + 
            pay_df['مكافآت شهرية'] - 
            pay_df['حسومات شهرية']
        )
        
        st.dataframe(pay_df[['الرقم الوظيفي امنكو', 'اسم الموظف', 'الشركة', 'المشروع', 'البنك', 'إجمالي المستحق']], use_container_width=True)
        
        csv = pay_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(f"📥 تحميل مسير {selected_co} (Excel)", csv, f"Payroll_{selected_co}_{datetime.now().strftime('%Y-%m')}.csv", "text/csv")

else:
    st.info("💡 بانتظار رفع ملف الماستر داتا لبدء العمل...")
