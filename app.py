import streamlit as st
from timeform_tips import scrape_tips

st.set_page_config(page_title="Timeform Tip Sheet Scraper", layout="centered")
st.title("Timeform Tip Sheet Scraper")

if st.button("Scrape Tomorrow's Tips", type="primary"):
    with st.spinner("Scraping Timeform..."):
        tips = scrape_tips()

    if not tips:
        st.warning("No tips found — the page may not have tomorrow's tips yet.")
    else:
        # Build HTML for display with bold meeting names
        html_lines = []
        for meeting in tips:
            html_lines.append(f"<strong>{meeting['meeting']}</strong>")
            for race in meeting["races"]:
                html_lines.append(f"{race['time']} {race['horse']} {race['odds']}")
            html_lines.append("")
        html_output = "<br>".join(html_lines).strip()
        st.markdown(html_output, unsafe_allow_html=True)

        # Plain text for copy-paste into WordPress
        plain_lines = []
        for meeting in tips:
            plain_lines.append(f"<strong>{meeting['meeting']}</strong>")
            for race in meeting["races"]:
                plain_lines.append(f"{race['time']} {race['horse']} {race['odds']}")
            plain_lines.append("")
        copy_text = "\n".join(plain_lines).strip()

        st.divider()
        st.subheader("Copy for WordPress")
        st.code(copy_text, language="html")
