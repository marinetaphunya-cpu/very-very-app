import streamlit as st
import pandas as pd

st.set_page_config(page_title="Staff & Rules Setup", page_icon="📋", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ กรุณาล็อกอินเข้าสู่ระบบก่อนใช้งานหน้านี้")
    st.stop()

st.title("📋 จัดการรายชื่อบุคลากรและกำหนดเดือนตารางเวร")
st.write("เลือกเดือน/ปีที่ต้องการจัดตาราง พร้อมกรอกรายชื่อพยาบาล RN, PN และตำแหน่งในวอร์ด")

# เลือกเดือนและปี
col_m1, col_m2 = st.columns(2)
with col_m1:
    months_list = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
                   "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    selected_month = st.selectbox("เลือกเดือนสำหรับจัดตารางเวร", months_list, index=7) # ค่าเริ่มต้น สิงหาคม
with col_m2:
    selected_year = st.selectbox("เลือกปี พ.ศ.", [2569, 2570, 2571], index=0)

st.session_state.target_month = selected_month
st.session_state.target_year = selected_year

st.markdown("---")
st.subheader("👥 รายชื่อบุคลากรและตำแหน่งในวอร์ด")

# ปรับคอลัมน์ให้ตรงตามฟอร์มจริง (ลำดับ, ชื่อ - สกุล, ตำแหน่ง)
if "staff_data" not in st.session_state:
    st.session_state.staff_data = pd.DataFrame([
        {"ลำดับ": 1, "ชื่อ - สกุล": "นางสาวA", "ตำแหน่ง": "พยาบาล"},
        {"ลำดับ": 2, "ชื่อ - สกุล": "นางสาวB", "ตำแหน่ง": "พยาบาล"},
        {"ลำดับ": 3, "ชื่อ - สกุล": "นางสาวC", "ตำแหน่ง": "พยาบาล"},
        {"ลำดับ": 4, "ชื่อ - สกุล": "นางสาวD", "ตำแหน่ง": "พยาบาล"},
        {"ลำดับ": 5, "ชื่อ - สกุล": "นางสาวE", "ตำแหน่ง": "พยาบาล"},
        {"ลำดับ": 6, "ชื่อ - สกุล": "นางสาวF", "ตำแหน่ง": "ผู้ช่วยพยาบาล"},
        {"ลำดับ": 7, "ชื่อ - สกุล": "นางสาวG", "ตำแหน่ง": "ผู้ช่วยพยาบาล"},
        {"ลำดับ": 8, "ชื่อ - สกุล": "นางสาวH", "ตำแหน่ง": "ผู้ช่วยพยาบาล"},
        {"ลำดับ": 9, "ชื่อ - สกุล": "นางสาวI", "ตำแหน่ง": "ผู้ช่วยพยาบาล"},
        {"ลำดับ": 10,"ชื่อ - สกุล": "นางสาวJ", "ตำแหน่ง": "ผู้ช่วยพยาบาล"},
    ])

edited_staff = st.data_editor(st.session_state.staff_data, num_rows="dynamic", use_container_width=True)
st.session_state.staff_data = edited_staff

st.markdown("---")
st.subheader("⚙️ เงื่อนไขการประชุมและกฎเหล็ก")
st.checkbox("เชื่อมโยงตารางประชุมคณะกรรมการหอผู้ป่วย (เช่น พุธที่ 1, พุธที่ 2 ของเดือน)", value=True)
st.checkbox("ล็อกหัวหน้าหอผู้ป่วยและหัวหน้า PN ขึ้นเวรเช้า จันทร์-ศุกร์", value=True)
st.checkbox("จำกัดการทำงานติดต่อกันไม่เกิน 7 วัน", value=True)

st.markdown("---")
if st.button("🚀 ยืนยันข้อมูลและไปหน้าจัดเวรอัจฉริยะ", type="primary", use_container_width=True):
    st.switch_page("pages/2.ai generate.py")
