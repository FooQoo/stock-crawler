# 使用方法まとめ
## デプロイ

```bash
$ gcloud beta functions deploy stock-clawler  --entry-point=main --trigger-topic=stock --env-vars-file=env.yaml --source=src --runtime=python38 --timeout=300
```

## スケジュール
```bash
gcloud scheduler jobs create pubsub feeder \
 --topic stock \
 --message-body='fetch info' \
 --schedule '* * * * *' \
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
