# AS情報更新フロー 手順書

- 目的: AS情報更新フローの手順を共有する（属人化解消）
- 形式: ハンズオンで実際に操作しながら学べる
- 前提: ローカルに 3 リポジトリ（`as_info` / `as_info_publish` / `as_test`）を clone 済み
  - 相対パス配置: `as_info` と `as_test` は `as_info_publish` と同じ親ディレクトリ配下

---

## 0. 更新フロー全体像

```
[Google スプレッドシート]
        │ エクスポート
        ▼
results_yyyymmdd.xlsx
        │ xlsx_to_yaml.py
        ▼
results_new.yaml ──┬─► (a) results.yaml への追記
        │            append_results.py
        └─► (b) as_info のID分割ファイルへ反映
                   split-results.ts

[as_test リポジトリ] (WAIC-TEST/*.md)
        │ make_tests.py
        ▼
tests.yaml ── update_tests_yaml.py ──► as_info/src/content/tests/tests.yaml

[as_info リポジトリ] (Astro 静的サイト)
        │ npm run dev / npm run build
        ▼
docs/ ──► デプロイ
```

**図の解説（文字で表した処理の流れ）:**

この図は、テスト結果データとテストケース情報が最終的に as_info の公開サイトに反映されるまでの流れを表しています。

1. Google スプレッドシートに記入されたテスト結果を `results_yyyymmdd.xlsx` としてエクスポートします。
2. `xlsx_to_yaml.py` で xlsx を `results_new.yaml` に変換します。
3. 変換結果は `append_results.py` で既存の `results.yaml` に追記され、`split-results.ts` で as_info の ID 分割ファイルへ反映されます。
4. 一方、as_test のテストケース（`WAIC-TEST/*.md`）から `make_tests.py` で `tests.yaml` を生成し、`update_tests_yaml.py` で as_info の `src/content/tests/tests.yaml` に反映します。
5. as_info リポジトリで `npm run dev` や `npm run build` を実行すると、静的サイト（`docs/`）が生成され、デプロイされます。

データは最終的に `as_info/src/content/` 配下の YAML（Content Collections）として管理されます。

### 3 リポジトリの役割

更新フローには以下の 3 リポジトリが関わります。

- **`as_info_publish`**: 変換・更新ツール集（xlsx→yaml、yaml マージ、tests 生成など）。この手順書のスクリプトを実行する場所です。
- **`as_info`**: Astro 静的サイト本体。公開データ（results / tests / criteria / techs / metadata）とビルド設定を管理します。
- **`as_test`**: テストケース（`WAIC-TEST/`）とテストコード（`WAIC-CODE/`）の元データを管理します。

### as_info のデータ構造（重要）

`results` は**1レコード1ファイル**で管理し、**100件ごとにサブフォルダ分割**されています。

```
as_info/src/content/results/
├── 0001/          # id 1〜100
│   ├── 0001.yaml
│   └── ...
├── 0101/          # id 101〜200
│   ├── 0101.yaml
│   └── ...
└── ...
```

**図の解説（ディレクトリ構造）:**

- `as_info/src/content/results/` 配下に、テスト結果を ID ごとに 1 ファイルずつ格納します。
- ファイル名はゼロ埋め 4 桁の ID（例: `0001.yaml`）。
- ID 100 件ごとにサブフォルダを分けます（`0001/` は ID 1〜100、`0101/` は ID 101〜200）。

- 分割: `npx tsx scripts/split-results.ts`
- 結合（逆操作）: `npx tsx scripts/merge-results.ts`
- ソート: `npx tsx scripts/sort-data.ts`

---

## 1. 事前準備（各自の環境で一度だけ実施）

### 1-1. ツールの確認

```bash
# Python パッケージ管理ツール uv（as_info_publish のスクリプト実行に必要）
uv --version

# Node.js（as_info のビルド・スクリプトに必要）
node --version
npm --version
```

### 1-2. uv のセットアップ（Python をインストールしていない人）

このツールの Python スクリプトは `uv run` で実行します。**Python 本体は不要**で、`uv` が管理する Python と依存パッケージを自動で用意します。

- **uv が無い場合**: [README のセットアップ](README.md) に従って uv をインストールします。
  - macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.sh | iex"`
- **uv はあるが Python が無い場合**: 何もする必要はありません。`uv run` が自動で Python を取得します。

### 1-3. as_info の依存関係インストール

```bash
cd ../as_info
npm install        # node_modules を作成
```

> as_info_publish のスクリプトは `uv run` で実行するため個別の pip install は不要です。

### 1-3. 作業用ブランチの作成（PR 前提の運用）

```bash
# as_info 側
cd ../as_info
git checkout -b update/as-results-2026
```

> master ブランチには直接コミットしない運用です（as_info の README 参照）。

---

## 2. テスト結果（results.yaml）の更新フロー

### 2-1. スプレッドシートから xlsx をエクスポート

Google スプレッドシート（結果入力フォーム）から最新結果を
`results_yyyymmdd.xlsx` としてエクスポートし、`as_info_publish` ディレクトリに配置します。

```bash
cd ../as_info_publish
# 例: results_20260812.xlsx を配置したとする
```

### 2-2. xlsx → YAML に変換

```bash
uv run xlsx_to_yaml.py results_20260812.xlsx --output results_new.yaml
```

- 列数（43列/44列）を自動検出します。
- 44列の場合、「視覚閲覧環境、音声閲覧環境の種別」列から `environment_type` を抽出します。
- 出力を確認:

```bash
head -50 results_new.yaml
```

### 2-3. 既存 results.yaml に追記

```bash
uv run append_results.py results_new.yaml
```

- 既存 ID は自動的にスキップされ、新規 ID のみ追加されます。
- デフォルトで `../as_info/src/content/results/results.yaml` に書き込みます（単一ファイルとして生成）。

### 2-4. 単一ファイル → 分割ファイルに反映（重要）

`append_results.py` は単一の `results.yaml` を出力しますが、as_info の運用は
**ID ごとの分割ファイル**です。追記後は分割処理を実行します。

```bash
cd ../as_info
npx tsx scripts/split-results.ts
```

これにより `src/content/results/{NNNN}/{NNNN}.yaml` が生成/更新されます。

> 補足: 万一既存の単一 `results.yaml` が残っている場合は、コミット前に
> `rm src/content/results/results.yaml` で削除してください（分割ファイルが正）。

### 2-5. environment_type のバックフィル（必要に応じて）

`environment_type` が未設定の既存データを補完します。

```bash
cd ../as_info_publish
uv run backfill_environment_type.py ../as_info/src/content/results/results.yaml
```

### 2-6. 正規化

複数行の値をリテラルブロック（`|-`）形式に統一し、空フィールドを `key:` 形式に整えます。

```bash
uv run normalize_yaml.py ../as_info/src/content/results/results.yaml
```

### 2-7. 差分の確認

```bash
git -C ../as_info diff src/content/results/
```

- 追加・変更されたレコードのみが差分に出ていることを確認します。
- 空フィールドが `key: null` ではなく `key:` になっていることを確認します。

---

## 3. テストケース（tests.yaml）の更新フロー

`as_test` リポジトリの Markdown ファイルから `tests.yaml` を生成し、as_info に反映します。

### 3-1. as_test の状態を確認

```bash
ls -1 ../as_test
```

`WAIC-TEST/` と `WAIC-CODE/` が存在することを確認します。

### 3-2. tests.yaml を生成

```bash
cd ../as_info_publish
uv run make_tests.py
```

カレントディレクトリに `tests.yaml` が生成されます。

```bash
# 生成件数を確認（期待値と一致するか）
grep -c "^[0-9]" tests.yaml
head -50 tests.yaml
```

> **注意**: 現行 `make_tests.py` は生成できなかったテストの警告を表示しません。
> 生成件数が期待と合わない場合は、`as_test` の Markdown ファイルに
> 「# テストコード (テストファイルへのリンク)」等の必須セクションがあるか確認します。

### 3-3. as_info の tests.yaml に更新

```bash
uv run update_tests_yaml.py tests.yaml
```

- `../as_info/src/content/tests/tests.yaml` を更新します。
- `criteria` と `techs` も `as_test` の最新状態から更新されます。

### 3-4. 差分の確認

```bash
git -C ../as_info diff src/content/tests/tests.yaml
```

---

## 4. criteria / techs / metadata の更新（必要に応じて）

WCAG 達成基準や達成方法（テクニック集）、サイトのメタデータを更新する場合:

```bash
cd ../as_info
npx tsx scripts/sort-data.ts    # データの一貫性（ソート）を確保
```

- `src/content/criteria/criteria.yaml`
- `src/content/techs/techs.yaml`
- `src/content/metadata/metadata.yaml`

---

## 5. ローカルでプレビュー確認

更新内容をブラウザで確認します。

### 5-1. 開発サーバー起動

```bash
cd ../as_info
npm run dev
```

- ブラウザで `http://localhost:4321` を開きます。
- 変更が即時反映されます（HMR）。

### 5-2. 確認ポイント

- results の一覧・詳細ページに新規レコードが表示されるか
- tests ページが最新テストケースと一致するか
- リンクが切れていないか

---

## 6. 本番ビルドとプレビュー

### 6-1. 静的サイト生成

```bash
npm run build
```

- `./docs/` に静的 HTML が生成されます（`.html` 拡張子付き）。

### 6-2. プレビュー

```bash
npm run preview
```

### 6-3. GitHub Pages でのプレビュー公開（フォーカスエリアAのアクション）

ローカルだけでなく GitHub Pages で公開プレビューして全員で確認する手順:

1. 作業ブランチを push し、PR を作成します。
2. PR 経由でプレビューを共有します（as_info の GitHub Actions 設定に応じて）。

---

## 7. 変更の確定とデプロイ

1. **コミット**:
   ```bash
   git -C ../as_info add src/content/
   git -C ../as_info commit -m "AS情報の更新（results/tests）"
   ```

2. **push & PR**:
   ```bash
   git -C ../as_info push origin update/as-results-2026
   ```
   master への PR を作成します。

3. **レビュー**:
   - 作業者以外のメンバーがレビューします。
   - レビュアーは作業者が指名できます。

4. **マージ**:
   - 問題なければ master にマージします（ブランチは自動削除）。
   - App Engine へのデプロイは GitHub Actions が自動実行します（PR 作成時）。

---

## 8. ハンズオンの練習課題（時間がある場合）

1. `results_20250205.yaml`（as_info_publish 内にサンプルあり）を使って、
   `append_results.py` の動作を確認する。
   ```bash
   cd ../as_info_publish
   uv run append_results.py results_20250205.yaml
   ```
   ※ 実際にコミットせず、動作確認のみ実施すること。

2. `make_tests.py` と `update_tests_yaml.py` を実行して、生成件数と差分を確認する。

3. `split-results.ts` と `merge-results.ts` を交互に実行し、双方向変換が成立することを確認する。

---

## 付録A. よくあるエラーと対処

以下の症状と対処を確認してください。

- **`uv: command not found`**: uv をインストールします（`brew install uv` など）。
- **空フィールドが `null` と出力される**: `xlsx_to_yaml.py` / `normalize_yaml.py` の `key:` 変換処理を確認します。
- **列数が合わないエラー**: xlsx の列数を確認します（44列想定。それ以外は警告）。
- **split で `results.yaml` が無いエラー**: `append_results.py` で単一 `results.yaml` を生成してから分割します。
- **期待したテストが生成されない**: `as_test` の Markdown に必須セクション（テストコードへのリンク）があるか確認します。
- **node コマンドで `npx: command not found`**: `npm install` を実行します。

## 付録B. 便利コマンド集

```bash
# xlsx → YAML 変換
uv run xlsx_to_yaml.py results_yyyymmdd.xlsx --output results_new.yaml

# 新規データを既存 results.yaml に追加
uv run append_results.py results_new.yaml

# as_info の結果を分割形式へ反映
cd ../as_info && npx tsx scripts/split-results.ts

# environment_type をバックフィル
cd ../as_info_publish
uv run backfill_environment_type.py ../as_info/src/content/results/results.yaml

# YAML 正規化
uv run normalize_yaml.py ../as_info/src/content/results/results.yaml

# tests.yaml 生成と更新
uv run make_tests.py
uv run update_tests_yaml.py

# ビルド・プレビュー
cd ../as_info
npm run build
npm run preview

# 差分確認
git -C ../as_info diff src/content/
```
