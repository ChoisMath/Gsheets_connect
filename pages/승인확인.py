import pandas as pd
import streamlit as st
import gspread as gc
import numpy as np
import os
from google.oauth2 import service_account
import datetime, json
from gspread_formatting import DataValidationRule, BooleanCondition, set_data_validation_for_cell_range
from functions import data_load, approval_filter, conditional_filter


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
    set_serial = row3[0].button("일련번호 입력")
    if set_serial:
        data= data_load()
        approved_data = approval_filter(data)
        insert_index = approved_data[approved_data['일련번호'] == ''].index
        serials = data['일련번호'].values.tolist()
        now_max_serial = np.max([int(x) if x!='' else 0 for x in serials])
        # st.success(insert_index)
        # st.success(serials)
        # st.success(now_max_serial)

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
        st.dataframe(filtered_data[["학교명", "일련번호", "구분","학년", "반", "번호", "이름", "봉사시간"]], use_container_width=True)

    st.write("ver.2024.04.29. 2:36")

if __name__ == '__main__':
    main()