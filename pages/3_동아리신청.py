import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload
from google.oauth2.service_account import Credentials
from io import BytesIO
import functions
import tempfile
import os
import time


# Streamlit 앱 설정
def main():
    st.title('Google Drive 파일 업로더')


    # 파일 업로더
    uploaded_file = st.file_uploader("파일을 선택하세요", type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv',"xls", "xlsx"])

    # 딕셔너리를 사용하여 Credentials 객체 생성
    credentials = Credentials.from_service_account_info(functions.credental_json,
                                                        scopes=['https://www.googleapis.com/auth/drive'])

    # Google Drive 서비스 객체 생성
    service = build('drive', 'v3', credentials=credentials)

    if uploaded_file is not None:
        # 파일을 임시 디렉토리에 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='_' + uploaded_file.name) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = tmp_file.name

        # 파일 메타데이터 생성
        file_metadata = {'name': uploaded_file.name, 'parents': ["1hDFC1bc9MNMn5U3XcBcAh-LrVwNpO8Nt"]}

        # 파일 콘텐츠를 메모리에서 읽기
        file_stream = BytesIO(uploaded_file.getvalue())
        media = MediaIoBaseUpload(file_stream, mimetype=uploaded_file.type)

        # 파일 업로드 실행
        try:
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            st.success(f'파일이 성공적으로 업로드 되었습니다. 파일 ID: {file["id"]}')
        except Exception as e:
            st.error(f'파일 업로드 실패: {e}')



if __name__ == "__main__":
    main()
