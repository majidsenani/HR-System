import streamlit as st
import pandas as pd
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="HR System", layout="wide")

st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    [data-testid="stSidebarNav"] { text-align: right; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; gap: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📂 نظام إدارة الموارد البشرية")

if 'master_data' not in st.session_state:
    st.session_state.master_data = None

# دالة ذكية للبحث عن الأعمدة لتجنب أخطاء المسميات والمسافات
def get_col(df, keywords):
    for col in df.columns:
        if any(key in col for key in keywords):
            return col
    return None

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    uploaded_file = st.file_uploader("ارفع ملف الماستر داتا", type=['xlsx', 'csv'])
    
    if st.button("تحديث البيانات"):
        if uploaded_file:
            df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
            # تنظيف مسميات الأعمدة من المسافات الزائدة في البداية والنهاية
            df.columns = df.columns.str.strip()
            
            # التأكد من وجود أعمدة المؤثرات
            for c in ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب', 'حالة القيد']:
                if c not in df.columns: df[c] = 0.0 if c != 'حالة القيد' else 'نشط'
            
            st.session_state.master_data = df
            st.success("تم تحديث البيانات بنجاح")

if st.session_state.master_data is not None:
    df = st.session_state.master_data
    
    # تحديد أسماء الأعمدة الفعلية من ملفك لتجنب الـ KeyError
    col_id = get_col(df, ['الرقم الوظيفي', 'الوظيفي'])
    col_name = get_col(df, ['اسم الموظف', 'الاسم'])
    col_salary = get_col(df, ['الراتب الأساسي', 'الأساسي'])
    col_company = get_col(df, ['الشركة'])
    col_project = get_col(df, ['المشروع'])
    col_start = get_col(df, ['تاريخ', 'البداية'])
    col_iban = get_col(df, ['الايبان', 'IBAN'])

    tab1, tab2, tab3, tab4 = st.tabs(["👥 قائمة الموظفين", "✍️ المؤثرات الشهرية", "⚙️ تعديل البيانات", "💰 المسير النهائي"])

    with tab1:
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("رصد المؤثرات")
        search_id = st.text_input("ادخل الرقم الوظيفي:")
        target = df[df[col_id].astype(str) == search_id] if col_id else pd.DataFrame()
        
        if not target.empty:
            st.write(f"الموظف: {target.iloc[0][col_name]}")
            with st.form("eff_form"):
                t_eff = st.selectbox("النوع:", ["مكافأة", "حسم", "غياب"])
                val = st.number_input("القيمة:")
                if st.form_submit_button("حفظ"):
                    idx = target.index[0]
                    c_name = 'مكافآت شهرية' if t_eff == "مكافأة" else ('حسومات شهرية' if t_eff == "حسم" else 'أيام غياب')
                    st.session_state.master_data.at[idx, c_name] = val
                    st.success("تم الحفظ")
                    st.rerun()

    with tab3:
        st.subheader("تعديل البيانات الأساسية")
        edit_emp = st.selectbox("اختر الموظف:", df[col_name].unique()) if col_name else []
        if edit_emp:
            row = df[df[col_name] == edit_emp].iloc[0]
            with st.form("edit_form"):
                new_sal = st.number_input("الراتب الأساسي:", value=float(row[col_salary])) if col_salary else 0
                new_proj = st.text_input("المشروع:", value=str(row[col_project])) if col_project else ""
                if st.form_submit_button("تحديث"):
                    idx = df[df[col_name] == edit_emp].index[0]
                    if col_salary: st.session_state.master_data.at[idx, col_salary] = new_sal
                    if col_project: st.session_state.master_data.at[idx, col_project] = new_proj
                    st.success("تم التعديل")
                    st.rerun()

    with tab4:
        st.subheader("المسير النهائي")
        res = df.copy()
        # حساب الصافي (تأكد من مسميات البدلات في ملفك)
        res['صافي المستحق'] = res[col_salary] + res['مكافآت شهرية'] - res['حسومات شهرية']
        st.dataframe(res[[col_id, col_name, col_salary, 'صافي المستحق']], use_container_width=True)
        st.download_button("تحميل المسير CSV", res.to_csv(index=False).encode('utf-8-sig'), "payroll.csv")

else:
    st.info("يرجى رفع ملف الماستر داتا")
