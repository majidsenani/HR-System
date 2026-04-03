import streamlit as st
import pandas as pd
import io
from datetime import datetime, date

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="نظام إدارة الموارد البشرية",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&display=swap');

*, body, .main { 
    font-family: 'Tajawal', sans-serif !important; 
    direction: rtl; 
    text-align: right;
}

:root {
    --primary: #1a2744;
    --accent: #c9a84c;
    --accent-light: #f0d98a;
    --surface: #f4f6fa;
    --card: #ffffff;
    --border: #e2e8f0;
    --success: #22c55e;
    --danger: #ef4444;
    --warning: #f59e0b;
    --text: #1e293b;
    --muted: #64748b;
}

.stApp { background: var(--surface); }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--primary) !important;
    border-left: 3px solid var(--accent);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stFileUploader label { color: var(--accent-light) !important; font-weight: 600; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--accent) !important; }

/* Header */
.app-header {
    background: linear-gradient(135deg, var(--primary) 0%, #2d4a8a 100%);
    color: white;
    padding: 28px 36px;
    border-radius: 16px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 32px rgba(26,39,68,0.18);
    border-bottom: 4px solid var(--accent);
}
.app-header h1 { margin: 0; font-size: 2rem; font-weight: 900; letter-spacing: -0.5px; }
.app-header .subtitle { color: var(--accent-light); font-size: 0.95rem; font-weight: 400; margin-top: 4px; }
.app-header .header-icon { font-size: 3rem; opacity: 0.85; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: var(--card);
    padding: 8px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    direction: rtl;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 10px 20px;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: var(--primary) !important;
    color: var(--accent) !important;
}

/* Cards */
.stat-card {
    background: var(--card);
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-top: 4px solid var(--accent);
    text-align: center;
    transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.stat-card .stat-number { font-size: 2.4rem; font-weight: 900; color: var(--primary); line-height: 1; }
.stat-card .stat-label { font-size: 0.85rem; color: var(--muted); margin-top: 6px; font-weight: 500; }

/* Sections */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 20px;
    background: linear-gradient(90deg, var(--primary) 0%, #2d4a8a 100%);
    color: white;
    border-radius: 10px;
    margin: 24px 0 16px 0;
    font-weight: 700;
    font-size: 1.05rem;
}

/* Info box */
.emp-info-box {
    background: linear-gradient(135deg, #e8f4fd 0%, #dbeafe 100%);
    border: 1.5px solid #93c5fd;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
    font-weight: 600;
    color: var(--primary);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--primary), #2d4a8a) !important;
    color: var(--accent-light) !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-family: 'Tajawal', sans-serif !important;
    font-size: 0.95rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 3px 10px rgba(26,39,68,0.2) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(26,39,68,0.3) !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #166534, #15803d) !important;
    color: #dcfce7 !important;
}

/* Form inputs */
.stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input {
    border-radius: 8px !important;
    border: 1.5px solid var(--border) !important;
    font-family: 'Tajawal', sans-serif !important;
    transition: border-color 0.2s !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.15) !important;
}

/* Table */
.stDataFrame { border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }

/* Badge */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
}
.badge-success { background: #dcfce7; color: #166534; }
.badge-danger { background: #fee2e2; color: #991b1b; }

/* Group box */
.group-card {
    background: var(--card);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border-right: 5px solid var(--accent);
}

/* Divider */
.section-divider {
    height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent);
    border: none;
    margin: 20px 0;
    border-radius: 2px;
}

/* Alert */
.stSuccess, .stInfo, .stWarning, .stError { border-radius: 10px !important; }

/* Note icon for remarks */
.note-box {
    background: #fffbeb;
    border: 1.5px solid #fcd34d;
    border-radius: 10px;
    padding: 12px 16px;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="app-header">
    <div>
        <h1>🏢 نظام إدارة الموارد البشرية والرواتب</h1>
        <div class="subtitle">منصة احترافية لإدارة الموظفين والرواتب والمؤثرات الشهرية</div>
    </div>
    <div class="header-icon">💼</div>
</div>
""", unsafe_allow_html=True)

# --- Session State ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = None
if 'effects_log' not in st.session_state:
    st.session_state.effects_log = []

# --- Sidebar ---
with st.sidebar:
    st.markdown("## ⚙️ إعدادات النظام")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📁 رفع ملف الماستر داتا", type=['xlsx', 'csv'],
                                      help="يدعم النظام ملفات Excel و CSV")
    
    if st.button("🔄 تحديث قاعدة البيانات", use_container_width=True):
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('xlsx'):
                    df = pd.read_excel(uploaded_file)
                else:
                    df = pd.read_csv(uploaded_file)
                
                df.columns = df.columns.str.strip()
                
                # إضافة أعمدة المؤثرات
                for col in ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب']:
                    if col not in df.columns:
                        df[col] = 0.0
                if 'حالة القيد' not in df.columns:
                    df['حالة القيد'] = 'نشط'
                if 'ملاحظات المؤثرات' not in df.columns:
                    df['ملاحظات المؤثرات'] = ''
                
                # معالجة تاريخ البداية - إزالة الأصفار
                date_cols = ['تاريخ  البداية', 'تاريخ البداية']
                for dc in date_cols:
                    if dc in df.columns:
                        df[dc] = pd.to_datetime(df[dc], errors='coerce')
                        df[dc] = df[dc].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else '')
                
                st.session_state.master_data = df
                st.success("✅ تم تحديث البيانات بنجاح!")
            except Exception as e:
                st.error(f"خطأ: {e}")
        else:
            st.warning("⚠️ الرجاء اختيار ملف أولاً")
    
    st.markdown("---")
    
    if st.session_state.master_data is not None:
        companies = ["الكل"] + sorted(st.session_state.master_data['الشركة'].unique().tolist())
        sel_company = st.selectbox("🏬 اختر الشركة:", companies)
        
        total = len(st.session_state.master_data)
        active = len(st.session_state.master_data[st.session_state.master_data['حالة القيد'] == 'نشط'])
        
        st.markdown(f"""
        <div style="background:rgba(201,168,76,0.15);border-radius:10px;padding:14px;margin-top:10px;">
            <div style="color:#f0d98a;font-weight:700;font-size:0.85rem;margin-bottom:8px;">📊 إحصاء سريع</div>
            <div style="color:white;font-size:0.9rem;">👥 إجمالي الموظفين: <b style="color:#f0d98a">{total}</b></div>
            <div style="color:white;font-size:0.9rem;margin-top:4px;">✅ الموظفون النشطون: <b style="color:#86efac">{active}</b></div>
            <div style="color:white;font-size:0.9rem;margin-top:4px;">⛔ الموقوفون: <b style="color:#fca5a5">{total - active}</b></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        sel_company = "الكل"

# --- Main Content ---
if st.session_state.master_data is not None:
    main_df = st.session_state.master_data
    
    if sel_company != "الكل":
        df_display = main_df[main_df['الشركة'] == sel_company].copy()
    else:
        df_display = main_df.copy()

    # --- Stats Row ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        total_sal = df_display.get('إجمالي الراتب', pd.Series([0])).sum()
        st.markdown(f"""<div class="stat-card">
            <div class="stat-number">{len(df_display)}</div>
            <div class="stat-label">👥 إجمالي الموظفين</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        active_count = len(df_display[df_display['حالة القيد'] == 'نشط']) if 'حالة القيد' in df_display.columns else 0
        st.markdown(f"""<div class="stat-card" style="border-top-color:#22c55e">
            <div class="stat-number" style="color:#166534">{active_count}</div>
            <div class="stat-label">✅ نشطون</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        total_bonuses = df_display['مكافآت شهرية'].sum() if 'مكافآت شهرية' in df_display.columns else 0
        st.markdown(f"""<div class="stat-card" style="border-top-color:#c9a84c">
            <div class="stat-number" style="color:#854d0e;font-size:1.6rem">{total_bonuses:,.0f}</div>
            <div class="stat-label">🎁 إجمالي المكافآت (ر.س)</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        total_deductions = df_display['حسومات شهرية'].sum() if 'حسومات شهرية' in df_display.columns else 0
        st.markdown(f"""<div class="stat-card" style="border-top-color:#ef4444">
            <div class="stat-number" style="color:#991b1b;font-size:1.6rem">{total_deductions:,.0f}</div>
            <div class="stat-label">🔻 إجمالي الحسومات (ر.س)</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥  قائمة الموظفين", "📋  المؤثرات الشهرية", "✏️  تعديل بيانات موظف", "💰  كشف الرواتب"])

    # ============================================================
    # التبويب 1: قائمة الموظفين
    # ============================================================
    with tab1:
        st.markdown('<div class="section-header">🔍 البحث والتصفية</div>', unsafe_allow_html=True)
        
        col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
        with col_s1:
            search_query = st.text_input("🔎 بحث بالرقم الوظيفي أو الهوية أو الاسم:", placeholder="أدخل كلمة البحث...")
        with col_s2:
            if 'المشروع' in df_display.columns:
                projects = ["الكل"] + sorted(df_display['المشروع'].dropna().unique().tolist())
                sel_project = st.selectbox("📍 المشروع:", projects)
            else:
                sel_project = "الكل"
        with col_s3:
            status_filter = st.selectbox("🔘 الحالة:", ["الكل", "نشط", "موقوف"])
        
        filtered_view = df_display.copy()
        
        if search_query:
            mask = pd.Series([False] * len(filtered_view), index=filtered_view.index)
            for col in ['الرقم الوظيفي امنكو', 'رقم الهوية الوطنية', 'اسم الموظف']:
                if col in filtered_view.columns:
                    mask |= filtered_view[col].astype(str).str.contains(search_query, case=False, na=False)
            filtered_view = filtered_view[mask]
        
        if sel_project != "الكل" and 'المشروع' in filtered_view.columns:
            filtered_view = filtered_view[filtered_view['المشروع'] == sel_project]
        
        if status_filter != "الكل" and 'حالة القيد' in filtered_view.columns:
            filtered_view = filtered_view[filtered_view['حالة القيد'] == status_filter]
        
        st.markdown(f"**عدد النتائج: {len(filtered_view)} موظف**")
        
        cols_to_hide = ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب', 'ملاحظات المؤثرات']
        show_cols = [c for c in filtered_view.columns if c not in cols_to_hide]
        st.dataframe(filtered_view[show_cols], use_container_width=True, hide_index=True, height=420)

    # ============================================================
    # التبويب 2: المؤثرات الشهرية
    # ============================================================
    with tab2:
        sub1, sub2 = st.tabs(["➕ إدخال مؤثر جديد", "📤 رفع مؤثرات Excel"])
        
        # --- الإدخال اليدوي ---
        with sub1:
            st.markdown('<div class="section-header">📝 إدخال مؤثر شهري للموظف</div>', unsafe_allow_html=True)
            
            emp_id_input = st.text_input("🔍 ادخل الرقم الوظيفي (أمنكو):", key="id_eff", placeholder="مثال: 12345")
            
            if emp_id_input:
                target_emp = df_display[df_display['الرقم الوظيفي امنكو'].astype(str).str.strip() == emp_id_input.strip()]
                
                if not target_emp.empty:
                    row_emp = target_emp.iloc[0]
                    st.markdown(f"""
                    <div class="emp-info-box">
                        <span>👤 <b>{row_emp.get('اسم الموظف', '')}</b></span>
                        &nbsp;|&nbsp; 
                        <span>📍 {row_emp.get('المشروع', '')}</span>
                        &nbsp;|&nbsp;
                        <span>🏢 {row_emp.get('الشركة', '')}</span>
                        &nbsp;|&nbsp;
                        <span>💼 {row_emp.get('المسمي الوظيفي', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # عرض المؤثرات الحالية
                    cur_bonus = float(main_df.at[target_emp.index[0], 'مكافآت شهرية'] or 0)
                    cur_deduct = float(main_df.at[target_emp.index[0], 'حسومات شهرية'] or 0)
                    cur_absence = float(main_df.at[target_emp.index[0], 'أيام غياب'] or 0)
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("🎁 المكافآت الحالية", f"{cur_bonus:,.0f} ر.س")
                    with m2:
                        st.metric("🔻 الحسومات الحالية", f"{cur_deduct:,.0f} ر.س")
                    with m3:
                        st.metric("📅 أيام الغياب", f"{cur_absence:.0f} يوم")
                    
                    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
                    
                    with st.form("effect_entry_form", clear_on_submit=True):
                        type_action = st.radio(
                            "🔧 نوع العملية:",
                            ["مكافأة ✨", "حسم 🔻", "غياب 📅"],
                            horizontal=True
                        )
                        
                        if type_action == "غياب 📅":
                            st.markdown('<div class="section-header" style="padding:10px 16px;font-size:0.9rem;margin:12px 0 10px">📅 تحديد فترة الغياب</div>', unsafe_allow_html=True)
                            col_d1, col_d2 = st.columns(2)
                            with col_d1:
                                d_from = st.date_input("📌 من تاريخ:", value=date.today(), key="abs_from")
                            with col_d2:
                                d_to = st.date_input("📌 إلى تاريخ:", value=date.today(), key="abs_to")
                            
                            if d_to >= d_from:
                                days_count = (d_to - d_from).days + 1
                                st.info(f"⏱️ إجمالي أيام الغياب: **{days_count} يوم** (من {d_from.strftime('%Y-%m-%d')} إلى {d_to.strftime('%Y-%m-%d')})")
                                final_val = float(days_count)
                            else:
                                st.error("⚠️ تاريخ النهاية يجب أن يكون بعد تاريخ البداية")
                                final_val = 0.0
                        else:
                            final_val = st.number_input("💵 المبلغ (ريال سعودي):", min_value=0.0, step=100.0, format="%.2f")
                        
                        # ملاحظات السبب
                        st.markdown('<div class="note-box">📝 <b>سبب العملية / ملاحظات</b></div>', unsafe_allow_html=True)
                        note_text = st.text_area(
                            "اكتب سبب المكافأة أو الحسم أو الغياب:",
                            placeholder="مثال: مكافأة أداء الربع الثاني / حسم تأخر متكرر / غياب بدون إذن...",
                            height=100,
                            key="note_field"
                        )
                        
                        submit_btn = st.form_submit_button("✅ اعتماد وحفظ المؤثر", use_container_width=True)
                        
                        if submit_btn:
                            idx = target_emp.index[0]
                            if type_action == "مكافأة ✨":
                                st.session_state.master_data.at[idx, 'مكافآت شهرية'] = final_val
                                col_used = 'مكافآت شهرية'
                            elif type_action == "حسم 🔻":
                                st.session_state.master_data.at[idx, 'حسومات شهرية'] = final_val
                                col_used = 'حسومات شهرية'
                            else:
                                st.session_state.master_data.at[idx, 'أيام غياب'] = final_val
                                col_used = 'أيام غياب'
                            
                            # حفظ الملاحظة
                            st.session_state.master_data.at[idx, 'ملاحظات المؤثرات'] = note_text
                            
                            # تسجيل في سجل المؤثرات
                            st.session_state.effects_log.append({
                                'التاريخ': datetime.now().strftime('%Y-%m-%d %H:%M'),
                                'الرقم الوظيفي': emp_id_input,
                                'اسم الموظف': row_emp.get('اسم الموظف', ''),
                                'نوع العملية': type_action.split()[0],
                                'القيمة': final_val,
                                'الملاحظات': note_text
                            })
                            
                            st.success(f"✅ تم حفظ المؤثر بنجاح! | {type_action.split()[0]}: {final_val:,.0f}")
                            st.rerun()
                else:
                    st.error("⚠️ لم يتم العثور على موظف بهذا الرقم الوظيفي في الشركة المحددة")
            
            # سجل المؤثرات
            if st.session_state.effects_log:
                st.markdown('<div class="section-header">📋 سجل المؤثرات لهذه الجلسة</div>', unsafe_allow_html=True)
                log_df = pd.DataFrame(st.session_state.effects_log)
                st.dataframe(log_df, use_container_width=True, hide_index=True)
        
        # --- رفع مؤثرات Excel ---
        with sub2:
            st.markdown('<div class="section-header">📤 رفع ملف المؤثرات من Excel</div>', unsafe_allow_html=True)
            
            st.info("""
            📌 **تعليمات ملف المؤثرات:**
            يجب أن يحتوي الملف على الأعمدة التالية:
            - `الرقم الوظيفي امنكو` - رقم الموظف
            - `مكافآت شهرية` - قيمة المكافأة (اختياري)
            - `حسومات شهرية` - قيمة الحسم (اختياري)
            - `أيام غياب` - عدد أيام الغياب (اختياري)
            - `ملاحظات المؤثرات` - سبب المؤثر (اختياري)
            """)
            
            # زر تحميل نموذج Excel
            template_data = {
                'الرقم الوظيفي امنكو': ['12345', '67890'],
                'مكافآت شهرية': [500, 0],
                'حسومات شهرية': [0, 200],
                'أيام غياب': [0, 2],
                'ملاحظات المؤثرات': ['مكافأة الأداء', 'تأخر متكرر']
            }
            template_df = pd.DataFrame(template_data)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                template_df.to_excel(writer, index=False, sheet_name='المؤثرات')
            
            st.download_button(
                "📥 تحميل نموذج المؤثرات (Excel)",
                data=buffer.getvalue(),
                file_name="نموذج_المؤثرات.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            effects_file = st.file_uploader("📁 ارفع ملف المؤثرات هنا:", type=['xlsx', 'csv'], key="effects_upload")
            
            if effects_file:
                try:
                    if effects_file.name.endswith('xlsx'):
                        eff_df = pd.read_excel(effects_file)
                    else:
                        eff_df = pd.read_csv(effects_file)
                    
                    eff_df.columns = eff_df.columns.str.strip()
                    st.markdown("**معاينة الملف المرفوع:**")
                    st.dataframe(eff_df, use_container_width=True, hide_index=True)
                    
                    if st.button("⚡ تطبيق المؤثرات على قاعدة البيانات", use_container_width=True):
                        updated = 0
                        not_found = []
                        
                        for _, eff_row in eff_df.iterrows():
                            emp_id = str(eff_row['الرقم الوظيفي امنكو']).strip()
                            mask = st.session_state.master_data['الرقم الوظيفي امنكو'].astype(str).str.strip() == emp_id
                            matches = st.session_state.master_data[mask]
                            
                            if not matches.empty:
                                idx = matches.index[0]
                                for col in ['مكافآت شهرية', 'حسومات شهرية', 'أيام غياب', 'ملاحظات المؤثرات']:
                                    if col in eff_df.columns and pd.notna(eff_row.get(col)):
                                        st.session_state.master_data.at[idx, col] = eff_row[col]
                                updated += 1
                            else:
                                not_found.append(emp_id)
                        
                        st.success(f"✅ تم تحديث {updated} موظف بنجاح!")
                        if not_found:
                            st.warning(f"⚠️ لم يتم العثور على الأرقام: {', '.join(not_found)}")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"خطأ في قراءة الملف: {e}")

    # ============================================================
    # التبويب 3: تعديل بيانات الموظف
    # ============================================================
    with tab3:
        st.markdown('<div class="section-header">✏️ تعديل ملف الموظف الكامل</div>', unsafe_allow_html=True)
        
        col_sel1, col_sel2 = st.columns([2, 1])
        with col_sel1:
            emp_to_edit = st.selectbox("👤 اختر الموظف:", df_display['اسم الموظف'].unique())
        with col_sel2:
            emp_id_filter = st.text_input("أو ابحث بالرقم الوظيفي:", key="edit_search")
        
        if emp_id_filter:
            matches = main_df[main_df['الرقم الوظيفي امنكو'].astype(str).str.strip() == emp_id_filter.strip()]
            if not matches.empty:
                emp_to_edit = matches.iloc[0]['اسم الموظف']
        
        if emp_to_edit:
            idx = main_df[main_df['اسم الموظف'] == emp_to_edit].index[0]
            row = main_df.loc[idx]
            
            with st.form("structured_edit_form"):
                # ===== المجموعة المالية =====
                st.markdown('<div class="section-header">💰 الرواتب والبدلات</div>', unsafe_allow_html=True)
                st.markdown('<div class="group-card">', unsafe_allow_html=True)
                cf1, cf2, cf3 = st.columns(3)
                with cf1:
                    new_basic = st.number_input("🏦 الراتب الأساسي", value=float(row.get('الراتب الأساسي', 0) or 0), step=100.0, format="%.2f")
                    new_housing = st.number_input("🏠 بدل السكن", value=float(row.get('بدل السكن', 0) or 0), step=100.0, format="%.2f")
                with cf2:
                    new_trans = st.number_input("🚗 بدل المواصلات", value=float(row.get('بدل مواصلات', 0) or 0), step=50.0, format="%.2f")
                    new_food = st.number_input("🍽️ بدل الاعاشة", value=float(row.get('بدل اعاشة', 0) or 0), step=50.0, format="%.2f")
                with cf3:
                    new_extra = st.number_input("⭐ علاوة", value=float(row.get('علاوة', 0) or 0), step=50.0, format="%.2f")
                    new_total = st.number_input("💵 إجمالي الراتب", value=float(row.get('إجمالي الراتب', 0) or 0), step=100.0, format="%.2f")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # ===== البيانات الوظيفية =====
                st.markdown('<div class="section-header">📋 البيانات الوظيفية</div>', unsafe_allow_html=True)
                st.markdown('<div class="group-card">', unsafe_allow_html=True)
                cj1, cj2, cj3 = st.columns(3)
                with cj1:
                    new_proj = st.text_input("📍 المشروع", value=str(row.get('المشروع', '') or ''))
                    new_branch = st.text_input("🏢 الفرع", value=str(row.get('الفرع', '') or ''))
                with cj2:
                    new_dept = st.text_input("🗂️ القسم", value=str(row.get('القسم', '') or ''))
                    new_title = st.text_input("💼 المسمى الوظيفي", value=str(row.get('المسمي الوظيفي', '') or ''))
                with cj3:
                    # تاريخ البداية - معالجة الأصفار والقيم الفارغة
                    raw_date = row.get('تاريخ  البداية', row.get('تاريخ البداية', ''))
                    try:
                        if pd.isna(raw_date) or str(raw_date).strip() in ['', 'nan', '0', '0.0']:
                            parsed_date = date.today()
                        else:
                            parsed_date = pd.to_datetime(str(raw_date), errors='coerce')
                            parsed_date = parsed_date.date() if pd.notna(parsed_date) else date.today()
                    except:
                        parsed_date = date.today()
                    
                    new_start_date = st.date_input("📅 تاريخ البداية", value=parsed_date)
                    
                    status_options = ["نشط", "موقوف"]
                    cur_status = str(row.get('حالة القيد', 'نشط'))
                    status_idx = 1 if cur_status == 'موقوف' else 0
                    new_status = st.selectbox("🔘 حالة القيد", status_options, index=status_idx)
                
                # عمود الشركة
                new_company = st.text_input("🏬 الشركة", value=str(row.get('الشركة', '') or ''))
                st.markdown('</div>', unsafe_allow_html=True)
                
                # ===== البيانات الشخصية =====
                st.markdown('<div class="section-header">👤 البيانات الشخصية</div>', unsafe_allow_html=True)
                st.markdown('<div class="group-card">', unsafe_allow_html=True)
                cp1, cp2, cp3 = st.columns(3)
                with cp1:
                    new_nat_id = st.text_input("🪪 رقم الهوية الوطنية", value=str(row.get('رقم الهوية الوطنية', '') or ''))
                    new_nation = st.text_input("🌍 الجنسية", value=str(row.get('الجنسية', '') or ''))
                with cp2:
                    new_gender = st.selectbox("⚥ الجنس", ["ذكر", "أنثى"], 
                                               index=0 if str(row.get('الجنس', 'ذكر')) == 'ذكر' else 1) if 'الجنس' in row.index else st.text_input("الجنس", "")
                    new_phone = st.text_input("📱 رقم الجوال", value=str(row.get('رقم الجوال', '') or ''))
                with cp3:
                    new_email = st.text_input("📧 البريد الإلكتروني", value=str(row.get('البريد الإلكتروني', '') or ''))
                    new_emp_num = st.text_input("🔢 الرقم الوظيفي أمنكو", value=str(row.get('الرقم الوظيفي امنكو', '') or ''))
                st.markdown('</div>', unsafe_allow_html=True)
                
                # ===== البيانات البنكية =====
                st.markdown('<div class="section-header">🏦 البيانات البنكية</div>', unsafe_allow_html=True)
                st.markdown('<div class="group-card">', unsafe_allow_html=True)
                cb1, cb2 = st.columns(2)
                with cb1:
                    new_bank = st.text_input("🏦 اسم البنك", value=str(row.get('البنك', '') or ''))
                with cb2:
                    new_iban = st.text_input("💳 رقم الآيبان (IBAN)", value=str(row.get('الايبان', '') or ''))
                st.markdown('</div>', unsafe_allow_html=True)

                # ===== التعاقد والإقامة =====
                st.markdown('<div class="section-header">📄 بيانات التعاقد والإقامة</div>', unsafe_allow_html=True)
                st.markdown('<div class="group-card">', unsafe_allow_html=True)
                cr1, cr2, cr3 = st.columns(3)
                with cr1:
                    new_contract = st.text_input("📝 نوع العقد", value=str(row.get('نوع العقد', '') or ''))
                    new_iqama = st.text_input("📋 رقم الإقامة", value=str(row.get('رقم الإقامة', '') or ''))
                with cr2:
                    new_iqama_exp = st.text_input("⏰ انتهاء الإقامة", value=str(row.get('انتهاء الإقامة', '') or ''))
                    new_passport = st.text_input("🛂 رقم الجواز", value=str(row.get('رقم الجواز', '') or ''))
                with cr3:
                    new_passport_exp = st.text_input("⏰ انتهاء الجواز", value=str(row.get('انتهاء الجواز', '') or ''))
                    new_work_permit = st.text_input("📜 رقم تصريح العمل", value=str(row.get('تصريح العمل', '') or ''))
                st.markdown('</div>', unsafe_allow_html=True)
                
                save_btn = st.form_submit_button("💾 حفظ جميع التغييرات", use_container_width=True)
                
                if save_btn:
                    updates = {
                        'الراتب الأساسي': new_basic,
                        'بدل السكن': new_housing,
                        'بدل مواصلات': new_trans,
                        'بدل اعاشة': new_food,
                        'علاوة': new_extra,
                        'إجمالي الراتب': new_total,
                        'المشروع': new_proj,
                        'الفرع': new_branch,
                        'القسم': new_dept,
                        'المسمي الوظيفي': new_title,
                        'تاريخ  البداية': new_start_date.strftime('%Y-%m-%d'),
                        'تاريخ البداية': new_start_date.strftime('%Y-%m-%d'),
                        'حالة القيد': new_status,
                        'الشركة': new_company,
                        'رقم الهوية الوطنية': new_nat_id,
                        'الجنسية': new_nation,
                        'رقم الجوال': new_phone,
                        'البريد الإلكتروني': new_email,
                        'البنك': new_bank,
                        'الايبان': new_iban,
                        'نوع العقد': new_contract,
                        'رقم الإقامة': new_iqama,
                        'انتهاء الإقامة': new_iqama_exp,
                        'رقم الجواز': new_passport,
                        'انتهاء الجواز': new_passport_exp,
                        'تصريح العمل': new_work_permit,
                        'الرقم الوظيفي امنكو': new_emp_num,
                    }
                    for k, v in updates.items():
                        if k in st.session_state.master_data.columns:
                            st.session_state.master_data.at[idx, k] = v
                    
                    st.success(f"✅ تم حفظ بيانات الموظف **{emp_to_edit}** بنجاح!")
                    st.rerun()

    # ============================================================
    # التبويب 4: كشف الرواتب
    # ============================================================
    with tab4:
        st.markdown('<div class="section-header">💰 كشف الرواتب الصافي الشهري</div>', unsafe_allow_html=True)
        
        payroll_df = df_display.copy()
        
        # فلتر النشطين فقط
        show_active_only = st.checkbox("عرض الموظفين النشطين فقط", value=True)
        if show_active_only and 'حالة القيد' in payroll_df.columns:
            payroll_df = payroll_df[payroll_df['حالة القيد'] == 'نشط']
        
        # حساب الصافي
        payroll_df['إجمالي المستحقات'] = (
            payroll_df.get('الراتب الأساسي', 0).fillna(0).astype(float) +
            payroll_df.get('بدل السكن', 0).fillna(0).astype(float) +
            payroll_df.get('بدل مواصلات', 0).fillna(0).astype(float) +
            payroll_df.get('بدل اعاشة', 0).fillna(0).astype(float) +
            payroll_df.get('علاوة', 0).fillna(0).astype(float) +
            payroll_df['مكافآت شهرية'].fillna(0).astype(float)
        )
        
        # حسم الغياب
        basic_daily = payroll_df.get('الراتب الأساسي', pd.Series([0]*len(payroll_df))).fillna(0).astype(float) / 30
        absence_deduction = basic_daily * payroll_df['أيام غياب'].fillna(0).astype(float)
        payroll_df['حسم الغياب'] = absence_deduction.round(2)
        
        payroll_df['إجمالي الحسومات'] = (
            payroll_df['حسومات شهرية'].fillna(0).astype(float) +
            payroll_df['حسم الغياب']
        )
        
        payroll_df['الصافي المستحق'] = (payroll_df['إجمالي المستحقات'] - payroll_df['إجمالي الحسومات']).round(2)
        
        # ملخص مالي
        pm1, pm2, pm3, pm4 = st.columns(4)
        with pm1:
            st.markdown(f"""<div class="stat-card">
                <div class="stat-number" style="font-size:1.5rem">{payroll_df['إجمالي المستحقات'].sum():,.0f}</div>
                <div class="stat-label">💰 إجمالي المستحقات (ر.س)</div>
            </div>""", unsafe_allow_html=True)
        with pm2:
            st.markdown(f"""<div class="stat-card" style="border-top-color:#ef4444">
                <div class="stat-number" style="font-size:1.5rem;color:#991b1b">{payroll_df['إجمالي الحسومات'].sum():,.0f}</div>
                <div class="stat-label">🔻 إجمالي الحسومات (ر.س)</div>
            </div>""", unsafe_allow_html=True)
        with pm3:
            st.markdown(f"""<div class="stat-card" style="border-top-color:#22c55e">
                <div class="stat-number" style="font-size:1.5rem;color:#166534">{payroll_df['الصافي المستحق'].sum():,.0f}</div>
                <div class="stat-label">✅ الصافي الإجمالي (ر.س)</div>
            </div>""", unsafe_allow_html=True)
        with pm4:
            st.markdown(f"""<div class="stat-card" style="border-top-color:#3b82f6">
                <div class="stat-number" style="font-size:1.5rem;color:#1d4ed8">{len(payroll_df)}</div>
                <div class="stat-label">👥 عدد الموظفين</div>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # الأعمدة المهمة للعرض
        important_cols = ['اسم الموظف', 'الرقم الوظيفي امنكو', 'المشروع', 'الشركة',
                         'الراتب الأساسي', 'بدل السكن', 'بدل مواصلات', 'بدل اعاشة', 'علاوة',
                         'مكافآت شهرية', 'إجمالي المستحقات',
                         'حسومات شهرية', 'أيام غياب', 'حسم الغياب', 'إجمالي الحسومات',
                         'الصافي المستحق', 'ملاحظات المؤثرات', 'البنك', 'الايبان']
        
        show_cols_payroll = [c for c in important_cols if c in payroll_df.columns]
        st.dataframe(payroll_df[show_cols_payroll], use_container_width=True, hide_index=True, height=400)
        
        # تحميل المسير
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_data = payroll_df[show_cols_payroll].to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                "📥 تحميل المسير (CSV)",
                data=csv_data,
                file_name=f"كشف_الرواتب_{datetime.now().strftime('%Y_%m')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_dl2:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                payroll_df[show_cols_payroll].to_excel(writer, index=False, sheet_name='كشف الرواتب')
            st.download_button(
                "📊 تحميل المسير (Excel)",
                data=excel_buffer.getvalue(),
                file_name=f"كشف_الرواتب_{datetime.now().strftime('%Y_%m')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

else:
    st.markdown("""
    <div style="
        text-align:center;
        padding: 80px 40px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        margin-top: 40px;
    ">
        <div style="font-size:5rem;margin-bottom:20px">📂</div>
        <h2 style="color:#1a2744;font-size:1.8rem;font-weight:900">مرحباً بك في نظام إدارة الموارد البشرية</h2>
        <p style="color:#64748b;font-size:1.1rem;margin-top:12px">
            يرجى رفع ملف الماستر داتا من القائمة الجانبية للبدء
        </p>
        <div style="
            display:inline-block;
            margin-top:24px;
            padding:12px 28px;
            background:linear-gradient(135deg,#1a2744,#2d4a8a);
            color:#c9a84c;
            border-radius:10px;
            font-weight:700;
            font-size:0.95rem;
        ">⬅️ ابدأ برفع الملف من القائمة الجانبية</div>
    </div>
    """, unsafe_allow_html=True)
