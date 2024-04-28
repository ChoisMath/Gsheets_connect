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


def data_load():
    all_data = pd.DataFrame(sheet.get_all_values())
    all_data.columns = list(all_data.iloc[0])
    all_data = all_data.iloc[1:]
    return all_data

def approval_filter(data):
    data = data.dropna(axis=0, how='any')
    data = data[data['승인']=="TRUE"]
    return data

def conditional_filter(data,
                       school_name = None,
                       grade_num = None,
                       student_ban = None,
                       student_id = None,
                       student_name =None):
    filtered_data = data
    if school_name is not None:
        filtered_data = filtered_data[filtered_data["학교명"]==school_name]
    if grade_num is not None:
        filtered_data = filtered_data[filtered_data['학년']==str(grade_num)]
    if student_ban is not None:
        filtered_data = filtered_data[filtered_data['반']==str(student_ban)]
    if student_id is not None:
        filtered_data = filtered_data[filtered_data['번호']==str(student_id)]
    if student_name is not None:
        filtered_data = filtered_data[filtered_data['이름']==student_name]

    return filtered_data

def main():
    st.subheader('2024. 대구수학페스티벌 참가자 확인')
    data = data_load()
    approved_data = approval_filter(data)

    row1 = st.columns(2)
    school_name = row1[0].selectbox('학교명', options=np.unique(np.array(approved_data['학교명'])))
    if school_name=="":
        school_name = None

    student_name = row1[1].text_input("이름")
    if student_name=="":
        student_name = None

    row2 = st.columns(3)
    grade_num = row2[0].number_input("학년", min_value=0, max_value=6, value=0)
    if grade_num==0:
        grade_num = None

    student_ban = row2[1].number_input("반", step=1, min_value=0, max_value=15, value=0, placeholder="선생님은 o반")
    if student_ban == 0:
        student_ban = None

    student_id = row2[2].number_input("번호", step=1, min_value=0, max_value=40, value=0, placeholder="선생님은 o번")
    if student_id == 0:
        student_id = None

    row3 = st.columns([0.7,1.2,0.5])
    set_serial = row3[0].button("일련번호 등록")
    if set_serial:
        data= data_load()
        approved_data = approval_filter(data)
        insert_index = approved_data[approved_data['일련번호']==''].index
        serials = approved_data['일련번호']
        now_max_serial = np.max(serials[serials!=''])
        # st.write(insert_index)
        # st.write(now_max_serial)

        for i in range(len(insert_index)):
            sheet.update(range_name="K" + str(insert_index[i]+1), values=[[int(now_max_serial)+i+1]])


    filter = row3[2].button("검색")
    if filter:
        filtered_data = conditional_filter(approved_data,
                                           school_name=school_name,
                                           grade_num=grade_num,
                                           student_ban=student_ban,
                                           student_id=student_id,
                                           student_name=student_name)
        st.dataframe(filtered_data, use_container_width=True)

if __name__ == '__main__':
    main()