from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


"""
https://github.com/gsuitedevs/python-samples/blob/master/sheets/snippets/spreadsheet_snippets.py
"""


class SheetAPI:
    """
    memcacheとやり取りするAPI

    Attributes
    -------
    GOOGLE_PATH : str
        キャッシュのキー
    KEY_FILE : str
        サービスアカウント情報が記載されたローカルのパス
    MIME_TYPE : str
        ファイル形式
    file_key : str
        google driveのフォルダーのキー
    service : service
        gcpのサービスアカウント
    """

    def __init__(self, service_account_key_path: str, sheet_id: str):
        """
        コンストラクタ

        Parameters
        ----------
        service_account_key_path : str
            サービスアカウントのキー情報が記載されたローカルパス
        sheet_id : str
            spreadsheetのキー
        """
        self.GOOGLE_PATH = 'https://www.googleapis.com/auth/drive.file'
        self.GOOGLE_SHEET_PATH = 'https://spreadsheets.google.com/feeds'
        self.KEY_FILE = service_account_key_path
        self.service = self.__get_google_service()
        self.SHEET_ID = '1MetA2G9ifOZLecWjQ-Lu-P4NGMCb0UBiy2VMXS_edlM'

    def append(self, cells: list):
        """
        google driveへのファイルアップロード

        Parameters
        ----------
        text : str
            ファイルの内容(銘柄情報のcsvフォーマット)
        """
        body = {
            'values': cells
        }
        self.service.spreadsheets().values().append(
            spreadsheetId=self.SHEET_ID, range='A1',
            valueInputOption='USER_ENTERED', body=body, insertDataOption='INSERT_ROWS').execute()

    def __get_google_service(self):
        """
        gcpのサービスアカウントの取得

        Returns
        -------
        service
            サービスアカウントクラス
        """
        scope = [self.GOOGLE_SHEET_PATH, self.GOOGLE_PATH]
        keyFile = self.KEY_FILE
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            keyFile, scopes=scope)

        return build("sheets", "v4", credentials=credentials, cache_discovery=False)
