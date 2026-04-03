import streamlit as st
import pandas as pd
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="HR Management System", layout="wide")

st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    [data-testid="stSidebarNav"] { text-align: right; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; gap: 10px; }
    .stForm { background-color: #fcfcfc; padding: 20px; border-radius: 15px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("📂 نظام إدارة الموارد البشرية - الإصدار الشامل")

if 'master_data' not in st.session_state:
    st.session_state.master_data = None

# دالة ذكية لتنظيف الأسماء والبحث عنها
def get_col(df, keyword):
    for col in df.columns:
        if keyword.strip().lower() in col.strip().lower():
            return col
    return None

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("⚙️ إدارة البيانات")
    uploaded_file = st.file_uploader("ارفع ملف الماستر داتا (إكسل)", type=['xlsx', 'csv'])
    
    if st.button("تحديث قاعدة البيانات"):
        if uploaded_file:
            df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
            df.columns = df.columns.str.strip()
            # إضافة أعمدة المؤثرات
            for c in ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب', 'حالة القيد']:
                if c not in df.columns: df[c] = 0.0 if c != 'حالة القيد' else 'نشط'
            st.session_state.master_data = df
            st.success("✅ تم تحديث كافة البيانات")

if st.session_state.master_data is not None:
    df = st.session_state.master_data
    
    # تحديد الأعمدة الأساسية للبحث
    c_id = get_col(df, 'الرقم الوظيفي امنكو')
    c_name = get_col(df, 'اسم الموظف')

    tab1, tab2, tab3, tab4 = st.tabs(["👥 قائمة الموظفين", "📅 المؤثرات والغياب", "⚙️ تعديل الملف الكامل", "💰 المسير النهائي"])

    # --- التبويب الأول: العرض الشامل ---
    with tab1:
        st.subheader("سجل الموظفين الحالي")
        st.dataframe(df, use_container_width=True, hide_index=True)

    # --- التبويب الثاني: المؤثرات مع التقويم المثبت ---
    with tab2:
        st.subheader("📝 إدخال المؤثرات الشهرية")
        search_id = st.text_input("🔍 ابحث بالرقم الوظيفي (أمنكو):")
        target = df[df[c_id].astype(str) == search_id] if c_id else pd.DataFrame()
        
        if not target.empty:
            st.success(f"الموظف: {target.iloc[0][c_name]}")
            with st.form("absence_form"):
                type_eff = st.selectbox("نوع المؤثر:", ["مكافأة", "حسم", "غياب (تقويم)"])
                
                # هنا التعديل الجذري للغياب
                if type_eff == "غياب (تقويم)":
                    c_date1, c_date2 = st.columns(2)
                    with c_date1: d_start = st.date_input("تاريخ بداية الغياب:", datetime.now())
                    with c_date2: d_end = st.date_input("تاريخ نهاية الغياب:", datetime.now())
                    days_diff = (d_end - d_start).days + 1
                    st.info(f"إجمالي الأيام المحسوبة: {max(0, days_diff)}")
                    val_to_save = float(max(0, days_diff))
                else:
                    val_to_save = st.number_input("القيمة (ريال):", min_value=0.0)
                
                if st.form_submit_button("اعتماد وحفظ"):
                    idx = target.index[0]
                    col_name = 'مكافآت شهرية' if type_eff == "مكافأة" else ('حسومات شهرية' if type_eff == "حسم" else 'أيام غياب')
                    st.session_state.master_data.at[idx, col_name] = val_to_save
                    st.success("✅ تم الحفظ بنجاح")
                    st.rerun()

    # --- التبويب الثالث: تعديل كل شيء (بدون استثناء) ---
    with tab3:
        st.subheader("⚙️ تعديل كافة بيانات الموظف")
        emp_to_edit = st.selectbox("اختر الموظف للتعديل:", df[c_name].unique())
        
        if emp_to_edit:
            idx = df[df[c_name] == emp_to_edit].index[0]
            current_row = df.loc[idx]
            
            with st.form("universal_edit_form"):
                st.write(f"تعديل بيانات: {emp_to_edit}")
                # عرض جميع أعمدة الماستر داتا للتعديل
                new_values = {}
                cols = st.columns(3)
                for i, column in enumerate(df.columns):
                    # توزيع الأعمدة على 3 مسارات لتنظيم الشكل
                    with cols[i % 3]:
                        val = current_row[column]
                        if isinstance(val, (int, float)):
                            new_values[column] = st.number_input(f"{column}", value=float(val))
                        else:
                            new_values[column] = st.text_input(f"{column}", value=str(val))
                
                if st.form_submit_button("حفظ كافة التغييرات"):
                    for col, newVal in new_values.items():
                        st.session_state.master_data.at[idx, col] = newVal
                    st.success("✅ تم تحديث الملف بالكامل")
                    st.rerun()

    # --- التبويب الرابع: المسير النهائي ---
    with tab4:
        st.subheader("💰 كشف الرواتب النهائي")
        res = st.session_state.master_data.copy()
        
        # محاولة البحث عن الراتب والبدلات للحساب التلقائي
        c_basic = get_col(res, 'الراتب الأساسي')
        c_h = get_col(res, 'بدل السكن')
        c_t = get_col(res, 'مواصلات')
        c_f = get_col(res, 'اعاشة')
        
        if c_basic:
            res['صافي المستحق'] = (res[c_basic] + res.get(c_h, 0) + res.get(c_t, 0) + res.get(c_f, 0) + 
                                   res['مكافآت شهرية'] - res['حسومات شهرية'])
        
        st.dataframe(res, use_container_width=True, hide_index=True)
        st.download_button("📥 تحميل المسير النهائي (CSV)", res.to_csv(index=False).encode('utf-8-sig'), "Payroll_Final.csv")

else:
    st.info("👋 بانتظار رفع ملف الماستر داتا للبدء.")
