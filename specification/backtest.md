```python
# バックテスト
## 条件
## 1単元ずつ買う
## 売り時では全額売る
import numpy as np
from scipy.stats import skew

def is_purchase(stage, brefore_stage, before_before_stage):
    return (stage == 5) and (brefore_stage == 5) and (before_before_stage != 5)

def is_selling(stage, before_stage):
    return (stage == 2) and (before_stage != 2)

balances = []

for code in tqdm(df.code.unique()):
    balance = 0
    num_stock = 0
    avg_price = 0
    before_stage = 5
    before_before_stage = 5

    for row in list(df[df.code==code].itertuples()):
        stage = row.closed_adj_stage
        price = int(row.price)
        date = row.Index.strftime('%Y-%m-%d')

        if is_purchase(stage, before_stage, before_before_stage):
            avg_price = int((avg_price*num_stock + price*100)/(num_stock+100))
            num_stock += 100
            elapsed = 0
            #print(f"日付：{date} 購入：{price}円 平均株価：{avg_price} 株式数：{num_stock} 合計金額：{avg_price*num_stock}")
            

        if is_selling(stage, before_stage) and num_stock>0:
            balance += num_stock*(price-avg_price)
            #print(f"日付：{date} 売却：{num_stock*price}円 残高：{balance}")
            num_stock = 0
            avg_price = 0
        
        before_stage = stage
        before_before_stage = before_stage

    balance += num_stock*(price-avg_price)
    balances.append(balance)

print(f"中央値：{np.median(balances)}、歪度：{skew(balances)}")
```

```python
for code in tqdm(df.code.unique()):
        df_picked = df.loc[df.code==code, :]

        # status変化をラベル変換
        moving_status = df_picked.closed_adj_stage.rolling(3).apply(
            lambda x: get_moving_statas(x))

        # ステージが5に変化したタイミングで購入する
        df_picked['purchase_sign'] = moving_status == 5
        # ステージが2に変化したタイミングで売る
        df_picked['selling_sign'] = moving_status == 2

        # 購入時の株数 (10万円以下の場合、10万に近くなるまで単元を増やす)
        df_picked['num_stock'] = df_picked.apply(lambda x: int(100000/x.price) if x.purchase_sign and x.price <= 1000 else 100, axis=1)

        signs.append(df_picked[['code', 'price', 'purchase_sign', 'selling_sign', 'num_stock']])
```