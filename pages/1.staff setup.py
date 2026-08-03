import streamlit as st
import pandas as pd

st.set_page_config(page_title="Staff & Rules Setup", page_icon="📋", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ กรุณาล็อกอินเข้าสู่ระบบก่อนใช้งานหน้านี้")
    st.stop()

st.title("📋 จัดการรายชื่อบุคลากรและกำหนดเดือนตารางเวร")
st.write("เลือกเดือน/ปีที่ต้องการจัดตาราง พร้อมกรอกรายชื่อพยาบาล RN, PN และตั้งค่าเงื่อนไข")

# เพิ่มส่วนเลือกเดือนและปี
col_m1, col_m2 = st.columns(2)
with col_m1:
    months_list = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
                   "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    selected_month = st.selectbox("เลือกเดือนสำหรับจัดตารางเวร", months_list, index=7) # เริ่มต้นที่สิงหาคม
with col_m2:
    selected_year = st.selectbox("เลือกปี พ.ศ.", [2569, 2570, 2571], index=0)

# บันทึกเดือนและปีลงใน session_state เพื่อเอาไปแสดงหน้าสุดท้าย
st.session_state.target_month = selected_month
st.session_state.target_year = selected_year

st.markdown("---")
st.subheader("👥 รายชื่อบุคลากรในวอร์ด")

if "staff_data" not in st.session_state:
    st.session_state.staff_data = pd.DataFrame([
        {"ลำดับ": 1, "ชื่อ-นามสกุล": "พยาบาล A", "ตำแหน่ง": "RN", "กลุ่มเวร": "เช้า (จันทร์-ศุกร์)"},
        {"ลำดับ": 2, "ชื่อ-นามสกุล": "พยาบาล B", "ตำแหน่ง": "RN", "กลุ่มเวร": "ทั่วไป"},
        {"ลำดับ": 3, "ชื่อ-นามสกุล": "ผู้ช่วยพยาบาล C", "ตำแหน่ง": "PN", "กลุ่มเวร": "เช้า (จันทร์-ศุกร์)"},
        {"ลำดับ": 4, "ชื่อ-นามสกุล": "พนักงานช่วย", "ตำแหน่ง": "PN", "กลุ่มเวร": "ทั่วไป"},
    ])

edited_staff = st.data_editor(st.session_state.staff_data, num_rows="dynamic", use_container_width=True)
st.session_state.staff_data = edited_staff

st.markdown("---")
st.subheader("⚙️ เงื่อนไขบังคับในการจัดเวร")
st.checkbox("ล็อกหัวหน้าหอผู้ป่วย RN และหัวหน้า PN ขึ้นเฉพาะเวรเช้า (จันทร์-ศุกร์)", value=True)
st.checkbox("จำกัดการทำงานติดต่อกันไม่เกิน 7 วัน", value=True)
st.checkbox("สิทธิ์วันหยุด Vacation เดือนละ 1-2 คน", value=True)

st.markdown("---")
if st.button("🚀 ยืนยันข้อมูลและไปหน้าจัดเวรอัจฉริยะ (AI)", type="primary", use_container_width=True):
    st.switch_page("pages/2.ai generate.py")

