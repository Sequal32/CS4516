import smtplib
from email.mime.text import MIMEText

USER = "YOUR EMAIL HERE"
TARGET = "RECEIPTIENT EMAIL HERE"
EMAIL_SERVER = "smtp.gmail.com"

with open("passwd", "r") as f:
    passwd = f.read().strip()
    
    msg = MIMEText("Hello world from Python!")
    msg['Subject'] = "Project 1 of CS4516"
    msg['From'] = USER
    msg['To'] = TARGET

    try:
        s = smtplib.SMTP(EMAIL_SERVER, 587)
        print(f"Connecting to {EMAIL_SERVER}")
        s.starttls()
        print(f"Logging in as {USER}")
        s.login(USER, passwd)
        print(f"Sending mail");
        s.sendmail(USER, TARGET, msg.as_string())
        s.quit()
    except Exception as e:
        print(f"Error sending email: {e}")
