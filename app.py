import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="نظام رواتب ماجد الاحترافي", layout="wide")

st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    [data-testid="stSidebarNav"] { text-align: right; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; gap: 15px; }
    .group-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-right: 5px solid #007bff; margin-bottom: 20px; }
    .stForm { background-color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📂 نظام إدارة الموارد البشرية والرواتب")

if 'master_data' not in st.session_state:
    st.session_state.master_data = None

# --- 2. رفع ومعالجة البيانات ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    uploaded_file = st.file_uploader("ارفع ملف الماستر داتا (Excel/CSV)", type=['xlsx', 'csv'])
    
    if st.button("تحديث قاعدة البيانات 🔄"):
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
                # تنظيف أسماء الأعمدة تماماً
                df.columns = df.columns.str.strip()
                
                # إضافة أعمدة المؤثرات إذا لم تكن موجودة
                for col in ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب', 'حالة القيد']:
                    if col not in df.columns:
                        df[col] = 0.0 if col != 'حالة القيد' else 'نشط'
                
                st.session_state.master_data = df
                st.success("✅ تم تحديث البيانات بنجاح")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الرفع: {e}")

    if st.session_state.master_data is not None:
        st.divider()
        # فلتر الشركة في اليسار (يتحكم بكل التبويبات)
        companies = ["الكل"] + st.session_state.master_data['الشركة'].unique().tolist()
        sel_company = st.selectbox("🎯 اختر الشركة للعرض:", companies)

# --- 3. تشغيل النظام بعد الرفع ---
if st.session_state.master_data is not None:
    # تطبيق الفلتر العام
    main_df = st.session_state.master_data
    if sel_company != "الكل":
        df_display = main_df[main_df['الشركة'] == sel_company]
    else:
        df_display = main_df

    tab1, tab2, tab3, tab4 = st.tabs(["👥 قائمة الموظفين", "📅 المؤثرات والغياب", "⚙️ تعديل بيانات موظف", "💰 المسير النهائي"])

    # --- التبويب 1: القائمة والبحث ---
    with tab1:
        st.subheader("🔍 البحث السريع")
        search_query = st.text_input("ابحث بالرقم الوظيفي أو رقم الهوية:")
        
        filtered_view = df_display
        if search_query:
            # البحث في الهوية أو الرقم الوظيفي (تحويلهم لنصوص للبحث الجزئي)
            filtered_view = df_display[
                (df_display['رقم الهوية الوطنية'].astype(str).str.contains(search_query)) | 
                (df_display['الرقم الوظيفي امنكو'].astype(str).str.contains(search_query))
            ]
        
        # عرض البيانات بدون أعمدة المؤثرات في هذا التبويب
        cols_to_hide = ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب']
        st.dataframe(filtered_view.drop(columns=[c for c in cols_to_hide if c in filtered_view.columns]), use_container_width=True, hide_index=True)

    # --- التبويب 2: المؤثرات والغياب ---
    with tab2:
        st.subheader("📝 إدخال المؤثرات الشهرية")
        emp_id_input = st.text_input("ادخل الرقم الوظيفي للموظف (أمنكو):", key="id_eff")
        
        # البحث عن الموظف
        target_emp = df_display[df_display['الرقم الوظيفي امنكو'].astype(str) == emp_id_input]
        
        if not target_emp.empty:
            st.info(f"الموظف المختار: **{target_emp.iloc[0]['اسم الموظف']}** | المشروع: {target_emp.iloc[0]['المشروع']}")
            with st.form("effect_entry_form"):
                type_action = st.radio("نوع العملية:", ["مكافأة", "حسم", "غياب (تقويم)"], horizontal=True)
                
                if type_action == "غياب (تقويم)":
                    c1, c2 = st.columns(2)
                    with c1: d_from = st.date_input("من تاريخ:")
                    with c2: d_to = st.date_input("إلى تاريخ:")
                    val_calc = float((d_to - d_from).days + 1)
                    st.warning(f"إجمالي الأيام: {max(0, val_calc)}")
                    final_val = max(0, val_calc)
                else:
                    final_val = st.number_input("المبلغ (ريال):", min_value=0.0)
                
                if st.form_submit_button("اعتماد وحفظ"):
                    idx = target_emp.index[0]
                    col_map = {'مكافأة': 'مكافآت شهرية', 'حسم': 'حسومات شهرية', 'غياب (تقويم)': 'أيام غياب'}
                    st.session_state.master_data.at[idx, col_map[type_action]] = final_val
                    st.success("✅ تم الحفظ بنجاح")
                    st.rerun()

    # --- التبويب 3: تعديل البيانات المنظم ---
    with tab3:
        st.subheader("⚙️ تعديل ملف الموظف")
        emp_to_edit = st.selectbox("اختر الموظف للتعديل:", df_display['اسم الموظف'].unique())
        
        if emp_to_edit:
            idx = main_df[main_df['اسم الموظف'] == emp_to_edit].index[0]
            row = main_df.loc[idx]
            
            with st.form("structured_edit_form"):
                # 1. المجموعة المالية (البدلات تحت بعض)
                st.markdown("### 💰 الرواتب والبدلات")
                col_fin1, col_fin2 = st.columns(2)
                with col_fin1:
                    new_basic = st.number_input("الراتب الأساسي", value=float(row.get('الراتب الأساسي', 0)))
                    new_housing = st.number_input("بدل السكن", value=float(row.get('بدل السكن', 0)))
                    new_trans = st.number_input("بدل مواصلات", value=float(row.get('بدل مواصلات', 0)))
                with col_fin2:
                    new_food = st.number_input("بدل اعاشة", value=float(row.get('بدل اعاشة', 0)))
                    new_extra = st.number_input("علاوة", value=float(row.get('علاوة', 0)))
                    new_total = st.number_input("إجمالي الراتب (المثبت)", value=float(row.get('إجمالي الراتب', 0)))

                # 2. المجموعة الوظيفية
                st.markdown("---")
                st.markdown("### 📝 البيانات الوظيفية")
                col_job1, col_job2 = st.columns(2)
                with col_job1:
                    new_proj = st.text_input("المشروع", value=str(row.get('المشروع', '')))
                    new_branch = st.text_input("الفرع", value=str(row.get('الفرع', '')))
                    new_dept = st.text_input("القسم", value=str(row.get('القسم', '')))
                with col_job2:
                    new_title = st.text_input("المسمي الوظيفي", value=str(row.get('المسمي الوظيفي', '')))
                    new_start = st.text_input("تاريخ البداية", value=str(row.get('تاريخ  البداية', '')))
                    new_status = st.radio("حالة القيد", ["نشط", "موقوف"], index=0 if row['حالة القيد'] == 'نشط' else 1)

                # 3. المجموعة الشخصية والبنكية
                st.markdown("---")
                st.markdown("### 🏦 البيانات الشخصية والبنكية")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    new_nat_id = st.text_input("رقم الهوية الوطنية", value=str(row.get('رقم الهوية الوطنية', '')))
                    new_nation = st.text_input("الجنسية", value=str(row.get('الجنسية', '')))
                with col_p2:
                    new_bank = st.text_input("البنك", value=str(row.get('البنك', '')))
                    new_iban = st.text_input("الايبان", value=str(row.get('الايبان', '')))

                if st.form_submit_button("حفظ كافة التغييرات ✅"):
                    # تحديث البيانات في الجدول الرئيسي
                    updates = {
                        'الراتب الأساسي': new_basic, 'بدل السكن': new_housing, 'بدل مواصلات': new_trans,
                        'بدل اعاشة': new_food, 'علاوة': new_extra, 'إجمالي الراتب': new_total,
                        'المشروع': new_proj, 'الفرع': new_branch, 'القسم': new_dept,
                        'المسمي الوظيفي': new_title, 'تاريخ  البداية': new_start, 'حالة القيد': new_status,
                        'رقم الهوية الوطنية': new_nat_id, 'الجنسية': new_nation, 'البنك': new_bank, 'الايبان': new_iban
                    }
                    for k, v in updates.items():
                        st.session_state.master_data.at[idx, k] = v
                    st.success("تم التحديث!")
                    st.rerun()

    # --- التبويب 4: المسير النهائي ---
    with tab4:
        st.subheader("💰 كشف الرواتب الصافي")
        payroll_df = df_display.copy()
        
        # معادلة الصافي: (الأساسي + سكن + مواصلات + اعاشة + علاوة + مكافآت) - (حسومات)
        # نستخدم .get لضمان عدم حدوث خطأ لو نقص عمود
        payroll_df['الصافي المستحق'] = (
            payroll_df.get('الراتب الأساسي', 0) + 
            payroll_df.get('بدل السكن', 0) + 
            payroll_df.get('بدل مواصلات', 0) + 
            payroll_df.get('بدل اعاشة', 0) + 
            payroll_df.get('علاوة', 0) + 
            payroll_df['مكافآت شهرية'] - 
            payroll_df['حسومات شهرية']
        )
        
        st.dataframe(payroll_df, use_container_width=True, hide_index=True)
        st.download_button("📥 تحميل المسير (Excel)", payroll_df.to_csv(index=False).encode('utf-8-sig'), "Monthly_Payroll.csv")

else:
    st.info("👋 مرحباً بك! يرجى رفع ملف الماستر داتا من القائمة الجانبية للبدء.")
