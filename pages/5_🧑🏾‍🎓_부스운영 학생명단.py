from io import BytesIO

import pandas as pd
import streamlit as st

from functions import data_load
from functions import stu


def save_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='학생신청양식')
    return output


# 예제 데이터 프레임 생성
empty_data = {
    '학교명': ['학교이름','','','','','','',''],
    '팀명': ['동아리 이름', '혹은 동아리가 아닐 경우 부스이름','','','','','',''],
    '학년': ['','','','','','','',''],
    '반': ['','','','','','','',''],
    '번호': ['','','','','','','',''],
    '이름': ['','','','','','','',''],
    '봉사활동시간': ['8시간 이내','','','','','','',''],
    '활동복사이즈': ['xxL', 'xL','L','M','S','xS','xxS','중 선택']
}

def main():
    st.subheader("2024-대수페-부스운영 학생명단 제출")
    s=stu()
    empty_df = pd.DataFrame(empty_data)
    val = save_to_excel(empty_df)
    st.sidebar.download_button(
        label="양식 다운로드",
        data=val,
        file_name='2024대수페_부스운영학생신청(양식).xlsx',
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    upload_file = st.sidebar.file_uploader("운영학생 파일업로드", type=["xls", "xlsx"])
    if upload_file is not None:
        excel_df = pd.read_excel(upload_file)
        s.stu_df_input(excel_df)

    stusheet = s.spreadsheet.worksheet("부스학생")
    stu_df = data_load(stusheet).sort_values(by=['입력시간'], ascending=False)
    st.dataframe(stu_df.iloc[:,2:])
        
    st.link_button(
        label = 'Link to Google Spreadsheet',
        url='https://docs.google.com/spreadsheets/d/1DwMKa9x9mHZnKUFgylhgQahEoFaTmfHCr4yeCVNVpT4/edit#gid=634440090',
        use_container_width=True
    )


if __name__ == "__main__":
    main()