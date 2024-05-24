import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

import gspread
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

credental_json = {
    "type": "service_account",
    "project_id": "chois-python-connect",
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"],
    "client_email": st.secrets["client_email"],
    "client_id": "116464278440047112678",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/chois-python-connect%40chois-python-connect.iam.gserviceaccount.com",
}

# Set up the connection to Google Sheets
# Google Sheets 및 Drive 서비스 설정
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_info(credental_json, scopes=scope)
client = gspread.authorize(credentials)
service = build('drive', 'v3', credentials=credentials)

def get_pdfdata_from_sheet(using_spreadsheet_id, gid):
    """Google Sheets에서 PDF 데이터를 가져오는 함수"""
    url = f"https://docs.google.com/spreadsheets/d/{using_spreadsheet_id}/export?exportFormat=pdf&gid={gid}"
    response = service._http.request(url)
    if response[0].status != 200:
        raise Exception(f"Failed to fetch PDF: {response[0].status}")
    pdf_data = response[1]
    return pdf_data

def send_mail(pdf_data, fromaddr, toaddr, school_name, name):
    """이메일 발송 함수"""
    if not isinstance(toaddr, str):
        raise ValueError("The email address must be a string.")

    msg = MIMEMultipart('alternative')
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = Header(f"{school_name} {name}학생의 대구수학페스티벌 이수증", 'utf-8')

    part = MIMEBase('application', "octet-stream")
    part.set_payload(pdf_data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=f"{school_name}_{name}.pdf")
    msg.attach(part)

    # 이메일 발송
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, st.secrets["email_secret"])
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()
