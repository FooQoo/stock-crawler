# memcache

## install
```sh
$  pip install python-memcached
```

## usage
```python
import memcached
db = memcache.Client(['127.0.0.1:11211'])
db.set('name', '太郎')
db.get('name')
```