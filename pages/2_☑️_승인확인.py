import numpy as np
import streamlit as st

from functions import chehum
from functions import conditional_filter


def main():
    st.subheader('2024. 대구수학페스티벌 참가자 확인')
    che = chehum()
    approved_data = che.chehum_approval_df()

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
        che.serial_input_chehum()



    filtered_data = conditional_filter(approved_data,
                                       school_name=school_name,
                                       grade_num=grade_num,
                                       student_ban=student_ban,
                                       student_id=student_id,
                                       student_name=student_name)
    st.dataframe(filtered_data[["학교명", "발급번호","학년", "반", "번호", "이름"]], use_container_width=True)

    st.write("ver.2024.05.10. 14:36")

if __name__ == '__main__':
    main()