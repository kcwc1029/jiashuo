import os
from pathlib import Path
from dotenv import load_dotenv
import smtplib
import requests
import yfinance as yf

from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header


### 環境變數
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
env_path = project_root / ".env"

load_dotenv(dotenv_path=env_path)

FromAddress = os.getenv("FromAddress")
AppPassword = os.getenv("AppPassword")


if not FromAddress or not AppPassword:
    print("錯誤：請確認 .env 裡面有 FromAddress 與 AppPassword")
    raise SystemExit


def clean_number(value):
    return float(value.replace(",", "").replace("--", "0"))


def get_tw_stock_data(stock_code):
    today = datetime.today()
    date_text = today.strftime("%Y%m%d")

    url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"

    params = {
        "response": "json",
        "date": date_text,
        "stockNo": stock_code
    }

    response = requests.get(url, params=params)
    result = response.json()

    if "data" not in result or len(result["data"]) < 2:
        return None

    data = result["data"]

    latest = data[-1]
    previous = data[-2]

    latest_date = latest[0]
    volume = clean_number(latest[1])
    open_price = clean_number(latest[3])
    high_price = clean_number(latest[4])
    low_price = clean_number(latest[5])
    close_price = clean_number(latest[6])

    previous_close = clean_number(previous[6])

    return {
        "ticker": stock_code,
        "latest_date": latest_date,
        "open": open_price,
        "high": high_price,
        "low": low_price,
        "close": close_price,
        "volume": volume,
        "previous_close": previous_close
    }


def get_us_stock_data(ticker_symbol):
    try:
        data = yf.download(
            ticker_symbol,
            period="10d",
            interval="1d",
            progress=False,
            auto_adjust=False,
            threads=False
        )
    except Exception as error:
        print("錯誤：yfinance 抓取失敗")
        print(error)
        return None

    if hasattr(data.columns, "nlevels") and data.columns.nlevels > 1:
        data.columns = data.columns.get_level_values(0)

    data = data.dropna()

    if len(data) < 2:
        return None

    latest = data.iloc[-1]
    previous = data.iloc[-2]

    return {
        "ticker": ticker_symbol,
        "latest_date": data.index[-1].strftime("%Y-%m-%d"),
        "open": float(latest["Open"]),
        "high": float(latest["High"]),
        "low": float(latest["Low"]),
        "close": float(latest["Close"]),
        "volume": float(latest["Volume"]),
        "previous_close": float(previous["Close"])
    }


### 使用者輸入
to_address = input("請輸入收件人 Email：").strip()
ticker_symbol = input("請輸入股票或 ETF 代號，例如 2330、006208、0050、NVDA、AAPL：").strip()


if not to_address:
    print("錯誤：收件人 Email 不可以空白")
    raise SystemExit

if not ticker_symbol:
    print("錯誤：股票或 ETF 代號不可以空白")
    raise SystemExit


### 判斷台股或美股
if ticker_symbol.isdigit():
    stock_data = get_tw_stock_data(ticker_symbol)
else:
    stock_data = get_us_stock_data(ticker_symbol)


if stock_data is None:
    print(f"錯誤：查無 {ticker_symbol} 的資料，請確認股票或 ETF 代號是否正確")
    raise SystemExit


### 取出資料
latest_date = stock_data["latest_date"]
open_price = stock_data["open"]
high_price = stock_data["high"]
low_price = stock_data["low"]
close_price = stock_data["close"]
volume = stock_data["volume"]
previous_close = stock_data["previous_close"]

change_amount = close_price - previous_close
change_percent = (change_amount / previous_close) * 100


### 簡單解讀
if change_amount > 0:
    market_comment = "今日收盤價高於前一個交易日，短線表現偏強。"
elif change_amount < 0:
    market_comment = "今日收盤價低於前一個交易日，短線表現偏弱。"
else:
    market_comment = "今日收盤價與前一個交易日相同，股價變動不大。"


if close_price > open_price:
    intraday_comment = "盤中走勢來看，收盤價高於開盤價，代表買盤相對積極。"
elif close_price < open_price:
    intraday_comment = "盤中走勢來看，收盤價低於開盤價，代表賣壓相對明顯。"
else:
    intraday_comment = "盤中走勢來看，開盤價與收盤價相同，整體波動有限。"


### 組合信件
subject = f"【財經觀察報告】{ticker_symbol}"

body = f"""
您好：

以下是您查詢的股票 / ETF 財經觀察報告。

股票或 ETF 代號：{ticker_symbol}
最新交易日期：{latest_date}

開盤價：{open_price:.2f}
最高價：{high_price:.2f}
最低價：{low_price:.2f}
最新收盤價：{close_price:.2f}
成交量：{volume:,.0f}

與前一個交易日相比：
漲跌金額：{change_amount:.2f}
漲跌幅：{change_percent:.2f}%

簡單解讀：
{market_comment}
{intraday_comment}

提醒：
本信件僅供教學練習，不構成投資建議。
"""


msg = MIMEText(body, "plain", "utf-8")
msg["Subject"] = Header(subject, "utf-8")
msg["From"] = FromAddress
msg["To"] = to_address


try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(FromAddress, AppPassword)
        server.sendmail(FromAddress, [to_address], msg.as_string())

except Exception as error:
    print("錯誤：Gmail 寄送失敗")
    print(error)
    raise SystemExit


print(f"財經報告已寄出至：{to_address}")