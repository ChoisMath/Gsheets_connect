import streamlit as st
import numpy as np
from functions import data_load, approval_filter, conditional_filter, input_serial
from functions import sheet

def main():
    st.subheader('2024. 대구수학페스티벌 참가자 확인')
    data = data_load(sheet)
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
        input_serial()


    filter = row3[2].button("검색")
    if filter:
        filtered_data = conditional_filter(approved_data,
                                           school_name=school_name,
                                           grade_num=grade_num,
                                           student_ban=student_ban,
                                           student_id=student_id,
                                           student_name=student_name)
        st.dataframe(filtered_data[["학교명", "발급번호","학년", "반", "번호", "이름"]], use_container_width=True)

    st.write("ver.2024.05.06. 17:36")

if __name__ == '__main__':
    main()