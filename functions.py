import pandas as pd
import streamlit as st
import gspread as gc
from google.oauth2 import service_account
from gspread_formatting import DataValidationRule, BooleanCondition, set_data_validation_for_cell_range
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import tempfile
import pytz
from datetime import datetime

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

def get_seoul_time():
    # 서울 시간대 객체 생성
    seoul_tz = pytz.timezone('Asia/Seoul')

    # 현재 UTC 시간을 가져온 후 서울 시간대로 변환
    utc_dt = datetime.utcnow()
    utc_dt = utc_dt.replace(tzinfo=pytz.utc)  # UTC 시간대 정보 추가
    seoul_dt = utc_dt.astimezone(seoul_tz)  # 서울 시간대로 변환

    # strftime을 사용하여 원하는 형식의 문자열로 변환
    formatted_time = seoul_dt.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time

def data_load(sheet_name):
    all_data = pd.DataFrame(sheet_name.get_all_values())
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

class chehum:
    def __init__(self):
        self.using_spreadsheet_id = '1DwMKa9x9mHZnKUFgylhgQahEoFaTmfHCr4yeCVNVpT4'
        self.spreadsheet = client.open_by_key(self.using_spreadsheet_id)
        self.chehumsheet = self.spreadsheet.worksheet('체험활동')  # 'Sheet1'은 열고자 하는 시트의 이름입니다.
        self.school_sheet = self.spreadsheet.worksheet('학교')



    def insert_row(self, input_list, last_row, message):
        self.chehumsheet.add_rows(1)
        validation_rule = DataValidationRule(
            BooleanCondition('BOOLEAN', ['TRUE', 'FALSE']),
            # condition'type' and 'values', defaulting to TRUE/FALSE
            showCustomUi=True)
        set_data_validation_for_cell_range(self.chehumsheet, "A" + str(last_row), validation_rule)  # inserting checkbox
        input_list.append(get_seoul_time())
        self.chehumsheet.update(range_name="B" + str(last_row), values=[input_list])
        self.chehumsheet.update_cell(last_row, 10, value="=\"Daugu-2024-\"&text(I" + str(last_row) + ",\"00#\")")
        st.success(message.format(input_list[0], input_list[1], input_list[2], input_list[3], input_list[4]))



    def data_input_chehum(self, input_list):
        last_row = self.chehumsheet.row_count+1
        del_message = """{0} {1}학년 {2}반 {3}번 {4}학생의 정보가 기존에 있습니다..  
         삭제후 다시 저장하였습니다.  
         대구과학고등학교 본관 1층 로비로 가서 체험활동확인서를 제출하고 승인 받으세요."""
        message = """{0} {1}학년 {2}반 {3}번 {4}학생의 정보가 저장되었습니다.  
         대구과학고등학교 본관 1층 로비로 가서 체험활동확인서를 제출하고 승인 받으세요."""
        if input_list[4] == "":
            st.warning("학생의 이름을 입력하지 않았습니다. 입력되지 않습니다.")
        else:
            chehum_df = self.chehum_df()
            detect_same_index = self.detect_same_index(chehum_df, input_list[:5])

            if detect_same_index:
                index_TF = chehum_df['승인'].values.tolist()[detect_same_index]
                if index_TF=='TRUE':
                    st.warning("해당 학생의 정보가 이미 승인되었습니다. [승인확인] 탭에서 발급번호를 확인하세요.")
                else:
                    self.chehumsheet.delete_rows(detect_same_index+2)
                    self.insert_row(input_list, last_row-1, del_message)

            else:
                self.insert_row(input_list, last_row, message)


    def serial_input_chehum(self):
        chehumdata = self.chehum_df()
        serials = chehumdata['일련번호'].tolist()
        max_serial = max(serials)
        approved_data = chehumdata[chehumdata['승인']=="TRUE"]
        insert_index = approved_data[approved_data['일련번호'] == ''].index
        for i in range(len(insert_index)):
            self.chehumsheet.update(range_name="I" + str(insert_index[i] + 1), values=[[int(max_serial) + i + 1]])



    def chehum_df(self):
        chehumdf= data_load(self.chehumsheet)
        return chehumdf

    def chehum_approval_df(self):
        data = self.chehum_df()
        data = data[data['승인'] == "TRUE"]
        return data

    def detect_same_index(self, df, input_list):
        data = df.values[:,1:6].tolist()
        input_list = [str(x) for x in input_list]
        if input_list in data:
             return data.index(input_list)
        else:
            return None



class drive_uoload:
    def __init__(self, drive_folder_id):
        self.drive_folder_id = drive_folder_id

    def data_upload_file(self):

        using_folder_id = self.drive_folder_id
        # 파일 업로더

        uploaded_file = st.file_uploader("파일을 선택하세요", type=["pdf", "csv", "xls", "xlsx", "hwp", "hwpx"])
        cols = st.columns([0.5, 1, 0.5])
        upload_btn = cols[0].button("업로드")
        file_list_call = cols[2].button("제출목록")

        file_names, file_ids = self.file_name_id_list()
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

    def file_name_id_list(self):

        using_folder_id = self.drive_folder_id
        query = f"'{using_folder_id}' in parents"
        results = service.files().list(q=query, fields="files(id, name, createdTime)").execute()
        items = results.get('files', [])
        file_names = pd.DataFrame(items)['name'].tolist()
        file_ids = pd.DataFrame(items)['id'].tolist()
        return file_names, file_ids


class booth:
    def __init__(self):
        self.using_spreadsheet_id = '1DwMKa9x9mHZnKUFgylhgQahEoFaTmfHCr4yeCVNVpT4'
        self.spreadsheet = client.open_by_key(self.using_spreadsheet_id)
        self.boothsheet = self.spreadsheet.worksheet('동아리부스')  # 'Sheet1'은 열고자 하는 시트의 이름입니다.
        self.booth_df = data_load(self.boothsheet)
        self.stusheet = self.spreadsheet.worksheet('부스학생')
        self.stu_df = data_load(self.stusheet)


    def insert_row(self, input_list, last_row, message):
        bsheet = self.boothsheet
        bsheet.add_rows(1)
        validation_rule = DataValidationRule(
            BooleanCondition('BOOLEAN', ['TRUE', 'FALSE']),
            # condition'type' and 'values', defaulting to TRUE/FALSE
            showCustomUi=True)
        set_data_validation_for_cell_range(bsheet, "A" + str(last_row), validation_rule)  # inserting checkbox
        bsheet.update_cell(last_row, 2, value="=row()-1")

        input_list.append(get_seoul_time())
        bsheet.update(range_name="C" + str(last_row), values=[input_list])
        st.success(message.format(input_list[3], input_list[4], input_list[5]))

    def detect_same_index(self, df, input_list):
        check_data = df[['학교명','팀명']].values.tolist()
        if input_list in check_data:
             return check_data.index(input_list)
        else:
            return None

    def data_input_booth(self, input_list, start_col="B"):
        bsheet = self.boothsheet
        b_df = self.booth_df
        last_row = bsheet.row_count + 1
        input_list.append(get_seoul_time())


        del_message = """{0} {1} 동아리의 기존 정보를 삭제하고 새로 입력한 주제 {2} 로 업데이트합니다.  
            변경이 불가하도록 하시려면 [대구과학고 교사 최재혁]에게 교육청 메신져로 메시지 하시면 됩니다. 
            내용: // {0} 학교 {1} 동아리 정보는 더이상 수정하지 않겠습니다. //  """
        message = "{0} {1} 동아리의 주제 {2}의 정보가 입력되었습니다. 불러오기를 통해 잘 저장되었는지 확인하세요. "

        detect_same_index = self.detect_same_index(b_df, input_list[3:5])

        if detect_same_index:
            index_TF = b_df['승인'].values.tolist()[detect_same_index]
            if index_TF == 'TRUE':
                st.warning("해당 동아리의 정보가 수정불가로 설정되었습니다.")
            else:
                bsheet.delete_rows(detect_same_index + 2)
                self.insert_row(input_list, last_row - 1, del_message)

        else:
            self.insert_row(input_list, last_row, message)




    def insert_row_stu(self, input_list, last_row, message):
        ssheet = self.stusheet
        ssheet.add_rows(1)
        validation_rule = DataValidationRule(
            BooleanCondition('BOOLEAN', ['TRUE', 'FALSE']),
            # condition'type' and 'values', defaulting to TRUE/FALSE
            showCustomUi=True)
        set_data_validation_for_cell_range(ssheet, "A" + str(last_row), validation_rule)  # inserting checkbox
        ssheet.update_cell(last_row, 2, value="=row()-1")

        input_list.append(get_seoul_time())
        ssheet.update(range_name="C" + str(last_row), values=[input_list])
        st.success(message.format(input_list[0], input_list[2], input_list[3], input_list[4], input_list[5]))


    def detect_same_stu_index(self, df, input_list):
        check_data = df.iloc[:,2:8].values.tolist()
        if input_list in check_data:
            return check_data.index(input_list)+2
        else:
            return None
    def stu_df_input(self, excel_df):
        stusheet = self.stusheet
        stu_df = self.stu_df
        excel_tolist = excel_df.values.tolist()

        for input_list in excel_tolist:
            last_row = stusheet.row_count

            del_message = """{0} {1}학년 {2}반 {3}번 {4}학생의 정보가 기존에 있습니다.  
             삭제후 다시 저장하였습니다."""
            message = """{0} {1}학년 {2}반 {3}번 {4}학생의 정보가 저장되었습니다."""
            inputlist = [str(x) for x in input_list[0:6]]
            detect_same_index = self.detect_same_stu_index(stu_df, inputlist)

            if detect_same_index is not None:
                index_TF = stu_df['승인'].values.tolist()[detect_same_index-2]
                if index_TF == 'TRUE':
                    st.warning("해당 동아리의 정보가 수정불가로 설정되었습니다.")
                else:
                    stusheet.delete_rows(detect_same_index)
                    self.insert_row_stu(input_list, last_row , del_message)

            else:
                self.insert_row_stu(input_list, last_row+1, message)

