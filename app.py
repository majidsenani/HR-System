import streamlit as st
import pandas as pd
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام رواتب ماجد", layout="wide")

st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    [data-testid="stSidebarNav"] { text-align: right; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; gap: 10px; }
    .stForm { background-color: #fcfcfc; padding: 20px; border-radius: 15px; border: 1px solid #eee; }
    div[data-testid="stMetric"] { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📂 نظام إدارة الموارد البشرية - الإصدار الشامل")

if 'master_data' not in st.session_state:
    st.session_state.master_data = None

# --- القائمة الجانبية (الرفع والفلترة) ---
with st.sidebar:
    st.header("⚙️ التحكم")
    uploaded_file = st.file_uploader("ارفع ملف الماستر داتا", type=['xlsx', 'csv'])
    if st.button("تحديث قاعدة البيانات"):
        if uploaded_file:
            df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
            # إضافة أعمدة المؤثرات إذا نقصت
            for c in ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب', 'حالة القيد']:
                if c not in df.columns: df[c] = 0.0 if c != 'حالة القيد' else 'نشط'
            st.session_state.master_data = df
            st.success("✅ تم التحديث")

    if st.session_state.master_data is not None:
        st.divider()
        # فلتر الشركة موجود دائماً في اليسار
        all_cos = ["الكل"] + st.session_state.master_data['الشركة'].unique().tolist()
        sel_co = st.selectbox("🎯 تصفية حسب الشركة:", all_cos)

if st.session_state.master_data is not None:
    # تطبيق فلتر الشركة على كل النظام
    full_df = st.session_state.master_data
    if sel_co != "الكل":
        df = full_df[full_df['الشركة'] == sel_co]
    else:
        df = full_df

    tab1, tab2, tab3, tab4 = st.tabs(["👥 قائمة الموظفين", "📅 المؤثرات والغياب", "⚙️ تعديل الملف الكامل", "💰 المسير النهائي"])

    # --- التبويب الأول: البحث والقائمة ---
    with tab1:
        st.subheader("🔍 البحث السريع عن موظف")
        search_val = st.text_input("ادخل (الرقم الوظيفي أمنكو) أو (رقم الهوية) للبحث:")
        
        # منطق البحث الذكي
        display_df = df
        if search_val:
            display_df = df[
                (df['الرقم الوظيفي امنكو'].astype(str).str.contains(search_val)) | 
                (df['رقم الهوية الوطنية '].astype(str).str.contains(search_val))
            ]
        
        # عرض البيانات الأساسية فقط في الجدول الرئيسي
        main_cols = ['رقم الهوية الوطنية ', 'الالرقم الوظيفي امنكو', 'اسم الموظف', 'الشركة', 'المشروع', 'إجمالي الراتب ']
        # التأكد من وجود الأعمدة قبل عرضها لتجنب الأخطاء
        actual_cols = [c for c in main_cols if c in display_df.columns]
        st.dataframe(display_df[actual_cols], use_container_width=True, hide_index=True)

    # --- التبويب الثاني: الغياب مع التقويم ---
    with tab2:
        st.subheader("📝 إدخال المؤثرات")
        id_eff = st.text_input("ادخل الرقم الوظيفي للموظف المطلوب:")
        target = df[df['الرقم الوظيفي امنكو'].astype(str) == id_eff]
        
        if not target.empty:
            st.info(f"الموظف: {target.iloc[0]['اسم الموظف']}")
            with st.form("eff_form"):
                eff_type = st.selectbox("نوع المؤثر:", ["مكافأة", "حسم", "غياب (تقويم)"])
                
                if eff_type == "غياب (تقويم)":
                    c1, c2 = st.columns(2)
                    with c1: d1 = st.date_input("من تاريخ:")
                    with c2: d2 = st.date_input("إلى تاريخ:")
                    val = float((d2 - d1).days + 1)
                    st.warning(f"الأيام المحسوبة: {max(0, val)}")
                else:
                    val = st.number_input("القيمة بالريال:", min_value=0.0)
                
                if st.form_submit_button("حفظ"):
                    idx = target.index[0]
                    col = 'مكافآت شهرية' if eff_type == "مكافأة" else ('حسومات شهرية' if eff_type == "حسم" else 'أيام غياب')
                    st.session_state.master_data.at[idx, col] = val
                    st.success("تم الحفظ")
                    st.rerun()

    # --- التبويب الثالث: تعديل كل البيانات (بدون استثناء) ---
    with tab3:
        st.subheader("⚙️ تعديل ملف الموظف الكامل")
        # البحث بالاسم داخل التعديل
        emp_name = st.selectbox("اختر الموظف المراد تعديله:", df['اسم الموظف'].unique())
        idx = df[df['اسم الموظف'] == emp_name].index[0]
        row = df.loc[idx]
        
        with st.form("universal_edit"):
            st.write(f"تعديل كافة البيانات لـ: {emp_name}")
            new_data = {}
            # توزيع كل أعمدة الماستر داتا (15+ عمود) على 3 أعمدة للتنسيق
            cols = st.columns(3)
            for i, col in enumerate(df.columns):
                # استبعاد أعمدة الحسابات الشهرية من بيانات الموظف الثابتة
                if col not in ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب']:
                    with cols[i % 3]:
                        val = row[col]
                        if isinstance(val, (int, float)):
                            new_data[col] = st.number_input(f"{col}", value=float(val))
                        else:
                            new_data[col] = st.text_input(f"{col}", value=str(val))
            
            if st.form_submit_button("حفظ كافة التغييرات"):
                for k, v in new_data.items():
                    st.session_state.master_data.at[idx, k] = v
                st.success("✅ تم التحديث بنجاح")
                st.rerun()

    # --- التبويب الرابع: المسير ---
    with tab4:
        res = df.copy()
        res['صافي المستحق'] = res['إجمالي الراتب '] + res['مكافآت شهرية'] - res['حسومات شهرية']
        st.dataframe(res, use_container_width=True)
        st.download_button("📥 تحميل المسير", res.to_csv(index=False).encode('utf-8-sig'), "Payroll.csv")

else:
    st.info("💡 ارفع ملف الماستر داتا من القائمة الجانبية.")
