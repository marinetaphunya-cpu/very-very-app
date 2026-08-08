import streamlit as st
import pandas as pd
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
days_in_month = st.session_state.get('days_in_month', 31)

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

# --- ใช้ตารางที่ AI จัดมาจากหน้า "2.ai generate.py" โดยตรง ไม่สุ่มสร้างใหม่อีกต่อไป ---
if "roster_data" in st.session_state:
    current_df = st.session_state.roster_data
    day_cols = [str(d) for d in range(1, days_in_month + 1)]
    day_cols_present = [c for c in day_cols if c in current_df.columns]

    if "original_data" not in st.session_state:
        st.session_state.original_data = current_df.copy()

    st.subheader("📊 ตารางเวรปฏิบัติงานประจำเดือน (จัดโดย AI ตามเงื่อนไขและรูปภาพที่แนบ)")
    styled_df = current_df.style.map(color_coding_shifts, subset=day_cols_present)
    st.dataframe(styled_df, use_container_width=True, height=500)

    st.markdown("---")
    st.subheader("📝 บันทึกข้อความ / หมายเหตุประจำเดือน")
    note_text = st.text_area("พิมพ์ข้อความชี้แจงเพิ่มเติมหรือบันทึกข้อตกลงในวอร์ด...", placeholder="เช่น บันทึกการประชุมพุธที่ 1 ของเดือน...")

    # --- ฟังก์ชันสร้าง HTML ที่ใช้ร่วมกันทั้งไฟล์ HTML และ PDF ---
    def build_html_table(df, month_name, year_val, day_cols, page_css=""):
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
                if col_name in day_cols:
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

        html_content += "</table></body></html>"
        return html_content

    def create_html_report(df, month_name, year_val, day_cols):
        html_content = build_html_table(df, month_name, year_val, day_cols)
        return io.BytesIO(html_content.encode('utf-8'))

    def create_pdf_report(df, month_name, year_val, day_cols):
        # ใช้ A3 แนวนอนเพราะคอลัมน์เยอะ (สูงสุด 31 วัน + สรุป)
        pdf_css = "@page { size: A3 landscape; margin: 1cm; }"
        html_content = build_html_table(df, month_name, year_val, day_cols, page_css=pdf_css)
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
        html_data = create_html_report(current_df, t_month, t_year, day_cols_present)
        st.download_button(
            label="📥 ดาวน์โหลด HTML",
            data=html_data,
            file_name=f"roster_{t_month}_{t_year}.html",
            mime="text/html",
            use_container_width=True
        )
    with col4:
        pdf_data = create_pdf_report(current_df, t_month, t_year, day_cols_present)
        st.download_button(
            label="📄 ดาวน์โหลด PDF",
            data=pdf_data,
            file_name=f"roster_{t_month}_{t_year}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

else:
    st.warning("⚠️ ยังไม่มีข้อมูลตารางเวร กรุณากลับไปให้ AI จัดตารางที่หน้าก่อนหน้าก่อนครับ")
