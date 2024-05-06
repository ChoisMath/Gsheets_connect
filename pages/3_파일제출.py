import streamlit as st

from functions import data_upload_file


# Streamlit 앱 설정
def main():

    st.title('2024. 대수페_파일제출')

    st.write(""" 파일명은 [학교명_동아리명.hwp or 학교명_동아리명.hwpx]로 해주시기 바랍니다.  
    수정된 파일을 업로드 할 떄도 파일명을 그대로 올려주시면,  
    기존 파일은 삭제되고 새로운 파일이 업로드됩니다.
    """)
    data_upload_file()





if __name__ == "__main__":
    main()
