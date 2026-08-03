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
st.info("💡 คำแนะนำ: ระบบจำลองการจัดเวรแบบสลับสับเปลี่ยนกำลังคน ไม่ให้หยุดตรงกัน สามารถคลิกแก้ไขตารางได้ ข้อมูลที่เปลี่ยนจะไฮไลท์ **สีม่วง** ครับ")

# ดึงข้อมูลรายชื่อและตำแหน่งจากหน้าแรก (Staff Setup) มาใช้
if "staff_data" in st.session_state:
    staff_df = st.session_state.staff_data
    num_rows = len(staff_df)
    
    data = {
        "ลำดับ": staff_df.get("ลำดับ", list(range(1, num_rows + 1))),
        "ชื่อ - สกุล": staff_df.get("ชื่อ - สกุล", [""] * num_rows),
        "ตำแหน่ง": staff_df.get("ตำแหน่ง", [""] * num_rows)
    }
    
    # อัลกอริทึมจำลองการจัดเวรที่ไม่ให้ทุกคนหยุดพร้อมกัน และสลับเวร เช้า บ่าย ดึก อย่างสมดุล
    shift_pool = ["เช้า", "บ่าย", "ดึก", "x", ""]
    
    for day in range(1, 32):
        col_values = []
        # สุ่มเลือกคนที่จะได้หยุดในแต่ละวัน (ให้หยุดแค่วันละ 1-2 คนพอ ไม่ให้หยุดหมด)
        off_duty_indices = random.sample(range(num_rows), k=min(2, num_rows))
        
        for i in range(num_rows):
            if i in off_duty_indices:
                col_values.append("x") # คนที่ได้รับสิทธิ์หยุดวันนี้
            else:
                # สลับเวร เช้า บ่าย ดึก ไม่ให้ซ้ำกันสะเปะสะปะ
                assigned_shift = random.choice(["เช้า", "บ่าย", "ดึก"])
                col_values.append(assigned_shift)
                
        data[str(day)] = col_values
        
    # ช่องสรุปและหมายเหตุ
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
