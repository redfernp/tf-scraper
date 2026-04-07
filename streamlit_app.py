import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
        # Build HTML for display and WordPress copy-paste
        html_lines = []
        for meeting in tips:
            html_lines.append(f"<strong>{meeting['meeting'].upper()}</strong>")
            for race in meeting["races"]:
                html_lines.append(f"{race['time']} {race['horse']} {race['odds']}")
            html_lines.append("")
        html_output = "<br>".join(html_lines).strip()
        copy_text = "\n".join(html_lines).strip()

        st.markdown(html_output, unsafe_allow_html=True)

        st.divider()
        st.subheader("Copy for WordPress")
        st.code(copy_text, language="html")

        # Send email
        try:
            app_password = st.secrets["GMAIL_APP_PASSWORD"]
            email_from = st.secrets["EMAIL_FROM"]
            email_to = st.secrets["EMAIL_TO"]
        except (KeyError, FileNotFoundError):
            app_password = email_from = email_to = ""

        if app_password and email_from and email_to:
            with st.spinner("Sending email..."):
                msg = MIMEMultipart("alternative")
                msg["Subject"] = "Timeform C4 + Irish Tips"
                msg["From"] = email_from
                msg["To"] = email_to

                # Plain text version
                plain_lines = []
                for meeting in tips:
                    plain_lines.append(meeting["meeting"].upper())
                    for race in meeting["races"]:
                        plain_lines.append(f"{race['time']} {race['horse']} {race['odds']}")
                    plain_lines.append("")
                plain_text = "\n".join(plain_lines).strip()
                msg.attach(MIMEText(plain_text, "plain"))

                # HTML version with bold meeting names
                msg.attach(MIMEText(html_output, "html"))

                try:
                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login(email_from, app_password)
                        server.sendmail(email_from, email_to.split(","), msg.as_string())
                    st.success("Email sent to jpredfern1979@gmail.com and hushrc@gmail.com")
                except Exception as e:
                    st.error(f"Failed to send email: {e}")
        else:
            st.warning("Email credentials not configured in .streamlit/secrets.toml")
