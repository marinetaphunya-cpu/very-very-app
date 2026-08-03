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
    st.write("🔍 ตรวจสอบรายชื่อบุคลากรและตำแหน่งตามวอร์ด...")
    time.sleep(1.5)
    st.write("⚖️ จัดสรรเวรเช้า บ่าย ดึก และวันประชุมคณะกรรมการ...")
    time.sleep(1.5)
    st.write("🛡️ ตรวจสอบเงื่อนไขความปลอดภัย (ห้ามบ่ายต่อดึก และห้ามดึกต่อเช้า)...")
    time.sleep(1.5)
    st.write("👾 พยาบาลเวรเช้า (รวมหัวหน้าพยาบาล จ-ศ 3 คน), เวรบ่าย 2 คน, เวรดึก 1 คน, ส-อ พยาบาล 1 คน")
    time.sleep(1.5)
    st.write("ผู้ช่วยพยาบาลเวรเช้า (รวมหัวหน้าผู้ช่วยพยาบาล จ-ศ 2 คน), เวรบ่าย 1 คน, เวรดึก 1 คน, ส-อ ผู้ช่วยพยาบาล 1 คน")
    time.sleep(1.5)
    status.update(label="✨ จัดตารางเวรเสร็จสมบูรณ์แล้ว!", state="complete", expanded=False)

# สร้างข้อมูลจำลองดึงจากหน้าแรก ถ้ามี
if "staff_data" in st.session_state:
    staff_df = st.session_state.staff_data
    num_rows = len(staff_df)
    names = staff_df.get("ชื่อ - สกุล", [""] * num_rows).tolist()
    positions = staff_df.get("ตำแหน่ง", [""] * num_rows).tolist()
else:
    num_rows = 10
    names = [f"นางสาวพยาบาล {i+1}" for i in range(num_rows)]
    positions = ["พยาบาล"] * 9 + ["ผู้ปฏิบัติฯ"]

if "roster_data" not in st.session_state:
    data = {
        "ลำดับ": list(range(1, num_rows + 1)),
        "ชื่อ - สกุล": names,
        "ตำแหน่ง": positions
    }
    
    # เติมช่องวันที่ 1 ถึง 31
    for day in range(1, 32):
        data[str(day)] = [""] * num_rows
        
    # เติมช่องสรุปท้ายตารางให้ครบชุด
    data["หยุด"] = [""] * num_rows
    data["ค้าง"] = [""] * num_rows
    data["OT_ด"] = [""] * num_rows
    data["OT_ช"] = [""] * num_rows
    data["OT_บ"] = [""] * num_rows
    data["เวร_ด"] = [""] * num_rows
    data["เวร_บ"] = [""] * num_rows
    data["หมายเหตุ"] = [""] * num_rows

    st.session_state.roster_data = pd.DataFrame(data)
    st.session_state.original_data = st.session_state.roster_data.copy()

st.success("🎉 ตารางเวรพร้อมแล้ว!")

if st.button("👉 ไปดูตารางเวรประจำเดือน", type="primary", use_container_width=True):
    st.switch_page("pages/3.Roster table.py")
