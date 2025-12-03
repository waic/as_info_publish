# AS情報 公開用ツール

このリポジトリは、AS情報（アクセシビリティサポーテッド情報）の公開用データを生成・管理するためのツール集です。

**コーディングAIで作業する場合は、[AGENTS.md](AGENTS.md) を必ず参照してください。**

## results.yaml

results_yyyymmdd.xlsx をダウンロードしてカレントディレクトリに移動します。

```
$ uv run xlsx_to_yaml.py results_yyyymmdd.xlsx --output results_new.yaml
```

results_new.yaml を as_info の data/results.yaml に追記します。

**詳細な手順や注意事項は [AGENTS.md](AGENTS.md) を参照してください。**

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
