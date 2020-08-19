import pandas as pd


class StockListAPI:
    """
    株価リストをローカル取得するAPI

    Attributes
    -------
    CODE_COLUMN : str
        CSVの銘柄が記載されたカラム
    first_code : str
        実行する最初の銘柄コード
    queue : dict
        銘柄コードの実行待ち順。銘柄コードに入力した際に、次回実行する銘柄コードが出力される。
    stock_info : dict
        銘柄コードに紐づく情報(銘柄名、業種分布)
    """
    CODE_COLUMN = '銘柄コード'
    CODE_NAME = '銘柄名'
    BIZ_TYPE = '業種分類'
    INFO_COLUMNS = ['銘柄名', '業種分類']
    BIZ_TYPE_FILTER = ['情報・通信', '倉庫・運輸関連業',
                       'その他製品', '医薬品', '精密機器', '建設業', 'サービス業']

    def __init__(self, filepath: str, filter_mode=False):
        """
        コンストラクタ

        Parameters
        ----------
        filepath : str
            ローカルのcsvファイルのパス
        filter_mode: bool
            業種フィルタの有無
        """

        df = pd.read_csv(filepath)

        if filter_mode:
            df = df[df[self.BIZ_TYPE].isin(self.BIZ_TYPE_FILTER)]

        stocks = df[self.CODE_COLUMN].tolist()
        self.__first_code = stocks[0]
        self.__queue = self.__get_stock_queue(stocks)
        self.__stock_info = self.__get_stock_info(df)

    def __get_stock_queue(self, stocks: list):
        """
        銘柄コードの実行待ち順を取得する。

        Parameters
        ----------
        stocks : list
            csvから取得した銘柄コード情報

        Returns
        -------
        dict
            銘柄コードの実行待ち順
        """
        queue = {}
        for i in range(len(stocks) - 1):
            queue[stocks[i]] = stocks[i + 1]
        queue[stocks[-1]] = stocks[0]
        return queue

    def get_next_code(self, code: str):
        """
        次回実行する銘柄コードを取得する。

        Parameters
        ----------
        code : str
            銘柄コード

        Returns
        -------
        str
            次回実行する銘柄コード
        """
        if code in self.__queue:
            return self.__queue[code]
        else:
            return None

    def get_first_code(self):
        """
        first_codeのgetterメソッド。

        Returns
        -------
        str
            first_code
        """
        return self.__first_code

    def __get_stock_info(self, df: pd.DataFrame):
        """
        株価情報の辞書を作成する

        Parameters
        ----------
        df : pd.DataFrame
            pandasのDataFrame

        Returns
        -------
        dict
            銘柄コードに紐づいた情報
        """
        return df.set_index(self.CODE_COLUMN).loc[:, self.INFO_COLUMNS].to_dict(orient='index')

    def get_stock_info_by_code(self, code: str):
        """
        銘柄コードに紐づいた株価情報を取得する

        Parameters
        ----------
        code : str
            銘柄コード

        Returns
        -------
        str
            銘柄情報
        """
        return self.__stock_info[code]
