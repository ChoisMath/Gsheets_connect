import streamlit as st


def main():
    st.subheader("2024-대수페-부스운영 학생명단 제출")
    st.sidebar.link_button("양식다운로드", "")
    st.sidebar.file_uploader("운영학생 파일업로드", type=["xls", "xlsx"])
    


if __name__ == "__main__":
    main()