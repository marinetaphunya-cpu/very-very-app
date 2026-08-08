import streamlit as st
import pandas as pd

# ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Staff & Rules Setup", page_icon="📋", layout="wide")

# --- CSS สำหรับซ่อนแถบเมนู Sidebar ด้านข้างของ Streamlit ---
hide_streamlit_style = """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ตรวจสอบการล็อกอิน
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ กรุณาล็อกอินเข้าสู่ระบบก่อนใช้งานหน้านี้")
    st.stop()

st.title("📋 จัดการรายชื่อบุคลากรและกำหนดเดือนตารางเวร")
st.write("เลือกเดือน/ปีที่ต้องการจัดตาราง พร้อมกำหนดรายชื่อ RN, PN และกฎระเบียบข้อบังคับต่างๆ")

# เลือกเดือนและปี
col_m1, col_m2 = st.columns(2)
with col_m1:
    months_list = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
                   "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    selected_month = st.selectbox("เลือกเดือนสำหรับจัดตารางเวร", months_list, index=7)
with col_m2:
    selected_year = st.selectbox("เลือกปี พ.ศ.", [2569, 2570, 2571], index=0)

st.session_state.target_month = selected_month
st.session_state.target_year = selected_year

st.markdown("---")
st.subheader("👥 รายชื่อบุคลากรและตำแหน่งในวอร์ด")

# ตารางรายชื่อบุคลากร
if "staff_data" not in st.session_state:
    st.session_state.staff_data = pd.DataFrame([
        {"ลำดับ": 1, "ชื่อ - สกุล": "นางสาวA", "ตำแหน่ง": "หัวหน้าพยาบาล"},
        {"ลำดับ": 2, "ชื่อ - สกุล": "นางสาวB", "ตำแหน่ง": "พยาบาล"},
        {"ลำดับ": 3, "ชื่อ - สกุล": "นางสาวC", "ตำแหน่ง": "พยาบาล"},
        {"ลำดับ": 4, "ชื่อ - สกุล": "นางสาวD", "ตำแหน่ง": "พยาบาล"},
        {"ลำดับ": 5, "ชื่อ - สกุล": "นางสาวE", "ตำแหน่ง": "พยาบาล"},
        {"ลำดับ": 6, "ชื่อ - สกุล": "นางสาวF", "ตำแหน่ง": "พยาบาล"},
        {"ลำดับ": 7, "ชื่อ - สกุล": "นางสาวG", "ตำแหน่ง": "พยาบาล"},
        {"ลำดับ": 8, "ชื่อ - สกุล": "นางสาวH", "ตำแหน่ง": "พยาบาล"},
        {"ลำดับ": 9, "ชื่อ - สกุล": "นางสาวI", "ตำแหน่ง": "หัวหน้าผู้ช่วยพยาบาล"},
        {"ลำดับ": 10,"ชื่อ - สกุล": "นางสาวJ", "ตำแหน่ง": "ผู้ช่วยพยาบาล"},
        {"ลำดับ": 11,"ชื่อ - สกุล": "นางสาวK", "ตำแหน่ง": "ผู้ช่วยพยาบาล"},
        {"ลำดับ": 12,"ชื่อ - สกุล": "นางสาวL", "ตำแหน่ง": "ผู้ช่วยพยาบาล"},
        {"ลำดับ": 13,"ชื่อ - สกุล": "นางสาวM", "ตำแหน่ง": "ผู้ช่วยพยาบาล"},
    ])

edited_staff = st.data_editor(st.session_state.staff_data, num_rows="dynamic", use_container_width=True)
st.session_state.staff_data = edited_staff

st.markdown("---")
st.subheader("⚙️ กฎและเงื่อนไขตายตัว (Hard Constraints)")
st.info(
    "📌 **เงื่อนไขบังคับระบบ:**\n"
    "1. **เวลาเวร:** เช้า (08:00 - 16:00), บ่าย (16:00 - 24:00), ดึก (24:00 - 08:00)\n"
    "2. **ลำดับการขึ้นเวร:** ห้ามขึ้น 'บ่ายต่อดึก' และห้ามขึ้น 'ดึกต่อเช้า' (อนุญาตเฉพาะ เช้า→บ่าย หรือ บ่าย→เช้า เท่านั้น)\n"
    "3. **วันหยุด:** พยาบาลและผู้ช่วยทุกคนต้องได้รับวันหยุดอย่างน้อย 1 วัน ทุกๆ 7 วัน"
)

st.checkbox("เชื่อมโยงตารางประชุมคณะกรรมการหอผู้ป่วย (เช่น พุธที่ 1, พุธที่ 2 ของเดือน)", value=True, key="rule_meeting")
st.checkbox("ล็อกหัวหน้าหอผู้ป่วยและหัวหน้าผู้ช่วยขึ้นเวรเช้า จันทร์-ศุกร์", value=True, key="rule_head_morning")
st.checkbox("จำกัดการทำงานติดต่อกันไม่เกิน 7 วัน", value=True, key="rule_max_days")
st.checkbox("พยาบาลเวรเช้า (จ-ศ 3 คน / บ่าย 2 คน / ดึก 1 คน / ส-อ พยาบาล 1 คน)", value=True, key="rule_rn_ratio")
st.checkbox("ผู้ช่วยพยาบาลเวรเช้า (จ-ศ 2 คน / บ่าย 1 คน / ดึก 1 คน / ส-อ ผู้ช่วย 1 คน)", value=True, key="rule_pn_ratio")

st.markdown("---")
st.subheader("📝 เงื่อนไขเพิ่มเติมเฉพาะเดือนนี้ (Soft Constraints / Custom Rules)")
st.text_area(
    "กรอกข้อจำกัดพิเศษ เช่น วันที่มีประชุม, คำขอลาหยุด (Vacation), หรือข้อจำกัดของบุคคล:",
    placeholder="เช่น:\n- วันที่ 10 มีประชุมย่อยช่วงบ่าย\n- นางสาวB ขอลาหยุดวันที่ 15\n- นางสาวC ห้ามขึ้นเวรดึก",
    key="custom_rules"
)

# --- แนบรูปภาพเพิ่มเติม (เช่น รูปใบลา, รูปกระดานเวรที่เขียนมือ) ให้ AI ช่วยอ่านประกอบ ---
st.markdown("##### 📎 แนบรูปภาพประกอบ (ถ้ามี)")
tab_upload, tab_camera = st.tabs(["🖼️ เลือกจากคลังภาพ", "📷 ถ่ายภาพ"])

with tab_upload:
    gallery_files = st.file_uploader(
        "เลือกรูปภาพได้หลายไฟล์ เช่น รูปใบลา, ตารางเวรที่เขียนมือ",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="gallery_uploader"
    )

with tab_camera:
    camera_file = st.camera_input("ถ่ายภาพด้วยกล้อง", key="camera_uploader")

# รวมรูปจากทั้งสองช่องทาง เก็บเป็น bytes ไว้ใน session_state เพื่อส่งต่อให้หน้า AI generate ใช้ร่วมกับ Gemini
combined_images = []
if gallery_files:
    for f in gallery_files:
        combined_images.append({"name": f.name, "bytes": f.getvalue(), "mime": f.type})
if camera_file is not None:
    combined_images.append({"name": "camera_capture.jpg", "bytes": camera_file.getvalue(), "mime": "image/jpeg"})

st.session_state.attached_images = combined_images

if st.session_state.attached_images:
    st.caption(f"แนบรูปภาพแล้ว {len(st.session_state.attached_images)} รูป")
    preview_cols = st.columns(min(len(st.session_state.attached_images), 4))
    for i, img in enumerate(st.session_state.attached_images):
        with preview_cols[i % len(preview_cols)]:
            st.image(img["bytes"], use_container_width=True, caption=img["name"])

st.markdown("---")

# บันทึกค่า AI Model ลง session state ไว้ใช้หน้าถัดไป
st.session_state.ai_model_choice = "gemini-2.5-pro"

if st.button("🚀 ยืนยันข้อมูลและไปหน้าจัดเวรอัจฉริยะ", type="primary", use_container_width=True):
    st.switch_page("pages/2.ai generate.py")
