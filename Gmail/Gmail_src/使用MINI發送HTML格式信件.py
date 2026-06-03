import os
import smtplib
from pathlib import Path
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr


current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

AppPassword = os.getenv("AppPassword")
LoginEmail = os.getenv("LoginEmail")
FromAddress = os.getenv("FromAddress")
ToAddress = os.getenv("ToAddress")

subject = "【課程即將上課通知】"
cc_user = ""
bcc_user = ""

html_body = """
<div style="font-family:Arial, 'Microsoft JhengHei', sans-serif; color:#333333; line-height:1.8; font-size:16px;">
  <p>您好：</p>

  <p>
    向您說明與確認下週的行程安排，以下為下週的會議時間與我的請假規劃：
  </p>

  <p>
    <strong>下週三 ([日期])：</strong>預計參與 [會議A名稱]。
  </p>

  <p>
    <strong>下週四 ([日期])：</strong>預計參與 [會議B名稱]。
  </p>

  <p>
    <strong>下週五 ([日期])：</strong>因 [請假事由，例如：個人私事 / 家庭安排]，預計請假一天。
  </p>

  <p style="background-color:#fff7ed; border-left:4px solid #f97316; padding:12px 14px;">
    請假當天的業務工作我會提前處理完畢。若當天有緊急突發狀況，我仍會保持手機暢通，或您可以直接聯絡代理人 [代理人名字]，我已與他完成相關業務的交接。
  </p>

  <p>
    以上行程與請假申請，再請您撥冗核准，謝謝！
  </p>

  <p>
    祝 順心
  </p>
</div>
"""

msg = MIMEText(html_body, "html", "utf-8")
msg["Subject"] = Header(subject, "utf-8")
msg["From"] = formataddr(("課程通知", FromAddress))
msg["To"] = ToAddress

all_recipients = [ToAddress]

if cc_user:
    msg["Cc"] = cc_user
    all_recipients.append(cc_user)

if bcc_user:
    all_recipients.append(bcc_user)

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.ehlo()
    server.starttls()
    server.login(LoginEmail, AppPassword)
    server.sendmail(FromAddress, all_recipients, msg.as_string())

print("郵件已寄出！")