import requests


class StockAPI:
    """
    株価を取得するAPI

    Attributes
    -------
    KABUOJI_PATH : str
        APIのエンドポイント
    header : str
        リクエストに付与するヘッダー
    """

    def __init__(self, path):
        """
        コンストラクタ
        """
        self.KABUOJI_PATH = path
        self.HEADER = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

    def fetch_stock(self, code: str, year: str):
        """
        リクエストを投げて株価を取得する

        Parameters
        ----------
        code : str
            銘柄コード
        year : str
            取得する年(西暦)

        Returns
        -------
        str
            csvフォーマットの株価情報
        """
        payload = self.__get_payload(code, year)

        r = requests.post(self.KABUOJI_PATH, data=payload,
                          headers=self.HEADER)

        r.raise_for_status()

        return r.text

    def __get_payload(self, code: str, year: str):
        """
        POSTパラメータの取得。

        Parameters
        ----------
        code : str
            銘柄コード
        year : str
            取得する年(西暦)


        Returns
        -------
        dict
            POSTパラメータ
        """
        return {
            "code": code, "year": year}
