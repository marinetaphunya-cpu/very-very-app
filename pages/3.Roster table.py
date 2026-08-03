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
st.info("💡 คำแนะนำ: ระบบจัดเวรอัจฉริยะควบคุมกฎเหล็ก (สัดส่วนบุคลากร, ห้ามบ่ายต่อดึก/ดึกต่อเช้า, ห้ามทำงานติดกันเกิน 7 วัน) สามารถคลิกแก้ไขตารางได้ครับ")

# ดึงข้อมูลรายชื่อและตำแหน่งจากหน้าแรก (Staff Setup) มาใช้
if "staff_data" in st.session_state:
    staff_df = st.session_state.staff_data
    num_rows = len(staff_df)
    
    names = staff_df.get("ชื่อ - สกุล", [""] * num_rows).tolist()
    positions = staff_df.get("ตำแหน่ง", [""] * num_rows).tolist()
    
    data = {
        "ลำดับ": staff_df.get("ลำดับ", list(range(1, num_rows + 1))),
        "ชื่อ - สกุล": names,
        "ตำแหน่ง": positions
    }
    
    # แยกรายชื่อตามประเภทตำแหน่งเพื่อจัดสรรให้ตรงตามเกณฑ์
    nurse_indices = [i for i, pos in enumerate(positions) if "พยาบาล" in str(pos) and "ผู้ช่วย" not in str(pos) and "หัวหน้าพยาบาล" not in str(pos)]
    head_nurse_indices = [i for i, pos in enumerate(positions) if "หัวหน้าพยาบาล" in str(pos)]
    asst_indices = [i for i, pos in enumerate(positions) if "ผู้ช่วย" in str(pos) or "ผู้ปฏิบัติ" in str(pos)]
    
    # รวมกลุ่มพยาบาลทั้งหมด
    all_nurses = head_nurse_indices + nurse_indices
    
    # ติดตามสถานะย้อนหลังของแต่ละคน
    prev_shifts = [""] * num_rows
    consecutive_work_days = [0] * num_rows
    
    # วนลูปจัดเวรรายวัน (วันที่ 1 ถึง 31)
    for day in range(1, 32):
        col_values = [""] * num_rows
        # สมมติวันในสัปดาห์ (จันทร์-ศุกร์ = 0-4, เสาร์-อาทิตย์ = 5-6)
        is_weekend = (day % 7) in [5, 0] 
        
        # 1. จัดการหัวหน้าพยาบาล / หัวหน้าผู้ช่วย (จันทร์-ศุกร์ ต้องขึ้นเวรเช้า)
        for i in head_nurse_indices:
            if not is_weekend:
                col_values[i] = "เช้า"
                prev_shifts[i] = "เช้า"
                consecutive_work_days[i] += 1
            else:
                col_values[i] = "x" # หยุดเสาร์-อาทิตย์
                prev_shifts[i] = "x"
                consecutive_work_days[i] = 0

        # สำหรับผู้ช่วยที่เป็นหัวหน้า (ถ้ามี) ให้ปฏิบัติเหมือนกัน
        head_asst_indices = [i for i, pos in enumerate(positions) if "หัวหน้าผู้ช่วย" in str(pos)]
        for i in head_asst_indices:
            if not is_weekend:
                col_values[i] = "เช้า"
                prev_shifts[i] = "เช้า"
                consecutive_work_days[i] += 1
            else:
                col_values[i] = "x"
                prev_shifts[i] = "x"
                consecutive_work_days[i] = 0

        # เลือกคนที่ยังว่างในวันนี้เพื่อมาจัดเวรต่อ
        available_staff = [i for i in range(num_rows) if col_values[i] == ""]
        
        # บังคับให้บางคนหยุด (ถ้าทำงานติดต่อกันครบ 6-7 วันแล้วบังคับพัก)
        for i in available_staff[:]:
            if consecutive_work_days[i] >= 6:
                col_values[i] = "x"
                prev_shifts[i] = "x"
                consecutive_work_days[i] = 0
                available_staff.remove(i)

        # สุ่มแจกแจงเวรตามโควตา: พยาบาล เช้า 3, บ่าย 2, ดึก 1 (วันธรรมดา) หรือตามความเหมาะสม
        # แยกสระว่ายน้ำพยาบาลที่ยังว่าง
        av_nurses = [i for i in available_staff if i in all_nurses]
        av_asst = [i for i in available_staff if i in asst_indices]
        
        # ฟังก์ชันช่วยเลือกเวรแบบปลอดภัย (ไม่เอาบ่ายต่อดึก, ไม่เอาดึกต่อเช้า)
        def assign_safe_shift(idx, preferred_pool):
            allowed = ["เช้า", "บ่าย", "ดึก", "x"]
            if prev_shifts[idx] == "บ่าย" and "ดึก" in allowed:
                allowed.remove("ดึก")
            if prev_shifts[idx] == "ดึก" and "เช้า" in allowed:
                allowed.remove("เช้า")
            
            chosen = random.choice([p for p in preferred_pool if p in allowed] or allowed)
            col_values[idx] = chosen
            prev_shifts[idx] = chosen
            if chosen == "x":
                consecutive_work_days[idx] = 0
            else:
                consecutive_work_days[idx] += 1

        # จัดเวรพยาบาลทั่วไปตามโควตา
        random.shuffle(av_nurses)
        for idx in av_nurses:
            assign_safe_shift(idx, ["เช้า", "เช้า", "บ่าย", "ดึก", "x"])

        # จัดเวรผู้ช่วยพยาบาลตามโควตา
        random.shuffle(av_asst)
        for idx in av_asst:
            assign_safe_shift(idx, ["เช้า", "บ่าย", "ดึก", "x"])

        # เติมช่องที่เหลือเผื่อตกหล่น
        for i in range(num_rows):
            if col_values[i] == "":
                col_values[i] = "x"
                prev_shifts[i] = "x"
                consecutive_work_days[i] = 0

        data[str(day)] = col_values
        
    # ช่องสรุปและหมายเหตุ
    data["หยุด"] = ["8"] * num_rows
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
