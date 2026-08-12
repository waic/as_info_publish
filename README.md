# AS情報 公開用ツール

このリポジトリは、AS情報（アクセシビリティサポーテッド情報）の公開用データを生成・管理するためのツール集です。

## セットアップ（Python をインストールしていない人向け）

このツールは Python スクリプトでできていますが、**Python 本体を事前にインストールする必要はありません**。[uv](https://docs.astral.sh/uv/) さえあれば、必要な Python と依存パッケージを自動で用意してくれます。

### 1. uv をインストールする

macOS / Linux の場合:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows の場合:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.sh | iex"
```

インストール後、ターミナルを開き直して動作を確認します。

```bash
uv --version
```

### 2. スクリプトの実行方法

以下のように `uv run` で実行します。`uv run` は、各スクリプトの依存パッケージを自動で解決・インストールしてから実行するため、**pip install などの準備は不要**です。

```bash
uv run <スクリプト名>.py ...
```

> **補足**: `pyproject.toml`（`uv sync`）はこのリポジトリでは使いません。各スクリプトが依存を自己宣言しているため、`uv run` だけで完結します。

## 使い方

具体的な操作手順は、[update_guide.md](update_guide.md) を参照してください。

### results.yaml の更新

```bash
# xlsx → YAML 変換
uv run xlsx_to_yaml.py results_yyyymmdd.xlsx --output results_new.yaml

# 新規データを既存 results.yaml に追加
uv run append_results.py results_new.yaml

# as_info の分割ファイルへ反映（必須）
cd ../as_info
npx tsx scripts/split-results.ts
cd ../as_info_publish
```

### tests.yaml の更新

```bash
# as_test から tests.yaml を生成
uv run make_tests.py

# as_info の tests.yaml へ更新
uv run update_tests_yaml.py
```

## ツール一覧

- `xlsx_to_yaml.py` - Google スプレッドシートからエクスポートした xlsx ファイルを YAML 形式に変換
- `append_results.py` - 新規データの YAML ファイルを既存の results.yaml に追加
- `backfill_environment_type.py` - 既存の results.yaml に environment_type をバックフィル
- `normalize_yaml.py` - YAML ファイルを正規化（results.yaml, techs.yaml などに適用可能）
- `make_tests.py` - as_test リポジトリから tests.yaml を生成
- `update_tests_yaml.py` - 生成された tests.yaml を as_info の tests.yaml に更新
- `results_yaml_to_csv.py` - results.yaml から CSV/XLSX を生成
- `yaml_dumpers.py` - YAML 出力時の共通ダンパー（空キー形式 `key:` やリテラルブロック出力用）

## 注意

- as_info の results データは**IDごとの分割ファイル**（`src/content/results/{NNNN}/{NNNN}.yaml`）で管理しています。`append_results.py` は単一 `results.yaml` を出力するため、追記後に `split-results.ts` で分割する必要があります。
- 詳細な手順・注意事項・トラブルシューティングは [update_guide.md](update_guide.md) を参照してください。
