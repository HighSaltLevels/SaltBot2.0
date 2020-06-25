from email.mime.text import MIMEText
import os
import smtplib

EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]


def send_email(msg):
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.login("swdrummer13", EMAIL_PASSWORD)
    body = "SaltBot crashed!\n" + error_msg
    msg = MIMEText(body)
    msg["Subject"] = "SaltBot Crashed"
    msg["From"] = "Me"
    msg["To"] = "davidgreeson13@gmail.com"
    s.send_message(msg)
    s.quit()
