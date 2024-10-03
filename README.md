# AS情報 公開用ツール

## results.yaml

results_yyyymmdd.xlsx をダウンロードしてカレントディレクトリに移動します。

```
$ python3.12 -m venv venv
$ source venv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
$ python xlsx_to_yaml.py results_yyyymmdd.xlsx --output results_new.yaml
```

results_new.yaml を as_info の data/results.yaml に追記します。

## tests.yaml

https://docs.astral.sh/uv/

相対パスで as_test を参照して作成します。

```
% ls -1 ../as_test
README.md
WAIC-CODE
WAIC-TEST
cgi-bin
notification
term.md

% uv run make_tests.py
```

一部は変換が不完全で、手作業で修正して as_info/data/tests.yaml に取り込んでいます。
