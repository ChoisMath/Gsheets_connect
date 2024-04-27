import pandas as pd
import streamlit as st
import gspread as gc
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
import re


# Google Sheets API에 액세스할 수 있는 권한 부여
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('.\.streamlit\chois-python-connect.json', scope) # 'credentials.json'은 본인의 서비스 계정 키 파일입니다.
client = gc.authorize(credentials)

# 스프레드시트 열기
spreadsheet = client.open_by_key('1DwMKa9x9mHZnKUFgylhgQahEoFaTmfHCr4yeCVNVpT4')

# 시트 선택
sheet = spreadsheet.worksheet('sheet1') # 'Sheet1'은 열고자 하는 시트의 이름입니다.
school_sheet = spreadsheet.worksheet('학교')

sheet.update_cell(1, 2, 'Bingo!')
