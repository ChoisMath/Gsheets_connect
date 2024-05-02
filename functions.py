import pandas as pd
import streamlit as st
import gspread as gc
import numpy as np
from google.oauth2 import service_account
from gspread_formatting import DataValidationRule, BooleanCondition, set_data_validation_for_cell_range
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials
from io import BytesIO
import tempfile
import time

# 서비스 계정 정보
credental_json = {
    "type": "service_account",
    "project_id": "chois-python-connect",
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"],
    "client_email": st.secrets["client_email"],
    "client_id": "116464278440047112678",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/chois-python-connect%40chois-python-connect.iam.gserviceaccount.com",
}


# Google Sheets 및 Drive API에 액세스할 수 있는 권한 부여
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]

credentials = service_account.Credentials.from_service_account_info(credental_json, scopes=scope)

# gspread 클라이언트 초기화
client = gc.authorize(credentials)

# Google Drive 서비스 객체 생성
service = build('drive', 'v3', credentials=credentials)




# 스프레드시트 열기
#API메일로 해당 스프레드시트 공유설정에 '편집자'권한으로 설정하기
using_spreadsheet_id = '1DwMKa9x9mHZnKUFgylhgQahEoFaTmfHCr4yeCVNVpT4'
spreadsheet = client.open_by_key(using_spreadsheet_id)

# 시트 선택
sheet = spreadsheet.worksheet('sheet1') # 'Sheet1'은 열고자 하는 시트의 이름입니다.
school_sheet = spreadsheet.worksheet('학교')

def data_input(input_list):
    all_data = np.array(sheet.get_all_values())
    last_row = all_data.shape[0]+1
    message = """{0} {1}학년 {2}반 {3}번 {4}학생의 정보가 저장되었습니다.  
     대구과학고등학교 본관 1층 로비로 가서 체험활동확인서를 제출하고 승인 받으세요."""
    if input_list[0][4] == "":
        st.warning("학생의 이름을 입력하지 않았습니다. 입력되지 않습니다.")
    else:
        sheet.update(range_name="B" + str(last_row), values=input_list)
        validation_rule = DataValidationRule(
            BooleanCondition('BOOLEAN', ['TRUE', 'FALSE']),  # condition'type' and 'values', defaulting to TRUE/FALSE
            showCustomUi=True)
        set_data_validation_for_cell_range(sheet,"A" + str(last_row), validation_rule)  # inserting checkbox
        sheet.update_cell(last_row,9, value="=\"Daugu-2024-\"&text(H"+str(last_row)+",\"00#\")")
        st.success(message.format(input_list[0][0], input_list[0][2], input_list[0][3], input_list[0][4], input_list[0][5]))


def data_load():
    all_data = pd.DataFrame(sheet.get_all_values())
    all_data.columns = list(all_data.iloc[0])
    all_data = all_data.iloc[1:]
    return all_data

def approval_filter(data):
    data = data.dropna(axis=0, how='any')
    data = data[data['승인']=="TRUE"]
    return data

def conditional_filter(data,
                       school_name = None,
                       grade_num = None,
                       student_ban = None,
                       student_id = None,
                       student_name =None):
    filtered_data = data
    if school_name is not None:
        filtered_data = filtered_data[filtered_data["학교명"]==school_name]
    if grade_num is not None:
        filtered_data = filtered_data[filtered_data['학년']==str(grade_num)]
    if student_ban is not None:
        filtered_data = filtered_data[filtered_data['반']==str(student_ban)]
    if student_id is not None:
        filtered_data = filtered_data[filtered_data['번호']==str(student_id)]
    if student_name is not None:
        filtered_data = filtered_data[filtered_data['이름']==student_name]

    return filtered_data

def input_serial():
    data = data_load()
    approved_data = approval_filter(data)
    insert_index = approved_data[approved_data['일련번호'] == ''].index
    serials = data['일련번호'].values.tolist()
    now_max_serial = np.max([int(x) if x != '' else 0 for x in serials])
    # st.success(insert_index)
    # st.success(serials)
    # st.success(now_max_serial)

    for i in range(len(insert_index)):
        sheet.update(range_name="H" + str(insert_index[i] + 1), values=[[int(now_max_serial) + i + 1]])

#API메일로 해당폴더 공유설정에 '편집자'권한으로 설정하기
using_folder_id = "1hDFC1bc9MNMn5U3XcBcAh-LrVwNpO8Nt"

def data_upload_file():
    # 파일 업로더
    cols = st.columns([0.5, 1, 0.5])
    upload_btn = cols[0].button("업로드")
    file_list_call = cols[2].button("제출목록")
    uploaded_file = st.file_uploader("파일을 선택하세요", type=["pdf", "csv", "xls", "xlsx", "hwp", "hwpx"])



    file_names, file_ids = file_name_id_list()
    if uploaded_file is not None and upload_btn:

        if uploaded_file.name in file_names:
            index_list = file_names.index(uploaded_file.name)
            file_id = file_ids[index_list]
            service.files().delete(fileId=file_id).execute()

        # 파일을 임시 디렉토리에 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='_' + uploaded_file.name) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = tmp_file.name

        # 파일 메타데이터 생성
        file_metadata = {'name': uploaded_file.name, 'parents': [using_folder_id]}

        # 파일 콘텐츠를 메모리에서 읽기
        file_stream = BytesIO(uploaded_file.getvalue())
        media = MediaIoBaseUpload(file_stream, mimetype=uploaded_file.type)

        # 파일 업로드 실행
        try:
            file = service.files().create(body=file_metadata, media_body=media, fields='id, name').execute()
            st.success(f'파일이 성공적으로 업로드 되었습니다. 파일 이름: {file["name"]}')

        except Exception as e:
            st.error(f'파일 업로드 실패: {e}')


    else:
        st.warning('[업로드]를 눌러 파일을 올리고, [제출목록]을 눌러 제출여부를 확인해 주세요.')

    if file_list_call:
        query = f"'{using_folder_id}' in parents"
        results = service.files().list(q=query, fields="files(id, name, createdTime)").execute()
        items = results.get('files', [])
        # 파일 목록 출력
        if not items:
            st.warning('No files found.')
        else:
            df = pd.DataFrame(items)
            sorted_df = df.sort_values(by='createdTime', ascending=False)
            st.dataframe(sorted_df[['name', 'createdTime']])

def file_name_id_list():
    query = f"'{using_folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name, createdTime)").execute()
    items = results.get('files', [])
    file_names = pd.DataFrame(items)['name'].tolist()
    file_ids = pd.DataFrame(items)['id'].tolist()
    return file_names, file_ids


