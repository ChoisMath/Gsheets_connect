
import streamlit as st
from functions import data_input
import datetime, json


def main():
    st.title("2024 대수페 신청사이트")
    row1= st.columns(4)
    school_name = row1[0].text_input("학교명")   #selectbox로 변경
    grade_num = row1[1].number_input("학년", min_value=0, max_value=6, value=0)
    student_ban = row1[2].number_input("반", step=1, min_value=0, max_value=15, value=0, placeholder="선생님은 o반")
    student_id = row1[3].number_input("번호", step=1, min_value=0, max_value=40, value=0, placeholder="선생님은 o번")


    row2 = st.columns(2)
    student_name = row2[0].text_input("이름")
    birthdate = row2[1].date_input("생년월일", datetime.date(2007, 1, 1))
    json_birth = json.dumps(birthdate, default=str).strip("\"")


    input_list = [[school_name, grade_num, student_ban, student_id, student_name, json_birth, ]]

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
    


if __name__ == "__main__":
    main()








