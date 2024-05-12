import datetime
import json

import streamlit as st

from functions import chehum


def main():
    st.title("2024 대수페 체험활동 확인서 신청")
    row1 = st.columns(4)
    school_name = row1[0].text_input("학교명")  # selectbox로 변경
    grade_num = row1[1].number_input("학년", min_value=1, max_value=6, value=1)
    student_ban = row1[2].number_input("반", step=1, min_value=1, max_value=15, value=1)
    student_id = row1[3].number_input("번호", step=1, min_value=1, max_value=40, value=1)

    row2 = st.columns(2)
    student_name = row2[0].text_input("이름")
    birthdate = row2[1].date_input("생년월일", datetime.date(2007, 1, 1))
    json_birth = json.dumps(birthdate, default=str).strip("\"")

    input_list = [school_name, grade_num, student_ban, student_id, student_name, json_birth]

    explain_toggle = st.toggle("항목별 설명")
    if explain_toggle:
        st.markdown("**학교명**: 정확한 명칭을 입력하세요.")
        st.markdown("**이름**: 본인의 이름을 정확하게 입력하세요. 오류 시 확인서 발급이 되지 않을 수 있습니다.")
        st.markdown("**생년월일**: 본인의 생년월일을 정확하게 입력하세요. 본인 확인용으로 활용됩니다.")

    submit = st.button("모든 정보를 정확히 입력하였습니까? 오류가 있을 경우 확인서가 발급되지 않을 수 있습니다.\n 저장하시겠습니까? ")
    if submit:
        che = chehum()
        che.data_input_chehum(input_list)


if __name__ == "__main__":
    main()








