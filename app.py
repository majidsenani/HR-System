import streamlit as st
import pandas as pd
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام الموارد البشرية", layout="wide")

# تنسيق يدعم العربية
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    [data-testid="stSidebarNav"] { text-align: right; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("📂 نظام إدارة الموارد البشرية - ماجد")

if 'master_data' not in st.session_state:
    st.session_state.master_data = None

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    uploaded_file = st.file_uploader("ارفع ملف الماستر داتا", type=['xlsx'])
    
    if st.button("تحديث قاعدة البيانات"):
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                
                # تنظيف أسماء الأعمدة من المسافات الزائدة
                df.columns = df.columns.str.strip()
                
                # التحقق من وجود الأعمدة الأساسية وتنبيهك لو نقص شيء
                required_cols = ['اسم الموظف', 'الشركة', 'الراتب الأساسي']
                missing = [c for c in required_cols if c not in df.columns]
                
                if missing:
                    st.error(f"⚠️ الملف ناقص أعمدة: {', '.join(missing)}")
                    st.info("تأكد من كتابة المسميات بالضبط: اسم الموظف، الشركة، الراتب الأساسي")
                else:
                    # إضافة أعمدة المؤثرات لو مو موجودة
                    for col in ['مكافآت', 'حسومات', 'أيام غياب', 'الحالة']:
                        if col not in df.columns:
                            df[col] = 0.0 if col != 'الحالة' else 'نشط'
                    
                    st.session_state.master_data = df
                    st.success("✅ تم تحميل البيانات بنجاح!")
            except Exception as e:
                st.error(f"خطأ في قراءة الملف: {e}")

# --- عرض التبويبات ---
if st.session_state.master_data is not None:
    
    # ميزة ذكية: التأكد من وجود عمود الشركة قبل محاولة عرضه
    available_companies = st.session_state.master_data['الشركة'].unique().tolist()
    selected_co = st.sidebar.selectbox("تصفية حسب الشركة:", ["الكل"] + available_companies)
    
    tab1, tab2, tab3 = st.tabs(["👥 قائمة الموظفين", "✍️ المؤثرات الشهرية", "💰 سحب الرواتب"])

    with tab1:
        st.subheader("بيانات الموظفين")
        view_df = st.session_state.master_data
        if selected_co != "الكل":
            view_df = view_df[view_df['الشركة'] == selected_co]
        st.dataframe(view_df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("إدخال المؤثرات")
        emp_filter = st.session_state.master_data
        if selected_co != "الكل":
            emp_filter = emp_filter[emp_filter['الشركة'] == selected_co]
            
        with st.form("effect_form", clear_on_submit=True):
            target_emp = st.selectbox("اسم الموظف:", emp_filter['اسم الموظف'].unique())
            effect_type = st.selectbox("نوع المؤثر:", ["مكافأة", "حسم", "غياب"])
            value = st.number_input("القيمة:", min_value=0.0)
            if st.form_submit_button("حفظ"):
                idx = st.session_state.master_data.index[st.session_state.master_data['اسم الموظف'] == target_emp].tolist()[0]
                col_name = "مكافآت" if effect_type == "مكافأة" else ("حسومات" if effect_type == "حسم" else "أيام غياب")
                st.session_state.master_data.at[idx, col_name] = value
                st.success(f"تم تسجيل {effect_type} لـ {target_emp}")
                st.rerun()

    with tab3:
        st.subheader("سحب المسير")
        payroll_df = st.session_state.master_data.copy()
        if selected_co != "الكل":
            payroll_df = payroll_df[payroll_df['الشركة'] == selected_co]
        
        payroll_df['صافي المستحق'] = payroll_df['الراتب الأساسي'] + payroll_df['مكافآت'] - payroll_df['حسومات']
        st.dataframe(payroll_df, use_container_width=True, hide_index=True)
        
        csv = payroll_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(f"📥 سحب مسير {selected_co}", csv, f"Payroll_{selected_co}.csv", "text/csv")
else:
    st.info("يرجى رفع ملف الماستر داتا للبدء.")
