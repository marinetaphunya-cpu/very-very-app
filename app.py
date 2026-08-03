import streamlit as st

st.set_page_config(page_title="Very Very - Login", page_icon="🌟", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌟 Very Very")
    st.subheader("ผู้ช่วยจัดตารางเวรอัจฉริยะสำหรับหอผู้ป่วย")
    st.write("กรุณากรอกรหัสผ่านเพื่อเข้าสู่ระบบจัดการเวร")
    
    password = st.text_input("รหัสผ่านระบบ (Password)", type="password")
    
    if st.button("เข้าสู่ระบบ 🚀", use_container_width=True):
        if password == "1234": # เปลี่ยนรหัสผ่านได้ตามต้องการ
            st.session_state.logged_in = True
            st.success("เข้าสู่ระบบสำเร็จ! กำลังพาท่านไปหน้าจัดการเวร...")
            st.rerun()
        else:
            st.error("รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
else:
    st.success("คุณเข้าสู่ระบบอยู่แล้ว!")
    st.info("👈 สามารถเลือกเมนูการทำงานต่างๆ จากแถบด้านซ้ายมือได้เลยครับ")
    if st.button("ออกจากระบบ"):
        st.session_state.logged_in = False
        st.rerun()

