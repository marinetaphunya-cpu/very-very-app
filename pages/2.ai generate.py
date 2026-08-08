import streamlit as st
import json
import calendar
import pandas as pd
from google import genai
from google.genai import types

st.set_page_config(page_title="AI Generating Roster", page_icon="⏳", layout="centered")

hide_streamlit_style = """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ กรุณาล็อกอินก่อนครับ")
    st.stop()

if "staff_data" not in st.session_state:
    st.warning("⚠️ กรุณากลับไปกรอกรายชื่อที่หน้า Staff Setup ก่อนครับ")
    st.stop()

target_month = st.session_state.get('target_month', 'สิงหาคม')
target_year = st.session_state.get('target_year', 2569)

months_list = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
               "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
month_index = months_list.index(target_month) + 1
greg_year = target_year - 543  # แปลง พ.ศ. เป็น ค.ศ. เพื่อคำนวณจำนวนวันในเดือนจริง
days_in_month = calendar.monthrange(greg_year, month_index)[1]
st.session_state.days_in_month = days_in_month

st.title("⏳ AI กำลังประมวลผลจัดตารางเวร...")
st.write(f"กำลังจัดตารางเวรสำหรับ **เดือน{target_month} พ.ศ. {target_year}** ({days_in_month} วัน)")

# --- เตรียมข้อมูลบุคลากร ---
staff_df = st.session_state.staff_data
num_rows = len(staff_df)
names = staff_df.get("ชื่อ - สกุล", [""] * num_rows).tolist()
positions = staff_df.get("ตำแหน่ง", [""] * num_rows).tolist()
orders = staff_df.get("ลำดับ", list(range(1, num_rows + 1))).tolist()

# --- รวมกฎตายตัวตามที่ติ๊กเลือกไว้ในหน้า Staff Setup ---
hard_rules = [
    "เวลาเวร: เช้า (08:00-16:00), บ่าย (16:00-24:00), ดึก (24:00-08:00)",
    "ห้ามขึ้นเวร 'บ่ายต่อดึก' และห้ามขึ้นเวร 'ดึกต่อเช้า' อนุญาตเฉพาะ เช้า→บ่าย หรือ บ่าย→เช้า เท่านั้น",
    "พนักงานทุกคนต้องได้รับวันหยุดอย่างน้อย 1 วัน ทุกๆ 7 วัน และห้ามทำงานติดต่อกันเกิน 6 วันโดยไม่มีวันหยุดคั่น",
]
if st.session_state.get("rule_meeting"):
    hard_rules.append("เชื่อมโยงตารางประชุมคณะกรรมการหอผู้ป่วยกับวันพุธสัปดาห์ที่ 1 และ 2 ของเดือน (ใช้รหัส 'ป')")
if st.session_state.get("rule_head_morning"):
    hard_rules.append("หัวหน้าพยาบาลและหัวหน้าผู้ช่วยพยาบาลขึ้นเวรเช้าทุกวันจันทร์-ศุกร์ (รหัส 'ช') ยกเว้นวันประชุม/อบรม")
if st.session_state.get("rule_max_days"):
    hard_rules.append("ห้ามพนักงานคนใดทำงานติดต่อกันเกิน 7 วันโดยไม่มีวันหยุดคั่น")
if st.session_state.get("rule_rn_ratio"):
    hard_rules.append("อัตรากำลังพยาบาล: จันทร์-ศุกร์ เช้า 3 คน / บ่าย 2 คน / ดึก 1 คน, เสาร์-อาทิตย์ เวรละ 1 คน")
if st.session_state.get("rule_pn_ratio"):
    hard_rules.append("อัตรากำลังผู้ช่วยพยาบาล: จันทร์-ศุกร์ เช้า 2 คน / บ่าย 1 คน / ดึก 1 คน, เสาร์-อาทิตย์ เวรละ 1 คน")

custom_rules_text = st.session_state.get("custom_rules", "").strip()
attached_images = st.session_state.get("attached_images", [])

staff_lines = "\n".join(f"{o}. {n} — ตำแหน่ง: {p}" for o, n, p in zip(orders, names, positions))

prompt_text = f"""
คุณคือระบบจัดตารางเวรพยาบาลมืออาชีพ กรุณาจัดตารางเวรเดือน{target_month} พ.ศ. {target_year} ({days_in_month} วัน)

รายชื่อบุคลากร:
{staff_lines}

กฎตายตัวที่ต้องปฏิบัติตามอย่างเคร่งครัด (Hard Constraints ห้ามละเมิดเด็ดขาด):
{chr(10).join(f"- {r}" for r in hard_rules)}

รหัสเวรที่ใช้ได้เท่านั้น: "ช"=เช้า, "บ"=บ่าย, "ด"=ดึก, "ป"=ประชุม, "อ"=อบรม, "x"=วันหยุด

เงื่อนไขเพิ่มเติมเฉพาะเดือนนี้ที่ผู้ใช้พิมพ์มา (Soft Constraints — สำคัญรองจาก Hard Constraints เท่านั้น):
{custom_rules_text if custom_rules_text else "(ไม่มี)"}

หากมีรูปภาพแนบมาด้วย (เช่น ใบลา, บันทึกลายมือ, ตารางเวรเดิม) ให้อ่านและตีความเนื้อหาในภาพเป็นเงื่อนไขเพิ่มเติม แล้วนำมาพิจารณาร่วมกับเงื่อนไขข้างต้นด้วย

ข้อกำหนดผลลัพธ์:
- วันหยุดของแต่ละคนต้องกระจายอย่างสมเหตุสมผล ห้ามติดกันเกินความจำเป็นและห้ามขัดกับ Hard Constraints
- นับจำนวนเวรดึก/เวรบ่าย/วันหยุด/OT ของแต่ละคนให้ตรงกับที่จัดจริงในตาราง (นับจากข้อมูลที่คุณจัดเอง อย่าเดา)
- ส่งคืนเฉพาะ JSON ตาม schema ที่กำหนดเท่านั้น โดยคีย์ในเวรรายวันคือเลขวันที่ "1" ถึง "{days_in_month}"
"""

roster_schema = {
    "type": "object",
    "properties": {
        "roster": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ลำดับ": {"type": "integer"},
                    "ชื่อ - สกุล": {"type": "string"},
                    "ตำแหน่ง": {"type": "string"},
                    "เวรรายวัน": {
                        "type": "object",
                        "description": "คีย์คือเลขวันที่แบบสตริง เช่น '1', '2' ค่าคือรหัสเวร",
                        "additionalProperties": {"type": "string"}
                    },
                    "ค้าง": {"type": "integer"},
                    "ot_เช้า": {"type": "integer"},
                    "ot_บ่าย": {"type": "integer"},
                    "ot_ดึก": {"type": "integer"},
                    "หมายเหตุ": {"type": "string"}
                },
                "required": ["ลำดับ", "ชื่อ - สกุล", "ตำแหน่ง", "เวรรายวัน"]
            }
        }
    },
    "required": ["roster"]
}

with st.status("กำลังวิเคราะห์ข้อมูลด้วย Gemini AI...", expanded=True) as status:
    st.write("🔍 ตรวจสอบรายชื่อบุคลากรและตำแหน่งตามวอร์ด...")
    st.write("⚖️ วิเคราะห์กฎตายตัวและเงื่อนไขเพิ่มเติม (Soft Constraints)...")
    if attached_images:
        st.write(f"🖼️ อ่านรูปภาพที่แนบมา {len(attached_images)} รูปประกอบการวิเคราะห์...")

    if "MY_API_KEY" not in st.secrets:
        status.update(label="❌ ไม่พบ API Key", state="error", expanded=True)
        st.error("ไม่พบ st.secrets['MY_API_KEY'] กรุณาตั้งค่าใน Streamlit Cloud ก่อนใช้งาน")
        st.stop()

    try:
        client = genai.Client(api_key=st.secrets["MY_API_KEY"])

        contents = [prompt_text]
        for img in attached_images:
            contents.append(
                types.Part.from_bytes(data=img["bytes"], mime_type=img.get("mime") or "image/jpeg")
            )

        st.write("🤖 กำลังสั่งการ Gemini 3.1 Flash ประมวลผลตารางเวรตามอัตรากำลัง...")
        response = client.models.generate_content(
            model="gemini-3.1-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=roster_schema,
                temperature=0.3,
            ),
        )

        result = json.loads(response.text)

        st.write("🛡️ ตรวจสอบเงื่อนไขความปลอดภัย (ห้ามบ่ายต่อดึก และห้ามดึกต่อเช้า)...")
        st.write("✨ ตรวจนับวันหยุด / เวรดึก / เวรบ่าย / OT ของแต่ละคน...")

        data = {"ลำดับ": [], "ชื่อ - สกุล": [], "ตำแหน่ง": []}
        for d in range(1, days_in_month + 1):
            data[str(d)] = []
        data["หยุด"] = []
        data["ค้าง"] = []
        data["OT_ด"] = []
        data["OT_ช"] = []
        data["OT_บ"] = []
        data["เวร_ด"] = []
        data["เวร_บ"] = []
        data["หมายเหตุ"] = []

        for person in result.get("roster", []):
            shifts = person.get("เวรรายวัน", {})
            data["ลำดับ"].append(person.get("ลำดับ", ""))
            data["ชื่อ - สกุล"].append(person.get("ชื่อ - สกุล", ""))
            data["ตำแหน่ง"].append(person.get("ตำแหน่ง", ""))

            day_values = []
            for d in range(1, days_in_month + 1):
                val = str(shifts.get(str(d), "x")).strip()
                data[str(d)].append(val)
                day_values.append(val)

            # นับจำนวนจริงจากตารางที่ AI จัด แทนการเชื่อค่าตัวเลขที่โมเดลบอกมาเฉยๆ
            data["หยุด"].append(str(day_values.count("x")))
            data["เวร_ด"].append(str(day_values.count("ด")))
            data["เวร_บ"].append(str(day_values.count("บ")))
            data["ค้าง"].append(str(person.get("ค้าง", 0)))
            data["OT_ช"].append(str(person.get("ot_เช้า", 0)))
            data["OT_บ"].append(str(person.get("ot_บ่าย", 0)))
            data["OT_ด"].append(str(person.get("ot_ดึก", 0)))
            data["หมายเหตุ"].append(person.get("หมายเหตุ", ""))

        st.session_state.roster_data = pd.DataFrame(data)
        st.session_state.original_data = st.session_state.roster_data.copy()

        status.update(label="✨ จัดตารางเวรเสร็จสมบูรณ์แล้ว!", state="complete", expanded=False)

    except Exception as e:
        status.update(label="❌ เกิดข้อผิดพลาดระหว่างประมวลผล", state="error", expanded=True)
        st.error(f"ไม่สามารถจัดตารางเวรได้: {e}")
        st.stop()

st.success("🎉 ตารางเวรพร้อมแล้ว! (จัดโดย AI ตามเงื่อนไขและรูปภาพที่แนบ)")

if st.button("👉 ไปดูตารางเวรประจำเดือน", type="primary", use_container_width=True):
    st.switch_page("pages/3.Roster table.py")
