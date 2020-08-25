# 使用方法まとめ
## デプロイ

```bash
$ gcloud beta functions deploy stock-crawler  --entry-point=main --trigger-topic=stock --env-vars-file=env.yaml --source=src --runtime=python38 --timeout=300
```

## スケジュール
- 毎週日曜日に毎分実行
```bash
# 新規作成
$ gcloud scheduler jobs create pubsub feeder \
 --topic stock \
 --message-body='fetch info' \
 --schedule '* * * * 5,6' \
 --time-zone='Asia/Tokyo'

 # 更新
$ gcloud scheduler jobs update pubsub feeder \
 --topic stock \
 --message-body='fetch info' \
 --schedule '* * * * 5,6' \
 --time-zone='Asia/Tokyo'
```
## 依存関係

```bash
$ poetry export -f requirements.txt --without-hashes > src/requirements.txt

```

## データ取得テスト方法

```bash
$ curl -X POST -d "code=1301&year=2020" "path" -o 1301_2020.csv
```

## gcp仕様
```
--timeout: max 540sec
```

## 銘柄コードのファイルマージ
```bash
$ bash etc/mergeCsv.sh -d ~/stock -o data/stock.csv 
```