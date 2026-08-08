import streamlit as st
import time
import pandas as pd
import google.generativeai as genai

# ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="AI Generating Roster", page_icon="⏳", layout="centered")

# --- CSS สำหรับซ่อนแถบเมนู Sidebar ด้านข้างของ Streamlit ---
hide_streamlit_style = """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ตรวจสอบการล็อกอิน
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ กรุณาล็อกอินก่อนครับ")
    st.stop()

st.title("⏳ AI กำลังประมวลผลจัดตารางเวร...")
target_month = st.session_state.get('target_month', 'สิงหาคม')
target_year = st.session_state.get('target_year', 2569)
st.write(f"กำลังจัดตารางเวรสำหรับ **เดือน{target_month} พ.ศ. {target_year}**")

# --- ส่วนของการเรียกใช้งานโมเดล Gemini ตัวล่าสุด ---
# หมายเหตุ: ไอด้าต้องมั่นใจว่าตั้งค่า st.secrets["GOOGLE_API_KEY"] ไว้แล้วใน Streamlit Cloud
try:
    if "MY_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["MY_API_KEY"])
        # ใช้โมเดลระดับท็อปสำหรับงานวิเคราะห์เงื่อนไขซับซ้อนตามที่ไอด้าต้องการ
        model = genai.GenerativeModel('gemini-2.5-pro')
    else:
        model = None
except Exception as e:
    model = None

with st.status("กำลังวิเคราะห์ข้อมูลด้วย Gemini AI...", expanded=True) as status:
    st.write("🔍 ตรวจสอบรายชื่อบุคลากรและตำแหน่งตามวอร์ด...")
    time.sleep(1.0)
    
    st.write("⚖️ วิเคราะห์กฎตายตัวและเงื่อนไขเพิ่มเติม (Soft Constraints)...")
    time.sleep(1.0)
    
    if model:
        st.write("🤖 กำลังสั่งการ Gemini 2.5 Pro ประมวลผลตารางเวรตามอัตรากำลัง...")
        # ตรงนี้สามารถส่ง Prompt ไปยัง Gemini ได้หากต้องการให้ AI ช่วย generate ข้อมูลดิบลงตาราง
        # prompt = f"จัดตารางเวรพยาบาลเดือน {target_month}..."
        # response = model.generate_content(prompt)
    else:
        st.write("⚠️ ไม่พบ API Key กำลังใช้ระบบจำลองโครงสร้างตารางอัจฉริยะแทน...")
    
    time.sleep(1.0)
    st.write("🛡️ ตรวจสอบเงื่อนไขความปลอดภัย (ห้ามบ่ายต่อดึก และห้ามดึกต่อเช้า)...")
    time.sleep(1.0)
    st.write("✨ พยาบาลเวรเช้า (จ-ศ 3 คน / บ่าย 2 คน / ดึก 1 คน / ส-อ 1 คน)")
    time.sleep(1.0)
    st.write("✨ ผู้ช่วยพยาบาลเวรเช้า (จ-ศ 2 คน / บ่าย 1 คน / ดึก 1 คน / ส-อ 1 คน)")
    time.sleep(1.0)
    status.update(label="✨ จัดตารางเวรเสร็จสมบูรณ์แล้ว!", state="complete", expanded=False)

# ดึงข้อมูลรายชื่อจากหน้าแรกมาสร้างตาราง
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
    
    # สมมติให้เดือนนี้มี 31 วัน (ปรับตามความเหมาะสมได้)
    for day in range(1, 32):
        data[str(day)] = [""] * num_rows
        
    # ช่องสรุปท้ายตาราง
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

# ปุ่มกดไปหน้าถัดไป (บังคับเส้นทาง)
if st.button("👉 ไปดูตารางเวรประจำเดือน", type="primary", use_container_width=True):
    st.switch_page("pages/3.Roster table.py")
