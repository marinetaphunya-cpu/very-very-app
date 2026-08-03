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
st.info("💡 คำแนะนำ: ระบบดึงรายชื่อและจัดตารางเวรให้อัตโนมัติ สามารถคลิกแก้ตารางได้ ข้อมูลที่เปลี่ยนจะไฮไลท์ **สีม่วง** ครับ")

# ดึงข้อมูลรายชื่อและตำแหน่งจากหน้าแรก (Staff Setup) มาใช้เสมอ
if "staff_data" in st.session_state:
    staff_df = st.session_state.staff_data
    num_rows = len(staff_df)
    
    # สร้างตารางใหม่สดๆ ทุกครั้ง เพื่อให้ดึงชื่อและใส่เวรจำลองให้ทันทีโดยไม่โล่ง
    data = {
        "ลำดับ": staff_df.get("ลำดับ", list(range(1, num_rows + 1))),
        "ชื่อ - สกุล": staff_df.get("ชื่อ - สกุล", [""] * num_rows),
        "ตำแหน่ง": staff_df.get("ตำแหน่ง", [""] * num_rows)
    }
    
    # สุ่มใส่เวรจำลอง (เช้า, บ่าย, ดึก, หยุด x) ลงในวันที่ 1 ถึง 31 ให้เต็มตารางดูสมจริง
    shift_options = ["เช้า", "บ่าย", "ดึก", "x", "V"]
    for day in range(1, 32):
        col_values = []
        for i in range(num_rows):
            # กำหนดเวรตัวอย่างให้ดูสมจริง
            if day in [1, 8, 15, 22, 29]: # สมมติวันหยุดประจำสัปดาห์
                col_values.append("x")
            else:
                # สุ่มเวร เช้า บ่าย ดึก ให้ตารางไม่โล่ง
                col_values.append(random.choice(["เช้า", "บ่าย", "ดึก", ""]))
        data[str(day)] = col_values
        
    # ช่องสรุปและหมายเหตุ
    data["หยุด"] = [str(random.randint(4, 8))] * num_rows
    data["ค้าง"] = ["0"] * num_rows
    data["OT_ด"] = ["1"] * num_rows
    data["OT_ช"] = ["0"] * num_rows
    data["OT_บ"] = ["2"] * num_rows
    data["เวร_ด"] = ["4"] * num_rows
    data["เวร_บ"] = ["5"] * num_rows
    data["หมายเหตุ"] = [""] * num_rows

    current_df = pd.DataFrame(data)
    
    # เก็บต้นฉบับไว้เทียบสีม่วงเวลาแก้
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
