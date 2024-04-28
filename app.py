import pandas as pd
import streamlit as st
import gspread as gc
import numpy as np
import os
from google.oauth2 import service_account
import datetime, json
from gspread_formatting import DataValidationRule, BooleanCondition, set_data_validation_for_cell_range

# 서비스 계정 정보
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

# Google Sheets 및 Drive API에 액세스할 수 있는 권한 부여
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

credentials = service_account.Credentials.from_service_account_info(credental_json, scopes=scope)

# gspread 클라이언트 초기화
client = gc.authorize(credentials)

# 스프레드시트 열기
spreadsheet = client.open_by_key('1DwMKa9x9mHZnKUFgylhgQahEoFaTmfHCr4yeCVNVpT4')

# 시트 선택
sheet = spreadsheet.worksheet('sheet1') # 'Sheet1'은 열고자 하는 시트의 이름입니다.
school_sheet = spreadsheet.worksheet('학교')

def data_input(input_list):
    all_data = np.array(sheet.get_all_values())
    last_row = all_data.shape[0]+1
    message = " 학교명: {0}\n 구분: {1}\n 학번: {2}학년 {3}반 {4}번\n 이름: {5}\n 생년월일: {6}\n 행사복: {7}사이즈\n 봉사시간: {8}시간"
    sheet.update(range_name="B" + str(last_row), values=input_list)
    validation_rule = DataValidationRule(
        BooleanCondition('BOOLEAN', ['TRUE', 'FALSE']),  # condition'type' and 'values', defaulting to TRUE/FALSE
        showCustomUi=True)
    set_data_validation_for_cell_range(sheet,"A" + str(last_row), validation_rule)  # inserting checkbox

def main():
    st.title("2024 대수페 신청사이트")
    row1= st.columns(5)
    school_name = row1[0].text_input("학교명")   #selectbox로 변경
    teacher_stu = row1[1].selectbox(label = "구분",options = ["교사","참여학생","체험학생"], key="teacher_stu" )
    grade_num = row1[2].number_input("학년", min_value=0, max_value=6, value=0)
    student_ban = row1[3].number_input("반", step=1, min_value=0, max_value=15, value=0, placeholder="선생님은 o반")
    student_id = row1[4].number_input("번호", step=1, min_value=0, max_value=40, value=0, placeholder="선생님은 o번")


    row2 = st.columns(4)
    student_name = row2[0].text_input("이름")
    birthdate = row2[1].date_input("생년월일", datetime.date(2007, 1, 1))
    json_birth = json.dumps(birthdate, default=str).strip("\"")
    size = row2[2].selectbox(label="행사복 사이즈", options = ["xxxL", "xxL", "xL", "L", "M", "S", "xS", "xxS", "xxxS", "해당없음"])
    volunteer = row2[3].number_input(label="봉사시간", step=1, min_value=0, max_value=8)

    input_list = [[school_name, teacher_stu, grade_num, student_ban, student_id, student_name, json_birth, size, volunteer]]

    explain_toggle = st.toggle("항목별 설명")
    if explain_toggle:
        st.markdown("**학교명**: 정확한 명칭을 입력하세요.")
        st.markdown(
            """**구분**:  
             - 교사-동아리 및 부스 운영 교사, 대수페 운영 및 기획 교사, 장학사 등.  
             - 참여학생 - 동아리, 부스, 봉사 등 사전에 계획하여 참여한 학생,  
             - 체험학생 - 대수페의 각종 체험활동을 통해 스티커를 00개 이상 모은 학생. - 승인이 필요하므로 꼭 본관 1층 방문하여 일련번호 받기
            """)
        st.markdown("**학년, 반, 번호**: '교사'는 0으로 입력. 학생은 학년, 반, 번호를 정확하게 입력. 본인 확인용으로 활용됩니다.")
        st.markdown("**이름**: 본인의 이름을 정확하게 입력하세요. 오류 시 확인서 발급이 되지 않을 수 있습니다.")
        st.markdown("**생년월일**: 본인의 생년월일을 정확하게 입력하세요. 본인 확인용으로 활용됩니다.")
        st.markdown("**행사복사이즈**: 행사운영 교사, 참여학생의 경우 자신의 사이즈 입력, 체험학생은 '해당없음' 입력")
        st.markdown("**봉사시간**: 참여학생의 경우 학교에서 미리 결재한 시간으로 입력, 교사, 체험학생은 0으로 입력")

    submit = st.button("모든 정보를 정확히 입력하였습니까? 오류가 있을 경우 확인서가 발급되지 않을 수 있습니다.\n 저장하시겠습니까? ")
    if submit:
        data_input(input_list)
        st.success("{0} {1}학년 {2}반 {3}번 {4}학생의 정보가 저장되었습니다.".format(input_list[0][0], input_list[0][2], input_list[0][3], input_list[0][4], input_list[0][5]))
    


if __name__ == "__main__":
    main()








