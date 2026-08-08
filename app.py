import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Very Very - ระบบจัดตารางเวรอัจฉริยะ", 
    page_icon="🏥", 
    layout="centered"
)

# --- CSS ตกแต่งเพิ่มเติมให้ดูพรีเมียมและซ่อน Sidebar ในหน้า Login ---
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    .main-title {
        text-align: center;
        font-weight: 700;
        color: #1E3A8A;
    }
    .sub-title {
        text-align: center;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# เริ่มต้น Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 class='main-title'>🌟 Very Very</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-title'>ผู้ช่วยจัดตารางเวรอัจฉริยะสำหรับหอผู้ป่วย</h3>", unsafe_allow_html=True)
    
    # ใช้ Container จัดกึ่งกลางให้ฟอร์มดูสวยงาม
    with st.container():
        st.info("🔐 กรุณากรอกรหัสผ่านเพื่อเข้าสู่ระบบจัดการตารางเวร")
        
        with st.form("login_form"):
            password = st.text_input("รหัสผ่านระบบ (Password)", type="password", placeholder="กรอกรหัสผ่าน...")
            submit_button = st.form_submit_button("เข้าสู่ระบบ 🚀", use_container_width=True)
            
            if submit_button:
                if password == "Very59": # รหัสผ่านระบบ
                    st.session_state.logged_in = True
                    st.success("🎉 เข้าสู่ระบบสำเร็จ! กำลังพาท่านเข้าสู่ระบบ...")
                    st.rerun()
                else:
                    st.error("❌ รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
else:
    st.success("✅ คุณเข้าสู่ระบบเรียบร้อยแล้ว!")
    st.info("👉 คลิกปุ่มด้านล่างเพื่อเข้าสู่หน้าจัดการรายชื่อและตั้งค่าตารางเวรได้เลยครับ")
    
    if st.button("📋 เริ่มต้นใช้งาน (จัดการรายชื่อและเงื่อนไข)", type="primary", use_container_width=True):
        st.switch_page("pages/1.staff setup.py")
        
    if st.button("🚪 ออกจากระบบ", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
