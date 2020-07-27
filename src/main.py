from os import environ
from dotenv import load_dotenv
from runner import Runner

config = 'resources/.env'
load_dotenv(config, verbose=True)


def main(event, context):
    """
    google functionで実行される関数

    Parameters
    ----------
    event : event
        event情報
    context : context
        context情報
    """
    drive_key = environ.get('FILE_KEY')
    cached_host = environ.get('MEMCACHE_HOST')
    cached_username = environ.get('MEMCACHE_USER')
    cached_password = environ.get('MEMCACHE_PASSWORD')
    stocklist_path = environ.get('STOCKLIST_PATH')
    service_account_key_path = environ.get('SERVICE_ACCOUNT_KEY_PATH')
    stock_api_path = environ.get('STOCK_API_PATH')
    sheet_id = environ.get('SHEET_ID')
    runner = Runner(cached_host, cached_username, cached_password,
                    stocklist_path, drive_key, service_account_key_path, stock_api_path, sheet_id)
    runner.start()


if __name__ == '__main__':
    main(None, None)
