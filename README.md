# AS情報 公開用ツール

このリポジトリは、AS情報（アクセシビリティサポーテッド情報）の公開用データを生成・管理するためのツール集です。

**コーディングAIで作業する場合は、[AGENTS.md](AGENTS.md) を必ず参照してください。**

## results.yaml

results_yyyymmdd.xlsx をダウンロードしてカレントディレクトリに移動します。

```
$ uv run xlsx_to_yaml.py results_yyyymmdd.xlsx --output results_new.yaml
```

新規データを既存の results.yaml に追加します：

```
$ uv run append_results.py results_new.yaml
```

既存のIDは自動的にスキップされ、新規IDのみが追加されます。

**詳細な手順や注意事項は [AGENTS.md](AGENTS.md) を参照してください。**

## tests.yaml

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

生成された `tests.yaml` を確認し、必要に応じて `as_info/src/content/tests/tests.yaml` に取り込みます。

**詳細な手順や注意事項は [AGENTS.md](AGENTS.md) を参照してください。**

### 制限事項

`make_tests.py` は以下のセクションが存在する Markdown ファイルのみを処理します：

- `# テスト ID` - 必須
- `# テストのタイトル` - 必須
- `# テストコード (テストファイルへのリンク)` - 必須

「# テストコード (テストファイルへのリンク)」セクションがないテストは生成されません。このようなテストがある場合は、`as_test` リポジトリの Markdown ファイルを修正する必要があります。
