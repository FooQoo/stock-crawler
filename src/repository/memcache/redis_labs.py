import bmemcached

"""
https://redislabs.com/lp/python-memcached/ 
"""


class MemcachedAPI:
    """
    memcacheとやり取りするAPI

    Attributes
    -------
    MEMCACHE_KEY : str
        キャッシュのキー
    EXPIRE_TIME : str
        キャッシュが切れるまでの時間(秒)
    db : Client
        キャッシュのconnection pool

    Raises
    ------
    Exception
        キャッシュのget/setが失敗した場合、例外を返す
    """
    MEMCACHE_KEY = 'code'
    EXPIRE_TIME = 60 * 30

    def __init__(self, host: str, username: str, password: str):
        """
        コンストラクタ

        Parameters
        ----------
        host : str
            memcacheのホスト
        username : str
            memcacheのユーザ名
        password : str
            memcacheのパスワード
        """
        self.db = bmemcached.Client(
            [host], username=username, password=password)

    def set_stock_code(self, code: str):
        """
        銘柄コードをキャッシュにセットする

        Parameters
        ----------
        code : str
            銘柄コード

        Raises
        ------
        Exception
            銘柄コードのsetに失敗した場合
        """
        is_healthy = self.db.set(self.MEMCACHE_KEY, code, self.EXPIRE_TIME)
        if not is_healthy:
            raise Exception('Failed set cache.')

    def get_stock_code(self):
        """
        銘柄コードを取得する

        Returns
        -------
        str
            銘柄コード

        Raises
        ------
        Exception
            銘柄コードのgetに失敗した場合
        """
        code = self.db.get(self.MEMCACHE_KEY)
        if code is None:
            raise Exception('Failed fetch cache')
        else:
            return code
