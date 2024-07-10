# AS情報 公開用ツール

results_yyyymmdd.xlsx をダウンロードしてカレントディレクトリに移動します。

```
$ python3.12 -m venv venv
$ source venv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
$ python xlsx_to_yaml.py results_yyyymmdd.xlsx --output results_new.yaml
```

results_new.yaml を as_info の data/results.yaml に追記します。

