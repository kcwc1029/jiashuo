import os
from pathlib import Path
from dotenv import load_dotenv
import smtplib
import csv
import time

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


### 寄件人名稱
senderName = "專屬行銷團隊"


### CSV 路徑
csv_path = project_root / "Gmail_datasets" / "customers.csv"


### PDF 路徑
pdf_path = project_root / "Gmail_datasets" / "產業新尖兵計畫-1120701.pdf"


### 建立與 SMTP 伺服器的連線
with smtplib.SMTP("smtp.gmail.com", 587) as server:

    server.ehlo()
    server.starttls()

    server.login(FromAddress, AppPassword)

    ### 開啟並讀取 CSV 檔案
    with open(csv_path, mode="r", encoding="utf-8-sig", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            customer_name = row["姓名"]
            gender = row["性別"]
            customer_email = row["信箱"]
            product = row["購買商品"]

            ### 自動判斷稱謂
            title = "先生" if gender.upper() == "M" else "小姐"

            ### 客製化信件
            subject = f"【專屬通知】感謝您購買 {product}"

            text_content = f"""親愛的 {customer_name} {title} 您好：

感謝您近期選購我們的【{product}】。

附件為本次課程講義 PDF，
請記得提前下載與閱讀。

祝您順心
{senderName} 敬上
"""

            ### 建立郵件
            msg = MIMEMultipart()

            msg["Subject"] = Header(subject, "utf-8")
            msg["From"] = Header(f"{senderName} <{FromAddress}>", "utf-8")
            msg["To"] = customer_email

            ### 加入純文字內容
            msg.attach(MIMEText(text_content, "plain", "utf-8"))

            ### 加入 PDF 附件
            with open(pdf_path, "rb") as pdf_file:

                attachment = MIMEApplication(pdf_file.read())

                attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=("utf-8", "", pdf_path.name)
                )

                msg.attach(attachment)

            ### 寄送郵件
            server.sendmail(
                FromAddress,
                [customer_email],
                msg.as_string()
            )

            print(f"已成功發送客製化信件至：{customer_name} ({customer_email})")

            time.sleep(1)


print("所有客製化信件發送完畢！")