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
    """
    CODE_COLUMN = '銘柄コード'

    def __init__(self, filepath: str):
        """
        コンストラクタ

        Parameters
        ----------
        filepath : str
            ローカルのcsvファイルのパス
        """

        df = pd.read_csv(filepath)
        stocks = df[self.CODE_COLUMN].tolist()
        self.__first_code = stocks[0]
        self.__queue = self.__get_stock_queue(stocks)

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
