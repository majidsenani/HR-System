import streamlit as st
import pandas as pd
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام مسيرات الرواتب", layout="wide")

# تنسيق الواجهة لتدعم العربية واليمين
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    div[data-testid="stSidebarNav"] { text-align: right; direction: rtl; }
    .stDataFrame { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("📑 نظام إدارة الرواتب والمسيرات الشهرية")

# --- إدارة قاعدة البيانات الثابتة ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = None

with st.sidebar:
    st.header("⚙️ الإعدادات")
    # رفع البيانات الأساسية (الماستر داتا)
    uploaded_master = st.file_uploader("ارفع ملف الماستر داتا (الشركتين)", type=['xlsx'])
    if st.button("تحديث قاعدة البيانات الثابتة"):
        if uploaded_master:
            df = pd.read_excel(uploaded_master)
            # التأكد من وجود الأعمدة الشهرية
            for col in ['مكافآت', 'حسومات', 'أيام غياب', 'صافي الراتب']:
                if col not in df.columns:
                    df[col] = 0.0
            st.session_state.master_data = df
            st.success("تم تحميل البيانات الثابتة")

# --- عرض النظام والعمليات ---
if st.session_state.master_data is not None:
    
    # 1. خيار تحديد الشركة
    companies = st.session_state.master_data['الشركة'].unique().tolist()
    selected_company = st.selectbox("🎯 اختر الشركة التي تريد العمل عليها:", ["الكل"] + companies)
    
    # تصفية البيانات بناءً على الشركة المختارة
    if selected_company == "الكل":
        df_filtered = st.session_state.master_data
    else:
        df_filtered = st.session_state.master_data[st.session_state.master_data['الشركة'] == selected_company]

    st.subheader(f"📊 كشف المؤثرات الشهرية - {selected_company}")
    st.info("يمكنك التعديل مباشرة على خانات المكافآت والحسومات في الجدول أدناه 👇")

    # 2. جدول تفاعلي للتعديل المباشر (Data Editor)
    # هذا الجدول يسمح لك بإدخال المؤثرات يدوياً لكل موظف
    edited_df = st.data_editor(
        df_filtered,
        column_config={
            "مكافآت": st.column_config.NumberColumn("المكافآت", format="%.2f"),
            "حسومات": st.column_config.NumberColumn("الحسومات", format="%.2f"),
            "أيام غياب": st.column_config.NumberColumn("الغياب", step=1),
            "الراتب الأساسي": st.column_config.NumberColumn(disabled=True),
            "اسم الموظف": st.column_config.TextColumn(disabled=True),
        },
        hide_index=True,
        use_container_width=True
    )

    # 3. حساب المسير النهائي
    if st.button("🔄 إنشاء المسير النهائي وحساب الرواتب"):
        # عملية حسابية بسيطة: أساسي + مكافأة - حسم
        edited_df['صافي الراتب'] = (
            edited_df['الراتب الأساسي'] + 
            edited_df['مكافآت'] - 
            edited_df['حسومات']
        )
        st.session_state.master_data.update(edited_df) # تحديث البيانات الأصلية
        st.success("تم حساب المسير بنجاح!")
        st.dataframe(edited_df[['اسم الموظف', 'الشركة', 'الراتب الأساسي', 'صافي الراتب']], use_container_width=True)

    # 4. سحب المسير (Download)
    final_csv = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label=f"📥 سحب مسير رواتب ({selected_company})",
        data=final_csv,
        file_name=f"Payroll_{selected_company}_{datetime.now().strftime('%Y-%m')}.csv",
        mime='text/csv'
    )

else:
    st.warning("الرجاء رفع ملف الماستر داتا من القائمة الجانبية (يحتوي على أعمدة: اسم الموظف، الشركة، الراتب الأساسي).")
