from repository.memcache import MemcachedAPI
from repository.stock_list import StockListAPI
from repository.stock import StockAPI
from repository.drive import GoogleDriveAPI
import traceback

from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

"""
logger: https://qiita.com/amedama/items/b856b2f30c2f38665701
"""


class Runner:
    """
    タスクを実行するクラス

    Attributes
    -------
    YEARS: list
        対象年度を格納したリスト
    CSV_HEADER: str
        CSVのヘッダー
    memcache_api : MemcachedAPI
        キャッシュAPIのインスタンス
    stock_list_api : StockListAPI
        株価リストAPIのインスタンス
    stock_api : KabuojiAPI
        株価取得APIのインスタンス
    drive_api: GoogleDriveAPI
        google driveのAPIのインスタンス
    """
    YEARS = ["2020", "2019", "2018"]
    CSV_HEADER = "code,date,open,high,low,closing,volume,closed_adj\n"

    def __init__(self, cached_host: str, cached_user: str, cached_password: str, filepath: str, drivepath: str, service_account_key_path: str, stock_api_path: str):
        """
        コンストラクタ

        Parameters
        ----------
        cached_host : str
            キャッシュのホスト
        cached_user : str
            キャッシュのユーザ
        cached_password : str
            キャッシュのパスワード
        filepath : str
            株価リストのローカルのファイルパス
        drivepath : str
            ファイル保存するgoogle driveのフォルダのキー値
        service_account_key_path : str
            google service accountのキーファイルがあるローカルのファイルパス
        stock_api_path : str
            株価取得APIのURL
        """
        self.memcache_api = MemcachedAPI(
            cached_host, cached_user, cached_password)
        self.stock_list_api = StockListAPI(filepath)
        self.stock_api = StockAPI(stock_api_path)
        self.drive_api = GoogleDriveAPI(drivepath, service_account_key_path)

    def start(self):
        """
        タスクの実行
        """
        try:
            code = self.__get_stock_code()
            csv = self.__fetch_stock(code)
            self.__drive_insert(csv, code)
            self.memcache_api.set_stock_code(code)
        except Exception:
            logger.error(traceback.format_exc())
            exit()

    def __get_stock_code(self):
        """
        銘柄コードの取得

        Returns
        -------
        str
            銘柄コード
        """
        try:
            ex_code = self.memcache_api.get_stock_code()
            code = self.stock_list_api.get_next_code(ex_code)
            if code is None:
                logger.info('Code is none.')
                exit()
        except Exception:
            logger.info('No hit memcached.')
            code = self.stock_list_api.get_first_code()
        return code

    def __fetch_stock(self, code: str):
        """
        銘柄情報の取得

        Parameters
        ----------
        code : str
            銘柄コード

        Returns
        -------
        str
            銘柄に関わるcsvフォーマットの文字列
        """
        csv = self.CSV_HEADER
        for year in self.YEARS:
            stock = self.stock_api.fetch_stock(code, year)
            csv += "\n" + \
                "\n".join(
                    [f"{code},{stock_day}" for stock_day in stock.split('\n')[2:]])
        return csv

    def __drive_insert(self, csv: str, code: str):
        """
        google driveへのファイルアップロード

        Parameters
        ----------
        csv : str
            アップロードするファイルの文字列
        code : str
            銘柄コード
        """
        fileid = self.drive_api.get_file(code)
        if fileid is not None:
            self.drive_api.delete_file(fileid)

        self.drive_api.upload_file(f'{code}.csv', csv)
