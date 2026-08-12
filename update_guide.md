# AS情報更新フロー 手順書

- 目的: AS情報更新フローの手順を共有する（属人化解消）
- 形式: ハンズオンで実際に操作しながら学べる
- 環境: この手順書は **macOS / Linux / WSL** を想定しています。Windows（PowerShell）の場合はパス区切りやコマンドを適宜読み替えてください。
- 前提: ローカルに 3 リポジトリ（`as_info` / `as_info_publish` / `as_test`）を clone する
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
results_new.yaml ──► as_info のID分割ファイルへ直接追加
                    append_results.py
        │
        ▼
as_info/src/content/results/{NNNN}/{NNNN}.yaml

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
3. `append_results.py` で新規データを **as_info の ID ごとの分割ファイル**（`src/content/results/{NNNN}/{NNNN}.yaml`）に直接追加します。
4. 一方、as_test のテストケース（`WAIC-TEST/*.md`）から `make_tests.py` で `tests.yaml` を生成し、`update_tests_yaml.py` で as_info の `src/content/tests/tests.yaml` に反映します。
5. as_info リポジトリで `npm run dev` や `npm run build` を実行すると、静的サイト（`docs/`）が生成され、デプロイされます。

データは最終的に `as_info/src/content/` 配下の YAML（Content Collections）として管理されます。

### 3 リポジトリの役割

更新フローには以下の 3 リポジトリが関わります。

- **`as_info_publish`**: 変換・更新ツール集（xlsx→yaml、分割ファイルへの追加、tests 生成など）。この手順書のスクリプトを実行する場所です。
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

> as_info 側の管理ツール（参考）:
> - 分割: `npx tsx scripts/split-results.ts`
> - 結合（逆操作）: `npx tsx scripts/merge-results.ts`
> - ソート: `npx tsx scripts/sort-data.ts`
>
> この手順の更新フローでは `append_results.py` が直接分割ファイルを書くため、
> 通常は `split-results.ts` を実行する必要はありません。

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

### 1-3. リポジトリの取得（clone）

3 つのリポジトリを **同じ親ディレクトリ配下** に clone し、相対参照できるようにします。

```bash
git clone https://github.com/waic/as_info.git
git clone https://github.com/waic/as_info_publish.git
git clone https://github.com/waic/as_test.git
```

これにより、以下の相対パスで参照できます（この手順書の前提と同じ配置）。

```
（任意のディレクトリ）/
├── as_info/
├── as_info_publish/
└── as_test/
```

> as_info_publish のスクリプトは `../as_info` や `../as_test` を相対パスで参照するため、
> 3 リポジトリを同じ親ディレクトリ配下に置く必要があります。
>
> 以降の手順は **`as_info_publish` をカレントディレクトリとして実行** します。
> clone 後は `cd as_info_publish` してください。

### 1-4. as_info の依存関係インストール

```bash
cd ../as_info
npm install        # node_modules を作成
cd ../as_info_publish
```

> as_info_publish のスクリプトは `uv run` で実行するため個別の pip install は不要です。

### 1-5. 作業用ブランチの作成（PR を出す場合の推奨）

PR を出して変更を共有する場合は、as_info で作業用ブランチを作成します。

```bash
cd ../as_info
git checkout -b update/as-results-2026
```

> - master ブランチには直接コミットしない運用です（as_info の README 参照）。
> - ブランチ作成は **PR を出す場合の推奨** であり、ローカルで動作確認するだけなら必須ではありません。
> - as_info_publish（ツール）と as_test（テストケース）は、ハンズオンでは
>   変更しないためブランチ作成は不要です。

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

> **パスの指定について**: 第1引数に xlsx の**パス**を指定できます。カレントディレクトリのファイルだけでなく、`examples/` 配下のサンプルデータもそのまま参照できます。
>
> ```bash
> # ハンズオン用サンプル（examples/ 配下）を直接使う場合
> uv run xlsx_to_yaml.py examples/results_20260812.xlsx --output results_new.yaml
> ```

- 列数（43列/44列）を自動検出します。
- 44列の場合、「視覚閲覧環境、音声閲覧環境の種別」列から `environment_type` を抽出します。
- 出力を確認:

```bash
head -50 results_new.yaml
```

### 2-3. as_info の分割ファイルに追加

```bash
uv run append_results.py results_new.yaml
```

- **第1引数 `results_new.yaml` は入力**です（2-2 で `xlsx_to_yaml.py` が生成した新規データ）。
- 新規データを **as_info の ID ごとの分割ファイル**（`src/content/results/{NNNN}/{NNNN}.yaml`）に直接追加します。
- **第2引数（省略可）は出力先の results ディレクトリ（フォルダ）** です。省略時は `../as_info/src/content/results` に固定。
  ```bash
  # 出力先ディレクトリを明示的に指定する場合
  uv run append_results.py results_new.yaml ../as_info/src/content/results
  ```
- 既存 ID は自動的にスキップされ、新規 ID のみ追加されます。
- 単一 `results.yaml` は生成しません。

### 2-4. 差分の確認

```bash
git -C ../as_info diff src/content/results/
```

- 追加・変更された分割ファイルのみが差分に出ていることを確認します。
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

> **注**: results の分割ファイル（`results/{NNNN}/{NNNN}.yaml`）は
> `append_results.py` が正規化（リテラルブロック・空値の `key:` 形式）を
> 組み込み済みのため、`normalize_yaml.py` を適用する必要はありません。
> `normalize_yaml.py` は単一 YAML（`results.yaml` など）用です。

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
cd ../as_info
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
   > ハンズオンでは as_info 側のデータ更新のみをコミットします。
   > as_info_publish のツール（スクリプト）の変更は、通常は別途コミット・
   > レビューしますが、ハンズオンの練習では対象外です。

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

1. `examples/results_20260812.xlsx`（公開用サンプル）を使って、
   `xlsx_to_yaml.py` → `append_results.py` の一連の流れを確認する。
   ```bash
   cd ../as_info_publish
   uv run xlsx_to_yaml.py examples/results_20260812.xlsx --output results_new.yaml
   # 出力先を一時ディレクトリに指定して、as_info を汚さないようにする
   uv run append_results.py results_new.yaml /tmp/handson_results
   ```
   ※ 実際にコミットせず、動作確認のみ実施すること。`/tmp/handson_results` に
   分割ファイルが生成されることを確認します。

2. `make_tests.py` と `update_tests_yaml.py` を実行して、生成件数と差分を確認する。

3. `append_results.py` を再実行し、既存 ID がスキップされること（重複追加されないこと）を確認する。

---

## 付録A. よくあるエラーと対処

以下の症状と対処を確認してください。

- **`uv: command not found`**: uv をインストールします（`brew install uv` など）。
- **空フィールドが `null` と出力される**: `xlsx_to_yaml.py` / `append_results.py` の `key:` 変換処理を確認します。
- **列数が合わないエラー**: xlsx の列数を確認します（44列想定。それ以外は警告）。
- **append_results でディレクトリが見つからない**: 引数に as_info の `src/content/results` ディレクトリを正しく指定しているか確認します。
- **期待したテストが生成されない**: `as_test` の Markdown に必須セクション（テストコードへのリンク）があるか確認します。
- **node コマンドで `npx: command not found`**: `npm install` を実行します。

## 付録B. 便利コマンド集

```bash
# xlsx → YAML 変換
uv run xlsx_to_yaml.py results_yyyymmdd.xlsx --output results_new.yaml

# 新規データを as_info の分割ファイルへ直接追加
uv run append_results.py results_new.yaml

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
