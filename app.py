import streamlit as st
import pandas as pd
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام إدارة الموارد البشرية", layout="wide")

# تنسيق يدعم العربية والترتيب الجمالي
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    [data-testid="stSidebarNav"] { text-align: right; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; gap: 10px; }
    .stForm { background-color: #f8f9fb; padding: 25px; border-radius: 15px; border: 1px solid #e6e9ef; }
    .header-style { color: #1c3d5a; border-bottom: 2px solid #007bff; padding-bottom: 5px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📂 نظام إدارة الموارد البشرية المطور")

if 'master_data' not in st.session_state:
    st.session_state.master_data = None

# دالة ذكية للبحث عن الأعمدة
def get_col(df, keyword):
    for col in df.columns:
        if keyword.strip().lower() in col.strip().lower(): return col
    return None

# --- القائمة الجانبية (الفلاتر والرفع) ---
with st.sidebar:
    st.header("⚙️ التحكم بالنظام")
    uploaded_file = st.file_uploader("ارفع ملف الماستر داتا", type=['xlsx', 'csv'])
    
    if st.button("تحديث البيانات الأساسية"):
        if uploaded_file:
            df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
            df.columns = df.columns.str.strip()
            # إضافة أعمدة المؤثرات في الذاكرة فقط (لا تظهر في التعديل)
            for c in ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب', 'حالة القيد']:
                if c not in df.columns: df[c] = 0.0 if c != 'حالة القيد' else 'نشط'
            st.session_state.master_data = df
            st.success("✅ تم التحميل")

    if st.session_state.master_data is not None:
        st.divider()
        c_co = get_col(st.session_state.master_data, 'الشركة')
        all_cos = ["الكل"] + st.session_state.master_data[c_co].unique().tolist()
        selected_co = st.selectbox("🎯 اختر الشركة:", all_cos)

if st.session_state.master_data is not None:
    df = st.session_state.master_data
    # تصفية البيانات حسب الشركة المختارة من اليسار
    if selected_co != "الكل":
        df_filtered = df[df[get_col(df, 'الشركة')] == selected_co]
    else:
        df_filtered = df

    tab1, tab2, tab3, tab4 = st.tabs(["👥 قائمة الموظفين", "📅 المؤثرات والغياب", "⚙️ تعديل بيانات موظف", "💰 المسير النهائي"])

    # --- التبويب الأول: القائمة مع البحث بالرقم الوظيفي ---
    with tab1:
        st.subheader("📋 سجل الموظفين")
        c_id = get_col(df, 'الرقم الوظيفي امنكو')
        search_id = st.text_input("🔍 ابحث بالرقم الوظيفي (أمنكو):", key="search_main")
        
        display_df = df_filtered
        if search_id:
            display_df = display_df[display_df[c_id].astype(str).str.contains(search_id)]
        
        # إخفاء أعمدة المؤثرات من هذا الجدول
        cols_to_show = [c for c in display_df.columns if c not in ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب']]
        st.dataframe(display_df[cols_to_show], use_container_width=True, hide_index=True)

    # --- التبويب الثاني: المؤثرات مع التقويم ---
    with tab2:
        st.subheader("📝 إدخال المؤثرات الشهرية")
        search_id_eff = st.text_input("🔍 ادخل الرقم الوظيفي لرصد مؤثرات الموظف:", key="search_eff")
        target = df_filtered[df_filtered[c_id].astype(str) == search_id_eff] if c_id else pd.DataFrame()
        
        if not target.empty:
            st.info(f"الموظف: {target.iloc[0][get_col(df, 'اسم الموظف')]}")
            with st.form("eff_form"):
                type_eff = st.selectbox("نوع الإجراء:", ["مكافأة", "حسم", "غياب (تحديد تاريخ)"])
                
                if type_eff == "غياب (تحديد تاريخ)":
                    col1, col2 = st.columns(2)
                    with col1: d1 = st.date_input("من تاريخ:", datetime.now())
                    with col2: d2 = st.date_input("إلى تاريخ:", datetime.now())
                    days = (d2 - d1).days + 1
                    st.warning(f"عدد الأيام: {max(0, days)}")
                    val = float(max(0, days))
                else:
                    val = st.number_input("القيمة بالريال:", min_value=0.0)
                
                if st.form_submit_button("حفظ المؤثر"):
                    idx = target.index[0]
                    col_target = 'مكافآت شهرية' if type_eff == "مكافأة" else ('حسومات شهرية' if type_eff == "حسم" else 'أيام غياب')
                    st.session_state.master_data.at[idx, col_target] = val
                    st.success("✅ تم الحفظ")
                    st.rerun()

    # --- التبويب الثالث: تعديل منظم جداً ---
    with tab3:
        st.subheader("⚙️ تعديل الملف الشخصي للموظف")
        c_name = get_col(df, 'اسم الموظف')
        emp_choice = st.selectbox("اختر الموظف:", df_filtered[c_name].unique())
        
        if emp_choice:
            idx = df[df[c_name] == emp_choice].index[0]
            curr = df.loc[idx]
            
            with st.form("structured_edit"):
                # المجموعة الأولى: الرواتب والبدلات
                st.markdown("<h3 class='header-style'>💰 الرواتب والبدلات</h3>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                with c1: n_basic = st.number_input("الراتب الأساسي", value=float(curr[get_col(df, 'الراتب الأساسي')]))
                with c2: n_house = st.number_input("بدل السكن", value=float(curr[get_col(df, 'بدل السكن')]))
                with c3: n_trans = st.number_input("بدل مواصلات", value=float(curr[get_col(df, 'مواصلات')]))
                with c4: n_total = st.number_input("إجمالي الراتب (المثبت)", value=float(curr[get_col(df, 'إجمالي الراتب')]))

                # المجموعة الثانية: البيانات الوظيفية والبنكية
                st.markdown("<h3 class='header-style'>📝 البيانات الوظيفية والبنكية</h3>", unsafe_allow_html=True)
                ca, cb, cc = st.columns(3)
                with ca: 
                    n_proj = st.text_input("المشروع", value=str(curr[get_col(df, 'المشروع')]))
                    n_job = st.text_input("المسمى الوظيفي", value=str(curr[get_col(df, 'المسمي الوظيفي')]))
                with cb:
                    n_bank = st.text_input("البنك", value=str(curr[get_col(df, 'البنك')]))
                    n_iban = st.text_input("الايبان", value=str(curr[get_col(df, 'الايبان')]))
                with cc:
                    n_id_nat = st.text_input("الهوية الوطنية", value=str(curr[get_col(df, 'رقم الهوية الوطنية')]))
                    n_status = st.radio("حالة القيد", ["نشط", "موقوف"], index=0 if curr['حالة القيد'] == 'نشط' else 1)

                if st.form_submit_button("حفظ التعديلات النهائية"):
                    # تحديث القيم في الذاكرة
                    updates = {
                        get_col(df, 'الراتب الأساسي'): n_basic, get_col(df, 'بدل السكن'): n_house,
                        get_col(df, 'مواصلات'): n_trans, get_col(df, 'إجمالي الراتب'): n_total,
                        get_col(df, 'المشروع'): n_proj, get_col(df, 'المسمي الوظيفي'): n_job,
                        get_col(df, 'البنك'): n_bank, get_col(df, 'الايبان'): n_iban,
                        get_col(df, 'رقم الهوية الوطنية'): n_id_nat, 'حالة القيد': n_status
                    }
                    for k, v in updates.items(): st.session_state.master_data.at[idx, k] = v
                    st.success("✅ تم تحديث بيانات الموظف")
                    st.rerun()

    # --- التبويب الرابع: المسير النهائي ---
    with tab4:
        st.subheader("💰 كشف المسير الشهري (شامل المؤثرات)")
        final_df = df_filtered.copy()
        
        # حساب الصافي النهائي
        c_bs = get_col(final_df, 'الراتب الأساسي')
        c_hs = get_col(final_df, 'بدل السكن')
        final_df['صافي المستحق النهائي'] = (final_df[c_bs] + final_df[c_hs] + 
                                           final_df['مكافآت شهرية'] - final_df['حسومات شهرية'])
        
        st.dataframe(final_df, use_container_width=True, hide_index=True)
        st.download_button("📥 تحميل المسير (Excel)", final_df.to_csv(index=False).encode('utf-8-sig'), "Payroll_Final.csv")

else:
    st.info("💡 يرجى رفع ملف الماستر داتا من القائمة الجانبية.")
