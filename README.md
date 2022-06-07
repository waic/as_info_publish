# AS情報 公開用ツール

results_master_yyyymmdd.xlsx をダウンロードしてカレントディレクトリに移動します。

```
$ python3.9 -m venv venv
$ source venv/bin/activate
$ python -m pip install -r requirements.txt
$ python results_csv_to_yaml.py --src results_master_yyyymmdd.xlsx --dest results_new.yaml
```

results_new.yaml を as_info の data/results.yaml に追記します。

