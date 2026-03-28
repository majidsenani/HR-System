import streamlit as st
import pandas as pd
from datetime import datetime

# --- إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="HR System", layout="wide")

# كود لتنسيق الواجهة لتدعم اللغة العربية
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    div[data-testid="stSidebarNav"] { text-align: right; direction: rtl; }
    label { text-align: right; display: block; width: 100%; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 نظام إدارة الموارد البشرية والرواتب - ماجد")
st.write(f"تاريخ اليوم: {datetime.now().strftime('%Y-%m-%d')}")
st.divider()

# --- إدارة البيانات في ذاكرة الموقع ---
if 'hr_data' not in st.session_state:
    st.session_state.hr_data = None

# --- القائمة الجانبية: رفع الملفات ---
with st.sidebar:
    st.header("📂 رفع بيانات الشهر")
    file_a = st.file_uploader("ارفع إكسل الشركة الأولى", type=['xlsx'])
    file_b = st.file_uploader("ارفع إكسل الشركة الثانية", type=['xlsx'])
    
    if st.button("دمج ومعالجة البيانات"):
        if file_a and file_b:
            df1 = pd.read_excel(file_a)
            df2 = pd.read_excel(file_b)
            
            df1['الشركة'] = 'الشركة الأولى'
            df2['الشركة'] = 'الشركة الثانية'
            
            combined = pd.concat([df1, df2], ignore_index=True)
            
            # التأكد من وجود أعمدة المتغيرات الأساسية
            for col in ['مكافآت', 'حسومات', 'غياب (أيام)', 'الحالة']:
                if col not in combined.columns:
                    combined[col] = 0.0 if col != 'الحالة' else 'نشط'
            
            st.session_state.hr_data = combined
            st.success("تم التحديث!")

# --- عرض وإدارة النظام ---
if st.session_state.hr_data is not None:
    
    col_input, col_table = st.columns([1, 2])

    with col_input:
        st.subheader("📝 إضافة مكافأة أو حسم")
        with st.form("update_form", clear_on_submit=True):
            emp_list = st.session_state.hr_data['اسم الموظف'].unique()
            selected_emp = st.selectbox("اختر الموظف", emp_list)
            action = st.selectbox("نوع الإجراء", ["مكافأة", "حسم", "غياب", "تغيير الحالة"])
            val = st.number_input("المبلغ أو عدد الأيام", min_value=0.0)
            status = st.radio("حالة الموظف", ["نشط", "موقوف"], horizontal=True)
            
            if st.form_submit_button("حفظ"):
                idx = st.session_state.hr_data.index[st.session_state.hr_data['اسم الموظف'] == selected_emp].tolist()[0]
                if action == "مكافأة": st.session_state.hr_data.at[idx, 'مكافآت'] = val
                elif action == "حسم": st.session_state.hr_data.at[idx, 'حسومات'] = val
                elif action == "غياب": st.session_state.hr_data.at[idx, 'غياب (أيام)'] = val
                
                st.session_state.hr_data.at[idx, 'الحالة'] = status
                st.rerun()

    with col_table:
        st.subheader("📋 الجدول الموحد")
        
        # محرك بحث
        search = st.text_input("🔍 ابحث بالاسم...")
        display_df = st.session_state.hr_data
        if search:
            display_df = display_df[display_df['اسم الموظف'].str.contains(search, na=False)]

        st.dataframe(display_df, use_container_width=True)
        
        # زر التحميل النهائي
        csv = st.session_state.hr_data.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل التقرير النهائي Excel", data=csv, file_name='final_payroll.csv')

else:
    st.warning("يرجى رفع ملفات الإكسل من القائمة الجانبية للبدء.")
