from repository.memcache import MemcachedAPI
from repository.stock_list import StockListAPI
from repository.stock import StockAPI
from repository.drive import GoogleDriveAPI
from repository.sheet import SheetAPI
import traceback
from io import StringIO
import pandas as pd

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
    CSV_HEADER = "code,date,open,high,low,closing,volume,closed_adj"
    STAGE_TRANSITION = [4, 4, 5]
    SHORT_TERM = 5
    MIDDLE_TERM = 25
    LONG_TERM = 75

    def __init__(
            self,
            cached_host: str,
            cached_user: str,
            cached_password: str,
            filepath: str,
            drivepath: str,
            service_account_key_path: str,
            stock_api_path: str,
            sheet_id: str):
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
        sheet_id : str
            スプレッドシートのid
        """
        self.memcache_api = MemcachedAPI(
            cached_host, cached_user, cached_password)
        self.stock_list_api = StockListAPI(filepath, filter_mode=True)
        self.stock_api = StockAPI(stock_api_path)
        self.drive_api = GoogleDriveAPI(drivepath, service_account_key_path)
        self.sheet_api = SheetAPI(service_account_key_path, sheet_id)

    def start(self, insert_flag=True):
        """
        タスクの実行

        Parameters
        ----------
        insert_flag : bool, optional
            google driveへの保存実行フラグ, by default True
        """
        try:
            code = self.__get_stock_code()
            csv = self.__fetch_stock(code)
            if insert_flag:
                self.__drive_insert(csv, code)
            self.__append_purchace_sign(csv)
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

    def __append_purchace_sign(self, csv: str):
        """
        買シグナルのある銘柄を保存する

        Parameters
        ----------
        csv : str
            取得したcsvファイル
        """

        # 買いシグナルを計算
        df = pd.read_csv(StringIO(csv), index_col='date',
                         parse_dates=True).sort_index()
        df['short'] = df.closed_adj.rolling(self.SHORT_TERM).mean().round(1)
        df['middle'] = df.closed_adj.rolling(self.MIDDLE_TERM).mean().round(1)
        df['long'] = df.closed_adj.rolling(self.LONG_TERM).mean().round(1)
        df['four_stage'] = (df.short < df.long) & (
            df.short < df.middle) & (df.middle < df.long)
        df['five_stage'] = (df.short < df.long) & (
            df.short >= df.middle) & (df.middle < df.long)
        df['stage'] = df.four_stage * 4 + df.five_stage * 5
        df = df.dropna()
        df['purchase_sign'] = df.stage.rolling(3).apply(
            lambda x: list(x) == self.STAGE_TRANSITION)

        cells = []
        for last_day in df.tail(1).itertuples():
            if last_day.purchase_sign:
                # 銘柄情報を取得する
                info = self.stock_list_api.get_stock_info_by_code(
                    last_day.code)

                cel = [
                    last_day.Index.strftime('%Y-%m-%d'),
                    last_day.code,
                    info[self.stock_list_api.CODE_NAME],
                    info[self.stock_list_api.BIZ_TYPE],
                    last_day.closed_adj,
                    last_day.short,
                    last_day.middle,
                    last_day.long
                ]

                cells.append(cel)

        if len(cells) > 0:
            self.sheet_api.append(cells)

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
            csv += "\n" + "\n".join(
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
