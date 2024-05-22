import re

import streamlit as st

from functions import booth


def apply_custom_css():
    st.markdown("""
        <style>
        /* 기본 라벨 스타일 */
        label {
            font-family: 'Garamond', serif;
            color: blue;
        }
        input[placeholder] {
            font-size: 12px;  /* Placeholder 텍스트의 크기를 조정 */
        }
        div[data-testid=="stSelectbox"] > label {
            font-size: 16px;
            font-weight: bold; /* 폰트를 진하게 */
        }
        </style>
    """, unsafe_allow_html=True)

def etc(name, location, unique_key):
    if name == "기타":
        name_etc = location.text_input(label = unique_key, label_visibility= 'hidden')
        name_etc = ":"+name_etc
    else:
        name_etc = ''
    return name_etc

def teacher_input(number):
    # Create layout for inputs
    raw_new = st.columns([0.7, 1, 1.7])
    teacher = raw_new[0].text_input(label=f"지도교사{number}")

    # Inputs for phone number and email with validation
    teacher_cp = raw_new[1].text_input(label=f"지도교사{number} C.P.", placeholder="010-0000-0000")
    teacher_e_mail = raw_new[2].text_input(label=f"지도교사{number} E-mail.", placeholder="your_email_id@domain.link")

    # Phone number validation
    phone_number_re = r"\d{3}-\d{4}-\d{4}"
    pat = re.compile(phone_number_re)
    if pat.match(teacher_cp) is None and teacher_cp:
        raw_new[1].warning("010-0000-0000")

    # Email format validation
    email_confirm_re = r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    p = re.compile(email_confirm_re)
    if p.match(teacher_e_mail) is None and teacher_e_mail:
        raw_new[2].warning("your_id@email.url")

    # Return values
    return teacher, teacher_cp, teacher_e_mail

# Streamlit 앱 설정
def main():
    apply_custom_css()  # CSS 적용
    st.title('2024. 대수페_부스운영 신청')
    st.caption("데이터를 수정하실 떈 학교명, 팀명을 동일하게 작성하신 후 나머지 자료를 입력하여 [제출]하세요.")
    raw1 = st.columns(3)
    school_level = raw1[0].selectbox(label="학교급", options = ["초", "중", "고", "기타"])
    school_level_etc = etc(school_level, raw1[0], "school_level")
    school_belong = raw1[1].selectbox(label="소속", options = ["동부", "서부", "남부", "달성", "시교육청", "기타"])
    school_belong_etc = etc(school_belong, raw1[1],"school_belong")
    publication = raw1[2].selectbox(label="설립", options = ["공립", "사립", "국립", "기타"])
    publication_etc = etc(publication, raw1[2], "publication")

    raw2 = st.columns(2)
    school_name = raw2[0].text_input(label="학교명")
    team_name = raw2[1].text_input(label="팀명(동아리명)")

    booth_subject = st.text_input(label="부스운영주제", placeholder="현수막 및 배너에 입력될 주제입니다. Ex) 다면체 탐구, 감성 ON! 라틴방진 소품 만들기. 네 꿈을 비춰봐! 등 ")


    teacher_1, teacher_1_cp, teacher_1_e_mail = teacher_input(1)
    teacher_2, teacher_2_cp, teacher_2_e_mail = teacher_input(2)

    stuffs = st.text_area(label = "필요물품 및 부스운영 시 고려할 점", placeholder="부스운영에 필요한 물품과 부스장소 선택시 고려해야 할 사항에 대해 기록하여 주세요. 모든 사항을 만족해 드릴 순 없어도 최대한 고려하겠습니다. 신청 예산을 통한 구입물품은 기록하지 않으셔도 됩니다. (신청서에 작성함)")
    budget = st.number_input(label = "신청예산(₩)", min_value = 500000, max_value =1000000, step = 10000)

    input_list = [school_level+school_level_etc,
                  school_belong + school_belong_etc,
                  publication+publication_etc,
                  school_name, team_name, booth_subject,
                  teacher_1, teacher_1_cp, teacher_1_e_mail,
                  teacher_2, teacher_2_cp, teacher_2_e_mail,
                  stuffs, budget]

    raw3 = st.columns(3)
    summit_btn = raw3[0].button("제출")

    b=booth()
    if summit_btn:
        check_list = input_list[:9]+input_list[12:]
        if "" in check_list:
            index_num = check_list.index("")
            labels = ['학교급', '소속', '설립', '학교명', '팀명(동아리명)','부스운영주제','지도교사1','지도교사1 C.P.','지도교사1 E-Mail', '필요물품', '신청예산']
            st.warning(f"{labels[index_num]}이 입력되지 않았습니다.")
        else:
            b.data_input_booth(input_list, start_col="B")

    call_btn = raw3[2].button("불러오기")
    if call_btn:
        data = b.booth_df
        data.sort_values(by=['입력일시'], ascending=False, inplace=True)
        st.dataframe(data, use_container_width=True)



if __name__ == "__main__":
    main()
