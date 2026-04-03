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
    .stForm { background-color: #f9f9f9; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 نظام إدارة الموارد البشرية المتكامل")

if 'master_data' not in st.session_state:
    st.session_state.master_data = None

# دالة ذكية للبحث عن الأعمدة
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
            df.columns = df.columns.str.strip()
            # إضافة أعمدة المؤثرات الافتراضية
            for c in ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب', 'حالة القيد']:
                if c not in df.columns: df[c] = 0.0 if c != 'حالة القيد' else 'نشط'
            st.session_state.master_data = df
            st.success("✅ تم تحديث البيانات")

if st.session_state.master_data is not None:
    df = st.session_state.master_data
    
    # تحديد الأعمدة من ملفك
    c_id = get_col(df, ['الرقم الوظيفي امنكو'])
    c_name = get_col(df, ['اسم الموظف'])
    c_salary = get_col(df, ['الراتب الأساسي'])
    c_housing = get_col(df, ['بدل السكن'])
    c_trans = get_col(df, ['مواصلات'])
    c_food = get_col(df, ['اعاشة'])
    c_extra = get_col(df, ['علاوة'])
    c_job = get_col(df, ['المسمي الوظيفي'])
    c_project = get_col(df, ['المشروع'])
    c_bank = get_col(df, ['البنك'])
    c_iban = get_col(df, ['الايبان'])
    c_nat_id = get_col(df, ['الهوية الوطنية'])

    tab1, tab2, tab3, tab4 = st.tabs(["👥 قائمة الموظفين", "✍️ المؤثرات الشهرية", "⚙️ تعديل كامل البيانات", "💰 المسير النهائي"])

    # --- التبويب الأول: العرض ---
    with tab1:
        st.dataframe(df, use_container_width=True, hide_index=True)

    # --- التبويب الثاني: المؤثرات (مع تقويم) ---
    with tab2:
        st.subheader("📝 رصد المؤثرات الشهرية")
        search_id = st.text_input("🔍 ادخل الرقم الوظيفي أمنكو:")
        target = df[df[c_id].astype(str) == search_id] if c_id else pd.DataFrame()
        
        if not target.empty:
            st.info(f"الموظف: {target.iloc[0][c_name]} | المشروع: {target.iloc[0][c_project]}")
            with st.form("eff_form"):
                type_eff = st.selectbox("نوع المؤثر:", ["مكافأة", "حسم", "غياب (بالتاريخ)"])
                
                if type_eff == "غياب (بالتاريخ)":
                    col_d1, col_d2 = st.columns(2)
                    with col_d1: d1 = st.date_input("من تاريخ:", datetime.now())
                    with col_d2: d2 = st.date_input("إلى تاريخ:", datetime.now())
                    calc_days = (d2 - d1).days + 1
                    st.warning(f"إجمالي الأيام المحسوبة: {max(0, calc_days)}")
                    final_val = float(max(0, calc_days))
                else:
                    final_val = st.number_input("القيمة بالريال:", min_value=0.0)
                
                if st.form_submit_button("حفظ المؤثر"):
                    idx = target.index[0]
                    col_target = 'مكافآت شهرية' if type_eff == "مكافأة" else ('حسومات شهرية' if type_eff == "حسم" else 'أيام غياب')
                    st.session_state.master_data.at[idx, col_target] = final_val
                    st.success("✅ تم الحفظ")
                    st.rerun()

    # --- التبويب الثالث: تعديل كل شيء ---
    with tab3:
        st.subheader("⚙️ تعديل ملف الموظف الكامل")
        edit_name = st.selectbox("اختر الموظف لتعديل بياناته:", df[c_name].unique())
        row = df[df[c_name] == edit_name].iloc[0]
        
        with st.form("full_edit_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("### البيانات المالية")
                new_sal = st.number_input("الراتب الأساسي:", value=float(row[c_salary]))
                new_house = st.number_input("بدل السكن:", value=float(row[c_housing]))
                new_trans = st.number_input("بدل مواصلات:", value=float(row[c_trans]))
                new_food = st.number_input("بدل إعاشة:", value=float(row[c_food]))
            with col2:
                st.markdown("### البيانات الوظيفية")
                new_proj = st.text_input("المشروع:", value=str(row[c_project]))
                new_job_title = st.text_input("المسمى الوظيفي:", value=str(row[c_job]))
                new_status = st.radio("حالة القيد:", ["نشط", "موقوف"], index=0 if row['حالة القيد']=='نشط' else 1)
            with col3:
                st.markdown("### البيانات الشخصية والبنكية")
                new_nat = st.text_input("الهوية الوطنية:", value=str(row[c_nat_id]))
                new_bnk = st.text_input("البنك:", value=str(row[c_bank]))
                new_ib = st.text_input("الآيبان:", value=str(row[c_iban]))
            
            if st.form_submit_button("تحديث وحفظ التغييرات"):
                idx = df[df[c_name] == edit_name].index[0]
                # تحديث القيم
                updates = {c_salary: new_sal, c_housing: new_house, c_trans: new_trans, c_food: new_food,
                           c_project: new_proj, c_job: new_job_title, 'حالة القيد': new_status,
                           c_nat_id: new_nat, c_bank: new_bnk, c_iban: new_ib}
                for k, v in updates.items(): st.session_state.master_data.at[idx, k] = v
                st.success("✅ تم تحديث بيانات الموظف بنجاح")
                st.rerun()

    # --- التبويب الرابع: المسير ---
    with tab4:
        res = df.copy()
        res['إجمالي البدلات'] = res[c_housing] + res[c_trans] + res[c_food] + res[c_extra]
        res['صافي الراتب'] = res[c_salary] + res['إجمالي البدلات'] + res['مكافآت شهرية'] - res['حسومات شهرية']
        st.dataframe(res[[c_id, c_name, c_project, 'صافي الراتب', 'حالة القيد']], use_container_width=True)
        st.download_button("📥 تحميل المسير النهائي", res.to_csv(index=False).encode('utf-8-sig'), "Payroll_Final.csv")

else:
    st.info("💡 يرجى رفع ملف الماستر داتا من القائمة الجانبية.")
