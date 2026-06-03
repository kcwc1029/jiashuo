import os
from pathlib import Path
from dotenv import load_dotenv
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header


### 環境變數
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
env_path = project_root / ".env"

load_dotenv(dotenv_path=env_path)


### 讀取環境變數
AppPassword = os.getenv("AppPassword")
FromAddress = os.getenv("FromAddress")
ToAddress = os.getenv("ToAddress")


### 郵件設定
subject = "【課程即將上課通知】"

text_content = """
您好：

附件為本次課程講義 PDF，
請記得提前下載與閱讀。

謝謝。
"""


### PDF 路徑
pdf_path = project_root / "Gmail_datasets" / "產業新尖兵計畫-1120701.pdf"

### 建立郵件
msg = MIMEMultipart()

msg["Subject"] = Header(subject, "utf-8")
msg["From"] = FromAddress
msg["To"] = ToAddress


### 加入純文字內容
msg.attach(MIMEText(text_content, "plain", "utf-8"))


### 加入 PDF 附件
with open(pdf_path, "rb") as file:

    pdf_file = MIMEApplication(file.read())

    pdf_file.add_header(
        "Content-Disposition",
        "attachment",
        filename=("utf-8", "", pdf_path.name)
    )

    msg.attach(pdf_file)


### 收件人
all_recipients = [ToAddress]


### 寄送郵件
with smtplib.SMTP("smtp.gmail.com", 587) as server:

    server.ehlo()
    server.starttls()

    server.login(FromAddress, AppPassword)

    server.sendmail(
        FromAddress,
        all_recipients,
        msg.as_string()
    )

print("郵件已寄出！")