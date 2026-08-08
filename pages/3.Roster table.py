import streamlit as st
import pandas as pd
import random
import io
from weasyprint import HTML

st.set_page_config(page_title="Very Very - Roster Table", page_icon="📅", layout="wide")

hide_streamlit_style = """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ กรุณาล็อกอินก่อนครับ")
    st.stop()

t_month = st.session_state.get('target_month', 'สิงหาคม')
t_year = st.session_state.get('target_year', 2569)

st.title(f"📅 กำหนดการปฏิบัติงานสำหรับเจ้าหน้าที่พยาบาล เดือน{t_month} พ.ศ. {t_year}")

# --- แถบแสดงคำอธิบายสี (Color Legend) ด้านบนสุด ---
st.markdown("""
    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; font-size: 14px;">
        <span style="background-color: #FFFFFF; border: 1px solid #ccc; padding: 3px 10px; border-radius: 4px; color: #000;"><b>ช</b> = เวรเช้า</span>
        <span style="background-color: #FFF9C4; border: 1px solid #ccc; padding: 3px 10px; border-radius: 4px; color: #000;"><b>บ</b> = เวรบ่าย</span>
        <span style="background-color: #E1BEE7; border: 1px solid #ccc; padding: 3px 10px; border-radius: 4px; color: #000;"><b>ด</b> = เวรดึก</span>
        <span style="background-color: #C8E6C9; border: 1px solid #ccc; padding: 3px 10px; border-radius: 4px; color: #1B5E20;"><b>ป</b> = ประชุม</span>
        <span style="background-color: #B3E5FC; border: 1px solid #ccc; padding: 3px 10px; border-radius: 4px; color: #01579B;"><b>อ</b> = อบรม</span>
        <span style="background-color: #FFCDD2; border: 1px solid #ccc; padding: 3px 10px; border-radius: 4px; color: #B71C1C;"><b>x</b> = วันหยุด</span>
    </div>
""", unsafe_allow_html=True)

def color_coding_shifts(val):
    val_str = str(val).strip()
    if val_str == "ช":
        return 'background-color: #FFFFFF; color: #000000; text-align: center;'
    elif val_str == "บ":
        return 'background-color: #FFF9C4; color: #000000; text-align: center;'
    elif val_str == "ด":
        return 'background-color: #E1BEE7; color: #000000; text-align: center;'
    elif val_str == "ป":
        return 'background-color: #C8E6C9; color: #1B5E20; font-weight: bold; text-align: center;'
    elif val_str == "อ":
        return 'background-color: #B3E5FC; color: #01579B; font-weight: bold; text-align: center;'
    elif val_str.lower() == "x":
        return 'background-color: #FFCDD2; color: #B71C1C; font-weight: bold; text-align: center;'
    return 'text-align: center;'

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

    head_nurse_indices = [i for i, pos in enumerate(positions) if "หัวหน้าพยาบาล" in str(pos)]
    nurse_indices = [i for i, pos in enumerate(positions) if "พยาบาล" in str(pos) and "ผู้ช่วย" not in str(pos) and "หัวหน้าพยาบาล" not in str(pos)]
    head_asst_indices = [i for i, pos in enumerate(positions) if "หัวหน้าผู้ช่วย" in str(pos)]
    asst_indices = [i for i, pos in enumerate(positions) if ("ผู้ช่วย" in str(pos) or "ผู้ปฏิบัติ" in str(pos)) and "หัวหน้าผู้ช่วย" not in str(pos)]

    prev_shifts = [""] * num_rows
    consecutive_work_days = [0] * num_rows

    for day in range(1, 32):
        col_values = [""] * num_rows
        is_weekend = (day % 7) in [5, 0]
        is_meeting_day = (day == 7)
        is_training_day = (day == 14)

        for i in head_nurse_indices + head_asst_indices:
            if is_meeting_day:
                col_values[i] = "ป"
                prev_shifts[i] = "ป"
            elif is_training_day:
                col_values[i] = "อ"
                prev_shifts[i] = "อ"
            elif not is_weekend:
                col_values[i] = "ช"
                prev_shifts[i] = "ช"
                consecutive_work_days[i] += 1
            else:
                col_values[i] = "x"
                prev_shifts[i] = "x"
                consecutive_work_days[i] = 0

        def get_safe_shifts(idx):
            allowed = ["ช", "บ", "ด", "x"]
            if prev_shifts[idx] == "บ":
                if "ด" in allowed: allowed.remove("ด")
            if prev_shifts[idx] == "ด":
                if "ช" in allowed: allowed.remove("ช")
            if consecutive_work_days[idx] >= 6:
                allowed = ["x"]
            return allowed

        needed_n_morning = 3 if not is_weekend else 1
        needed_n_afternoon = 2 if not is_weekend else 1
        needed_n_night = 1

        current_morning_nurses = sum(1 for i in head_nurse_indices if col_values[i] in ["ช", "ป", "อ"])
        remaining_morning_n = max(0, needed_n_morning - current_morning_nurses)

        free_nurses = [i for i in nurse_indices if col_values[i] == ""]
        random.shuffle(free_nurses)

        for _ in range(remaining_morning_n):
            if free_nurses:
                idx = free_nurses.pop(0)
                safe = get_safe_shifts(idx)
                chosen = "ช" if "ช" in safe else random.choice(safe)
                col_values[idx] = chosen
                prev_shifts[idx] = chosen
                consecutive_work_days[idx] = 0 if chosen == "x" else consecutive_work_days[idx] + 1

        for _ in range(needed_n_afternoon):
            if free_nurses:
                idx = free_nurses.pop(0)
                safe = get_safe_shifts(idx)
                chosen = "บ" if "บ" in safe else random.choice(safe)
                col_values[idx] = chosen
                prev_shifts[idx] = chosen
                consecutive_work_days[idx] = 0 if chosen == "x" else consecutive_work_days[idx] + 1

        for _ in range(needed_n_night):
            if free_nurses:
                idx = free_nurses.pop(0)
                safe = get_safe_shifts(idx)
                chosen = "ด" if "ด" in safe else random.choice(safe)
                col_values[idx] = chosen
                prev_shifts[idx] = chosen
                consecutive_work_days[idx] = 0 if chosen == "x" else consecutive_work_days[idx] + 1

        for idx in free_nurses:
            col_values[idx] = "x"
            prev_shifts[idx] = "x"
            consecutive_work_days[idx] = 0

        needed_a_morning = 2 if not is_weekend else 1
        needed_a_afternoon = 1
        needed_a_night = 1

        current_morning_asst = sum(1 for i in head_asst_indices if col_values[i] in ["ช", "ป", "อ"])
        remaining_morning_a = max(0, needed_a_morning - current_morning_asst)

        free_assts = [i for i in (asst_indices + head_asst_indices) if col_values[i] == ""]
        random.shuffle(free_assts)

        for _ in range(remaining_morning_a):
            if free_assts:
                idx = free_assts.pop(0)
                safe = get_safe_shifts(idx)
                chosen = "ช" if "ช" in safe else random.choice(safe)
                col_values[idx] = chosen
                prev_shifts[idx] = chosen
                consecutive_work_days[idx] = 0 if chosen == "x" else consecutive_work_days[idx] + 1

        for _ in range(needed_a_afternoon):
            if free_assts:
                idx = free_assts.pop(0)
                safe = get_safe_shifts(idx)
                chosen = "บ" if "บ" in safe else random.choice(safe)
                col_values[idx] = chosen
                prev_shifts[idx] = chosen
                consecutive_work_days[idx] = 0 if chosen == "x" else consecutive_work_days[idx] + 1

        for _ in range(needed_a_night):
            if free_assts:
                idx = free_assts.pop(0)
                safe = get_safe_shifts(idx)
                chosen = "ด" if "ด" in safe else random.choice(safe)
                col_values[idx] = chosen
                prev_shifts[idx] = chosen
                consecutive_work_days[idx] = 0 if chosen == "x" else consecutive_work_days[idx] + 1

        for idx in free_assts:
            col_values[idx] = "x"
            prev_shifts[idx] = "x"
            consecutive_work_days[idx] = 0

        for i in range(num_rows):
            if col_values[i] == "":
                col_values[i] = "x"
                prev_shifts[i] = "x"
                consecutive_work_days[i] = 0

        data[str(day)] = col_values

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

    # --- แสดงผลตารางบนเว็บ ---
    st.subheader("📊 ตารางเวรปฏิบัติงานประจำเดือน")
    styled_df = current_df.style.map(color_coding_shifts, subset=[str(d) for d in range(1, 32)])
    st.dataframe(styled_df, use_container_width=True, height=500)

    st.markdown("---")
    st.subheader("📝 บันทึกข้อความ / หมายเหตุประจำเดือน")
    note_text = st.text_area("พิมพ์ข้อความชี้แจงเพิ่มเติมหรือบันทึกข้อตกลงในวอร์ด...", placeholder="เช่น บันทึกการประชุมพุธที่ 1 ของเดือน...")

    # --- ฟังก์ชันสร้าง HTML ที่ใช้ร่วมกันทั้งสองแบบ (HTML report / PDF) ---
    def build_html_table(df, month_name, year_val, page_css=""):
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>ตารางเวร เดือน {month_name} {year_val}</title>
            <style>
                {page_css}
                body {{ font-family: 'Tahoma', 'Sarabun', 'Loma', 'Garuda', sans-serif; padding: 20px; }}
                h2 {{ text-align: center; color: #1E3A8A; }}
                table {{ border-collapse: collapse; width: 100%; font-size: 11px; }}
                th, td {{ border: 1px solid #999; padding: 6px; text-align: center; }}
                th {{ background-color: #1E3A8A; color: white; }}
                .shift-ch {{ background-color: #FFFFFF; color: #000; }}
                .shift-b {{ background-color: #FFF9C4; color: #000; }}
                .shift-d {{ background-color: #E1BEE7; color: #000; }}
                .shift-p {{ background-color: #C8E6C9; color: #1B5E20; font-weight: bold; }}
                .shift-o {{ background-color: #B3E5FC; color: #01579B; font-weight: bold; }}
                .shift-x {{ background-color: #FFCDD2; color: #B71C1C; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h2>📅 กำหนดการปฏิบัติงานพยาบาล เดือน{month_name} พ.ศ. {year_val}</h2>
            <table>
                <tr>
        """
        for col in df.columns:
            html_content += f"<th>{col}</th>"
        html_content += "</tr>"

        for _, row in df.iterrows():
            html_content += "<tr>"
            for col_name in df.columns:
                val = str(row[col_name])
                if col_name in [str(d) for d in range(1, 32)]:
                    v_trim = val.strip()
                    if v_trim == "บ": cls = "shift-b"
                    elif v_trim == "ด": cls = "shift-d"
                    elif v_trim == "ป": cls = "shift-p"
                    elif v_trim == "อ": cls = "shift-o"
                    elif v_trim.lower() == "x": cls = "shift-x"
                    else: cls = "shift-ch"
                    html_content += f"<td class='{cls}'>{val}</td>"
                else:
                    html_content += f"<td style='text-align: left;'>{val}</td>"
            html_content += "</tr>"

        html_content += """
            </table>
        </body>
        </html>
        """
        return html_content

    def create_html_report(df, month_name, year_val):
        # ไฟล์ HTML สำหรับเปิดในมือถือ/iPad (ไม่ fix ขนาดหน้ากระดาษ)
        html_content = build_html_table(df, month_name, year_val)
        return io.BytesIO(html_content.encode('utf-8'))

    def create_pdf_report(df, month_name, year_val):
        # ไฟล์ PDF ใช้กระดาษ A3 แนวนอน เพราะคอลัมน์เยอะ (31 วัน + สรุป)
        pdf_css = "@page { size: A3 landscape; margin: 1cm; }"
        html_content = build_html_table(df, month_name, year_val, page_css=pdf_css)
        pdf_bytes = HTML(string=html_content).write_pdf()
        return io.BytesIO(pdf_bytes)

    st.markdown("---")
    col1, col2, col3, col4 = st.columns([3, 3, 3, 3])
    with col1:
        if st.button("⬅️ ย้อนกลับไปหน้าตั้งค่า", use_container_width=True):
            st.switch_page("pages/1.staff setup.py")
    with col2:
        if st.button("💾 บันทึกการแก้ไข", use_container_width=True):
            st.success("บันทึกการแก้ไขเรียบร้อยแล้ว!")
    with col3:
        html_data = create_html_report(current_df, t_month, t_year)
        st.download_button(
            label="📥 ดาวน์โหลด HTML",
            data=html_data,
            file_name=f"roster_{t_month}_{t_year}.html",
            mime="text/html",
            use_container_width=True
        )
    with col4:
        pdf_data = create_pdf_report(current_df, t_month, t_year)
        st.download_button(
            label="📄 ดาวน์โหลด PDF",
            data=pdf_data,
            file_name=f"roster_{t_month}_{t_year}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

else:
    st.warning("⚠️ กรุณากลับไปกรอกรายชื่อที่หน้า Staff Setup ก่อนครับ")
