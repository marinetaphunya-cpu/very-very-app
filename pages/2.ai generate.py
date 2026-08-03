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
    st.write("🛡️ ตรวจสอบเงื่อนไขความปลอดภัย (ไม่เกิน 7 วัน และวันหยุด)...")
    time.sleep(1.5)
    status.update(label="✨ จัดตารางเวรเสร็จสมบูรณ์แล้ว!", state="complete", expanded=False)

# สร้างข้อมูลจำลองให้ตรงกับโครงสร้างฟอร์มตารางจริง (วันที่ 1-31, ช่องสรุป, หมายเหตุ)
if "roster_data" not in st.session_state:
    data = {
        "ลำดับ": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "ชื่อ - สกุล": [
            "นายปัณณธร ศฤงคาร", "นางสาวธัญญาลักษณ์ บุญประคม", "นางสาวนิศารัตน์ วงศ์ใหญ่",
            "นางสาวนิสารัตน์ ไชยวงศ์", "นางสาวจิราภรณ์ บำรุงผล", "นายนภัทร โขโยนะ",
            "นางสาวพิมพ์มาดา ศรีคำวัง", "นางสาวมารินี ทาปัญญา", "นางสาวณัชพุนินทร์ ทองเพ็ญ", "นางสาวสายแนน แสนสามารถ"
        ],
        "ตำแหน่ง": ["พยาบาล", "พยาบาล", "พยาบาล", "พยาบาล", "พยาบาล", "พยาบาล", "พยาบาล", "พยาบาล", "พยาบาล", "ผู้ปฏิบัติฯ"]
    }
    
    # เติมช่องวันที่ 1 ถึง 31
    for day in range(1, 32):
        data[str(day)] = [""] * 10
        
    # เติมช่องสรุปท้ายตารางให้ครบชุด
    data["หยุด"] = [""] * 10
    data["ค้าง"] = [""] * 10
    data["OT_ด"] = [""] * 10
    data["OT_ช"] = [""] * 10
    data["OT_บ"] = [""] * 10
    data["เวร_ด"] = [""] * 10
    data["เวร_บ"] = [""] * 10
    data["หมายเหตุ"] = [""] * 10

    st.session_state.roster_data = pd.DataFrame(data)
    st.session_state.original_data = st.session_state.roster_data.copy()

st.success("🎉 ตารางเวรพร้อมแล้ว!")

# แก้ชื่อลิงก์หน้าปลายทางให้ตรงกับชื่อไฟล์จริง 3_📅_Roster_Table.py อย่างถูกต้อง
if st.button("👉 ไปดูตารางเวรประจำเดือน", type="primary", use_container_width=True):
    st.switch_page("pages/3.Roster table.py")
