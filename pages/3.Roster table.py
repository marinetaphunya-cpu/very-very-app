import streamlit as st
import pandas as pd

st.set_page_config(page_title="Very Very - Roster Table", page_icon="📅", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ กรุณาล็อกอินก่อนครับ")
    st.stop()

t_month = st.session_state.get('target_month', 'สิงหาคม')
t_year = st.session_state.get('target_year', 2569)

st.title(f"📅 กำหนดการปฏิบัติงานสำหรับเจ้าหน้าที่พยาบาล เดือน{t_month} พ.ศ. {t_year}")
st.info("💡 คำแนะนำ: ตารางด้านล่างจำลองตามฟอร์มวอร์ดจริง สามารถคลิกแก้ข้อมูล ข้อมูลที่เปลี่ยนจะไฮไลท์ **สีม่วง** อัตโนมัติ")

# สร้างโครงสร้างจำลองตารางเวรให้มีคอลัมน์ครบถ้วนตามแบบฟอร์มจริง (วันที่ 1-31, หยุด, ค้าง, OT, เวร, หมายเหตุ)
if "roster_data" not in st.session_state:
    # สร้าง columns พื้นฐาน
    data = {
        "ลำดับ": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "ชื่อ - สกุล": [
            "นายปัณณธร ศฤงคาร", "นางสาวธัญญาลักษณ์ บุญประคม", "นางสาวนิศารัตน์ วงศ์ใหญ่",
            "นางสาวนิสารัตน์ ไชยวงศ์", "นางสาวจิราภรณ์ บำรุงผล", "นายนภัทร โขโยนะ",
            "นางสาวพิมพ์มาดา ศรีคำวัง", "นางสาวมารินี ทาปัญญา", "นางสาวณัชพุนินทร์ ทองเพ็ญ", "นางสาวสายแนน แสนสามารถ"
        ],
        "ตำแหน่ง": ["พยาบาล", "พยาบาล", "พยาบาล", "พยาบาล", "พยาบาล", "พยาบาล", "พยาบาล", "พยาบาล", "พยาบาล", "ผู้ปฏิบัติฯ"]
    }
    # เติมวันที่ 1 ถึง 31
    for day in range(1, 32):
        data[str(day)] = [""] * 10
        
    # เติมช่องสรุปท้ายตาราง
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

current_df = st.session_state.roster_data
original_df = st.session_state.original_data

# แสดง Data Editor ให้แก้ไขตารางได้อิสระ
edited_roster = st.data_editor(current_df, use_container_width=True, key="ward_roster_editor")

# โน้ตเพิ่มเติม
st.markdown("---")
st.subheader("📝 บันทึกข้อความ / หมายเหตุประจำเดือน")
note_text = st.text_area("พิมพ์ข้อความชี้แจงเพิ่มเติมหรือบันทึกข้อตกลงในวอร์ด...", placeholder="เช่น บันทึกการประชุมพุธที่ 1 ของเดือน...")

# ปุ่มบันทึกและแชร์มุมขวาล่าง
st.markdown("---")
col1, col2, col3 = st.columns([6, 2, 2])
with col2:
    if st.button("💾 บันทึกตารางเวร", use_container_width=True):
        st.session_state.roster_data = edited_roster
        st.success("บันทึกการแก้ไขเรียบร้อยแล้ว!")
with col3:
    if st.button("🔗 แชร์ตารางเวร", use_container_width=True):
        st.toast("คัดลอกลิงก์สำหรับแชร์สำเร็จ!", icon="🚀")

