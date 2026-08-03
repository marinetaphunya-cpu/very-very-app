import streamlit as st
import time
import pandas as pd

st.set_page_config(page_title="AI Generating Roster", page_icon="⏳", layout="centered")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ กรุณาล็อกอินก่อนครับ")
    st.stop()

st.title("⏳ AI กำลังประมวลผลจัดตารางเวร...")
st.write(f"กำลังจัดตารางเวรสำหรับ **เดือน{st.session_state.get('target_month', 'สิงหาคม')} พ.ศ. {st.session_state.get('target_year', 2569)}**")

with st.status("กำลังวิเคราะห์ข้อมูลด้วย Gemini AI...", expanded=True) as status:
    st.write("🔍 ตรวจสอบรายชื่อบุคลากรและตำแหน่ง...")
    time.sleep(1.5)
    st.write("⚖️ จัดสรรเวรเช้า บ่าย ดึก ตามสัดส่วนกำลังคน...")
    time.sleep(1.5)
    st.write("🛡️ ตรวจสอบเงื่อนไขความปลอดภัย (ไม่เกิน 7 วัน)...")
    time.sleep(1.5)
    status.update(label="✨ จัดตารางเวรเสร็จสมบูรณ์แล้ว!", state="complete", expanded=False)

if "roster_data" not in st.session_state:
    mock_roster = pd.DataFrame([
        {"ลำดับ": 1, "ชื่อ-นามสกุล": "พญ.สมศรี (หัวหน้า RN)", "ตำแหน่ง": "RN", "วันที่ 1": "เช้า", "วันที่ 2": "เช้า", "วันที่ 3": "เช้า", "วันที่ 4": "เช้า", "วันที่ 5": "เช้า", "รวมหยุด": 0},
        {"ลำดับ": 2, "ชื่อ-นามสกุล": "นース ไอด้า", "ตำแหน่ง": "RN", "วันที่ 1": "บ่าย", "วันที่ 2": "ดึก", "วันที่ 3": "X", "วันที่ 4": "เช้า", "วันที่ 5": "บ่าย", "รวมหยุด": 1},
        {"ลำดับ": 3, "ชื่อ-นามสกุล": "พี่กบ (หัวหน้า PN)", "ตำแหน่ง": "PN", "วันที่ 1": "เช้า", "วันที่ 2": "เช้า", "วันที่ 3": "เช้า", "วันที่ 4": "เช้า", "วันที่ 5": "เช้า", "รวมหยุด": 0},
        {"ลำดับ": 4, "ชื่อ-นามสกุล": "พี่เอื้อม (แม่บ้าน)", "ตำแหน่ง": "PN/แม่บ้าน", "วันที่ 1": "เช้า", "วันที่ 2": "เช้า", "วันที่ 3": "X", "วันที่ 4": "X", "วันที่ 5": "เช้า", "รวมหยุด": 2},
    ])
    st.session_state.roster_data = mock_roster
    st.session_state.original_data = mock_roster.copy()

st.success("🎉 ตารางเวรพร้อมแล้ว!")
if st.button("👉 ไปดูตารางเวรประจำเดือน", type="primary", use_container_width=True):
    st.switch_page("pages/3_📅_Roster_Table.py")

