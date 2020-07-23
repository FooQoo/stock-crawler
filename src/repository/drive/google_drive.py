"""
http://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.files.html
"""

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.service_account import ServiceAccountCredentials
import io


class GoogleDriveAPI:
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

    def __init__(self, file_key: str, service_account_key_path: str):
        """
        コンストラクタ

        Parameters
        ----------
        file_key : str
            google driveのフォルダーのキー
        service_account_key_path : str
            サービスアカウントのキー情報が記載されたローカルパス
        """
        self.GOOGLE_PATH = 'https://www.googleapis.com/auth/drive.file'
        self.KEY_FILE = service_account_key_path
        self.MIME_TYPE = "text/csv"
        self.file_key = file_key
        self.service = self.__get_google_service()

    def upload_file(self, filename: str, text: str):
        """
        google driveへのファイルアップロード

        Parameters
        ----------
        filename : str
            アップロードするファイル名
        text : str
            ファイルの内容(銘柄情報のcsvフォーマット)

        Returns
        -------
        str
            ファイルキー値
        """
        fh = io.BytesIO(text.encode('utf8'))

        file_metadata = {"name": filename, "mimeType": self.MIME_TYPE,
                         "parents": [self.file_key]}
        media = MediaIoBaseUpload(
            fh, mimetype=self.MIME_TYPE, resumable=True)
        file_info = self.service.files().create(
            body=file_metadata, media_body=media, fields='id').execute()
        return file_info['id']

    def update_file(self, text: str, fileid: str):
        """
        ファイル更新

        Parameters
        ----------
        text : str
            更新するcsvのファイル内容
        fileid : str
            更新するファイルのキー値
        """
        fh = io.BytesIO(text.encode('utf8'))

        media = MediaIoBaseUpload(
            fh, mimetype=self.MIME_TYPE, resumable=True)
        self.service.files().update(fileId=fileid, media_body=media).execute()

    def get_file(self, code: str):
        """
        google driveからファイルのキー値を取得する

        Parameters
        ----------
        code : str
            銘柄コード

        Returns
        -------
        str
            ファイルのキー値
        """
        results = self.service.files().list(
            q=f"name contains '{code}'", fields='nextPageToken, files(id, name, mimeType)').execute()
        items = results.get('files', [])

        if not items:
            return None
        else:
            return items[0]['id']

    def delete_file(self, fileid: str):
        """
        google driveのファイル削除

        Parameters
        ----------
        fileid : str
            ファイルのキー値
        """
        self.service.files().delete(fileId=fileid).execute()

    def __get_google_service(self):
        """
        gcpのサービスアカウントの取得

        Returns
        -------
        service
            サービスアカウントクラス
        """
        scope = [self.GOOGLE_PATH]
        keyFile = self.KEY_FILE
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            keyFile, scopes=scope)

        return build("drive", "v3", credentials=credentials, cache_discovery=False)


if __name__ == "__main__":
    api = GoogleDriveAPI('your/drive/path')
    api.upload_file('test', 'hoge')
    fileid = api.get_file('test')
    api.delete_file(fileid)
