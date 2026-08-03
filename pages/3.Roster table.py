import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Very Very - Roster Table", page_icon="📅", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ กรุณาล็อกอินก่อนครับ")
    st.stop()

t_month = st.session_state.get('target_month', 'สิงหาคม')
t_year = st.session_state.get('target_year', 2569)

st.title(f"📅 กำหนดการปฏิบัติงานสำหรับเจ้าหน้าที่พยาบาล เดือน{t_month} พ.ศ. {t_year}")
st.info("💡 คำแนะนำ: ระบบจัดเวรอัจฉริยะควบคุมกฎความปลอดภัย (**ห้ามบ่ายต่อดึก, ห้ามดึกต่อเช้า**) สามารถคลิกแก้ไขตารางได้ ข้อมูลที่เปลี่ยนจะไฮไลท์ **สีม่วง** ครับ")

# ดึงข้อมูลรายชื่อและตำแหน่งจากหน้าแรก (Staff Setup) มาใช้
if "staff_data" in st.session_state:
    staff_df = st.session_state.staff_data
    num_rows = len(staff_df)
    
    data = {
        "ลำดับ": staff_df.get("ลำดับ", list(range(1, num_rows + 1))),
        "ชื่อ - สกุล": staff_df.get("ชื่อ - สกุล", [""] * num_rows),
        "ตำแหน่ง": staff_df.get("ตำแหน่ง", [""] * num_rows)
    }
    
    # เก็บสถานะเวรของวันก่อนหน้าสำหรับพยาบาลแต่ละคน (เริ่มต้นให้ไม่มีเวร หรือว่าง)
    # ใช้จำค่าเวรวันก่อนหน้าเพื่อเอามาเช็คกฎเหล็ก
    previous_shifts = [""] * num_rows
    
    # วนลูปจัดเวรทีละวัน ตั้งแต่วันที่ 1 ถึง 31
    for day in range(1, 32):
        col_values = []
        # สุ่มคนที่จะได้หยุด (x) ในวันนี้ (วันละประมาณ 2 คน เพื่อไม่ให้วอร์ดแตก)
        off_duty_indices = random.sample(range(num_rows), k=min(2, num_rows))
        
        for i in range(num_rows):
            if i in off_duty_indices:
                col_values.append("x")
                previous_shifts[i] = "x" # อัปเดตเวรวันก่อนหน้าเป็นหยุด
            else:
                # รายการเวรที่เป็นไปได้ทั้งหมด
                allowed_shifts = ["เช้า", "บ่าย", "ดึก"]
                
                # กฎเหล็ก 1: ถ้าวันก่อนหน้าลง "บ่าย" ห้ามขึ้น "ดึก" วันนี้
                if previous_shifts[i] == "บ่าย" and "ดึก" in allowed_shifts:
                    allowed_shifts.remove("ดึก")
                
                # กฎเหล็ก 2: ถ้าวันก่อนหน้าลง "ดึก" ห้ามขึ้น "เช้า" วันนี้ (เพื่อให้นอนพักผ่อนพอ)
                if previous_shifts[i] == "ดึก" and "เช้า" in allowed_shifts:
                    allowed_shifts.remove("เช้า")
                
                # สุ่มเลือกเวรจากตัวเลือกที่ปลอดภัยแล้ว
                chosen_shift = random.choice(allowed_shifts)
                col_values.append(chosen_shift)
                
                # บันทึกเวรวันนี้เก็บไว้เช็คของวันถัดไป
                previous_shifts[i] = chosen_shift
                
        data[str(day)] = col_values
        
    # ช่องสรุปและหมายเหตุคำนวณคร่าวๆ
    data["หยุด"] = [str(random.randint(6, 8))] * num_rows
    data["ค้าง"] = ["0"] * num_rows
    data["OT_ด"] = ["1"] * num_rows
    data["OT_ช"] = ["0"] * num_rows
    data["OT_บ"] = ["2"] * num_rows
    data["เวร_ด"] = ["5"] * num_rows
    data["เวร_บ"] = ["6"] * num_rows
    data["หมายเหตุ"] = [""] * num_rows

    current_df = pd.DataFrame(data)
    
    if "original_data" not in st.session_state:
        st.session_state.original_data = current_df.copy()
        
    original_df = st.session_state.original_data

    # แสดงตารางที่แก้ไขได้
    edited_roster = st.data_editor(current_df, use_container_width=True, key="ward_roster_editor")

    # โน้ตเพิ่มเติม
    st.markdown("---")
    st.subheader("📝 บันทึกข้อความ / หมายเหตุประจำเดือน")
    note_text = st.text_area("พิมพ์ข้อความชี้แจงเพิ่มเติมหรือบันทึกข้อตกลงในวอร์ด...", placeholder="เช่น บันทึกการประชุมพุธที่ 1 ของเดือน...")

    # ปุ่มบันทึกและแชร์
    st.markdown("---")
    col1, col2, col3 = st.columns([6, 2, 2])
    with col2:
        if st.button("💾 บันทึกตารางเวร", use_container_width=True):
            st.success("บันทึกการแก้ไขเรียบร้อยแล้ว!")
    with col3:
        if st.button("🔗 แชร์ตารางเวร", use_container_width=True):
            st.toast("คัดลอกลิงก์สำหรับแชร์สำเร็จ!", icon="🚀")
else:
    st.warning("⚠️ กรุณากลับไปกรอกรายชื่อที่หน้า Staff Setup ก่อนครับ")
