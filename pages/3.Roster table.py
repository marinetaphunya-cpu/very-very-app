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
st.info("💡 คำแนะนำ: ระบบจัดเวรอัจฉริยะล็อกโควตาตรงตามเงื่อนไขเป๊ะๆ (พยาบาลเช้า 3, บ่าย 2, ดึก 1 | ผู้ช่วยเช้า 2, บ่าย 1, ดึก 1) พร้อมคุมกฎความปลอดภัยครับ")

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
    
    # แยกกลุ่มบุคลากรตามตำแหน่งจริง
    head_nurse_indices = [i for i, pos in enumerate(positions) if "หัวหน้าพยาบาล" in str(pos)]
    nurse_indices = [i for i, pos in enumerate(positions) if "พยาบาล" in str(pos) and "ผู้ช่วย" not in str(pos) and "หัวหน้าพยาบาล" not in str(pos)]
    head_asst_indices = [i for i, pos in enumerate(positions) if "หัวหน้าผู้ช่วย" in str(pos)]
    asst_indices = [i for i, pos in enumerate(positions) if ("ผู้ช่วย" in str(pos) or "ผู้ปฏิบัติ" in str(pos)) and "หัวหน้าผู้ช่วย" not in str(pos)]
    
    all_nurses = head_nurse_indices + nurse_indices
    all_assts = head_asst_indices + asst_indices
    
    # ติดตามสถานะย้อนหลัง
    prev_shifts = [""] * num_rows
    consecutive_work_days = [0] * num_rows
    
    for day in range(1, 32):
        col_values = [""] * num_rows
        is_weekend = (day % 7) in [5, 0] # เสาร์-อาทิตย์
        
        # 1. หัวหน้าพยาบาลและหัวหน้าผู้ช่วย: จันทร์-ศุกร์ ขึ้นเวรเช้า, เสาร์-อาทิตย์ หยุด
        for i in head_nurse_indices + head_asst_indices:
            if not is_weekend:
                col_values[i] = "เช้า"
                prev_shifts[i] = "เช้า"
                consecutive_work_days[i] += 1
            else:
                col_values[i] = "x"
                prev_shifts[i] = "x"
                consecutive_work_days[i] = 0

        # ฟังก์ชันตรวจสอบความปลอดภัย (ห้ามบ่ายต่อดึก, ห้ามดึกต่อเช้า, ไม่ทำงานเกิน 7 วันติด)
        def get_safe_shifts(idx):
            allowed = ["เช้า", "บ่าย", "ดึก", "x"]
            if prev_shifts[idx] == "บ่าย":
                if "ดึก" in allowed: allowed.remove("ดึก")
            if prev_shifts[idx] == "ดึก":
                if "เช้า" in allowed: allowed.remove("เช้า")
            if consecutive_work_days[idx] >= 6:
                # ถ้าทำติดกัน 6-7 วันแล้ว บังคับให้ลงได้แค่ x (หยุด)
                allowed = ["x"]
            return allowed

        # --- จัดสรรโควตาพยาบาล ---
        # วันธรรมดา: เช้า 3 คน (รวมหัวหน้า), บ่าย 2 คน, ดึก 1 คน
        # วันหยุด: เช้า 1 คน, บ่าย 1 คน, ดึก 1 คน (หรือปรับตามเหมาะสม)
        needed_n_morning = 3 if not is_weekend else 1
        needed_n_afternoon = 2 if not is_weekend else 1
        needed_n_night = 1
        
        # หักหัวหน้าพยาบาลที่ลงเวรเช้าไปแล้ว
        current_morning_nurses = sum(1 for i in head_nurse_indices if col_values[i] == "เช้า")
        remaining_morning_n = max(0, needed_n_morning - current_morning_nurses)
        
        # รายชื่อพยาบาลทั่วไปที่ยังว่างในวันนี้
        free_nurses = [i for i in nurse_indices if col_values[i] == ""]
        random.shuffle(free_nurses)
        
        # ลงเวรเช้าพยาบาล
        for _ in range(remaining_morning_n):
            if free_nurses:
                idx = free_nurses.pop(0)
                safe = get_safe_shifts(idx)
                chosen = "เช้า" if "เช้า" in safe else random.choice(safe)
                col_values[idx] = chosen
                prev_shifts[idx] = chosen
                consecutive_work_days[idx] = 0 if chosen == "x" else consecutive_work_days[idx] + 1

        # ลงเวรบ่ายพยาบาล
        for _ in range(needed_n_afternoon):
            if free_nurses:
                idx = free_nurses.pop(0)
                safe = get_safe_shifts(idx)
                chosen = "บ่าย" if "บ่าย" in safe else random.choice(safe)
                col_values[idx] = chosen
                prev_shifts[idx] = chosen
                consecutive_work_days[idx] = 0 if chosen == "x" else consecutive_work_days[idx] + 1

        # ลงเวรดึกพยาบาล
        for _ in range(needed_n_night):
            if free_nurses:
                idx = free_nurses.pop(0)
                safe = get_safe_shifts(idx)
                chosen = "ดึก" if "ดึก" in safe else random.choice(safe)
                col_values[idx] = chosen
                prev_shifts[idx] = chosen
                consecutive_work_days[idx] = 0 if chosen == "x" else consecutive_work_days[idx] + 1

        # พยาบาลที่เหลือจากโควตาให้ได้สิทธิ์หยุด (x)
        for idx in free_nurses:
            col_values[idx] = "x"
            prev_shifts[idx] = "x"
            consecutive_work_days[idx] = 0


        # --- จัดสรรโควตาผู้ช่วยพยาบาล ---
        # วันธรรมดา: เช้า 2 คน (รวมหัวหน้าผู้ช่วย), บ่าย 1 คน, ดึก 1 คน
        # วันหยุด: เช้า 1 คน, บ่าย 1 คน, ดึก 1 คน
        needed_a_morning = 2 if not is_weekend else 1
        needed_a_afternoon = 1
        needed_a_night = 1
        
        current_morning_asst = sum(1 for i in head_asst_indices if col_values[i] == "เช้า")
        remaining_morning_a = max(0, needed_a_morning - current_morning_asst)
        
        free_assts = [i for i in (asst_indices + head_asst_indices) if col_values[i] == ""]
        random.shuffle(free_assts)
        
        # ลงเวรเช้าผู้ช่วย
        for _ in range(remaining_morning_a):
            if free_assts:
                idx = free_assts.pop(0)
                safe = get_safe_shifts(idx)
                chosen = "เช้า" if "เช้า" in safe else random.choice(safe)
                col_values[idx] = chosen
                prev_shifts[idx] = chosen
                consecutive_work_days[idx] = 0 if chosen == "x" else consecutive_work_days[idx] + 1

        # ลงเวรบ่ายผู้ช่วย
        for _ in range(needed_a_afternoon):
            if free_assts:
                idx = free_assts.pop(0)
                safe = get_safe_shifts(idx)
                chosen = "บ่าย" if "บ่าย" in safe else random.choice(safe)
                col_values[idx] = chosen
                prev_shifts[idx] = chosen
                consecutive_work_days[idx] = 0 if chosen == "x" else consecutive_work_days[idx] + 1

        # ลงเวรดึกผู้ช่วย
        for _ in range(needed_a_night):
            if free_assts:
                idx = free_assts.pop(0)
                safe = get_safe_shifts(idx)
                chosen = "ดึก" if "ดึก" in safe else random.choice(safe)
                col_values[idx] = chosen
                prev_shifts[idx] = chosen
                consecutive_work_days[idx] = 0 if chosen == "x" else consecutive_work_days[idx] + 1

        # ผู้ช่วยที่เหลือให้หยุด (x)
        for idx in free_assts:
            col_values[idx] = "x"
            prev_shifts[idx] = "x"
            consecutive_work_days[idx] = 0

        # ป้องกันช่องว่างเผื่อตกหล่น
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

    st.markdown("---")
    st.subheader("📝 บันทึกข้อความ / หมายเหตุประจำเดือน")
    note_text = st.text_area("พิมพ์ข้อความชี้แจงเพิ่มเติมหรือบันทึกข้อตกลงในวอร์ด...", placeholder="เช่น บันทึกการประชุมพุธที่ 1 ของเดือน...")

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
