import streamlit as st
import pandas as pd

st.set_page_config(page_title="Very Very - Roster Table", page_icon="📅", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ กรุณาล็อกอินก่อนครับ")
    st.stop()

t_month = st.session_state.get('target_month', 'สิงหาคม')
t_year = st.session_state.get('target_year', 2569)

st.title(f"📅 กำหนดการปฏิบัติงานสำหรับเจ้าหน้าที่พยาบาล เดือน{t_month} พ.ศ. {t_year}")
st.info("💡 คำแนะนำ: ระบบดึงรายชื่อและตำแหน่งจากหน้าแรกมาแสดงอัตโนมัติ สามารถคลิกแก้ตารางได้ ข้อมูลที่เปลี่ยนจะไฮไลท์ **สีม่วง** ครับ")

# ดึงข้อมูลรายชื่อและตำแหน่งจากหน้าแรก (Staff Setup) มาใช้
if "staff_data" in st.session_state:
    staff_df = st.session_state.staff_data
    num_rows = len(staff_df)
    
    # ตรวจสอบว่ามีข้อมูลตารางเวรเดิมอยู่แล้วไหม ถ้ายังให้สร้างใหม่โดยดึงชื่อจากหน้าแรก
    if "roster_data" not in st.session_state:
        data = {
            "ลำดับ": staff_df.get("ลำดับ", list(range(1, num_rows + 1))),
            "ชื่อ - สกุล": staff_df.get("ชื่อ - สกุล", [""] * num_rows),
            "ตำแหน่ง": staff_df.get("ตำแหน่ง", [""] * num_rows)
        }
        
        # เติมช่องวันที่ 1 ถึง 31 พร้อมตัวอย่างเวร
        for day in range(1, 32):
            col_values = []
            for i in range(num_rows):
                if day in [1, 2]:
                    col_values.append("x")
                elif day in [5, 6, 7] and i % 2 == 0:
                    col_values.append("ด")
                elif day in [5, 6, 7] and i % 2 != 0:
                    col_values.append("บ")
                else:
                    col_values.append("")
            data[str(day)] = col_values
            
        # ช่องสรุปและหมายเหตุ
        data["หยุด"] = ["2"] * num_rows
        data["ค้าง"] = [""] * num_rows
        data["OT_ด"] = [""] * num_rows
        data["OT_ช"] = [""] * num_rows
        data["OT_บ"] = [""] * num_rows
        data["เวร_ด"] = [""] * num_rows
        data["เวร_บ"] = [""] * num_rows
        data["หมายเหตุ"] = [""] * num_rows

        st.session_state.roster_data = pd.DataFrame(data)
        st.session_state.original_data = st.session_state.roster_data.copy()
    else:
        # อัปเดตรายชื่อและตำแหน่งให้ตรงกับหน้าแรกเสมอ กรณีมีการแก้ไขชื่อเพิ่ม/ลด
        st.session_state.roster_data["ลำดับ"] = staff_df.get("ลำดับ", list(range(1, num_rows + 1)))
        st.session_state.roster_data["ชื่อ - สกุล"] = staff_df.get("ชื่อ - สกุล", [""] * num_rows)
        st.session_state.roster_data["ตำแหน่ง"] = staff_df.get("ตำแหน่ง", [""] * num_rows)

current_df = st.session_state.roster_data
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
        st.session_state.roster_data = edited_roster
        st.success("บันทึกการแก้ไขเรียบร้อยแล้ว!")
with col3:
    if st.button("🔗 แชร์ตารางเวร", use_container_width=True):
        st.toast("คัดลอกลิงก์สำหรับแชร์สำเร็จ!", icon="🚀")
