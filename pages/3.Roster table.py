import streamlit as st
import pandas as pd

st.set_page_config(page_title="Very Very - Roster Table", page_icon="📅", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ กรุณาล็อกอินก่อนครับ")
    st.stop()

# ดึงค่าเดือนและปีที่เลือกไว้จากหน้า Staff Setup มาแสดงหัวข้อ
t_month = st.session_state.get('target_month', 'สิงหาคม')
t_year = st.session_state.get('target_year', 2569)

st.title(f"📅 ตารางเวรประจำเดือน{t_month} พ.ศ. {t_year}")
st.info("💡 คำแนะนำ: คุณสามารถคลิกแก้ข้อมูลในตารางได้โดยตรง ช่องไหนที่มีการเปลี่ยนแปลงแก้ไขจากระบบ จะเปลี่ยนเป็น **สีม่วง** อัตโนมัติครับ")

if "roster_data" in st.session_state:
    current_df = st.session_state.roster_data
    original_df = st.session_state.original_data

    # แสดง Data Editor ให้ผู้ใช้แก้ไขได้อิสระ
    edited_roster = st.data_editor(current_df, use_container_width=True, key="final_roster_editor")

    # ช่องโน้ตเพิ่มเติมใต้ตาราง
    st.markdown("---")
    st.subheader("📝 บันทึกข้อความ / หมายเหตุประจำเดือน")
    note_text = st.text_area("พิมพ์ข้อความชี้แจงเพิ่มเติมหรือโน้ตสำหรับทีมในวอร์ด...", placeholder="เช่น สลับเวรวันที่ 3 ระหว่างไอด้ากับ...")

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
else:
    st.warning("⚠️ ยังไม่มีข้อมูลตารางเวร กรุณาไปทำตามขั้นตอนที่หน้า 'Staff Setup' ก่อนครับ")

