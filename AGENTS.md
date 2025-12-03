# AGENTS.md

このファイルは、コーディングAI（Claude Code など）がこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

基本的な使用方法は [README.md](README.md) を参照してください。このファイルは、コーディングAIが作業する際の詳細なガイダンスを提供します。

## プロジェクト構造

- `xlsx_to_yaml.py` - Google スプレッドシートからエクスポートした xlsx ファイルを YAML 形式に変換
- `make_results.py` - CSV から results.yaml を生成（旧形式）
- `make_tests.py` - as_test リポジトリから tests.yaml を生成
- `results_csv_to_yaml.py` - CSV/XLSX から results.yaml を生成
- `results_yaml_to_csv.py` - results.yaml から CSV/XLSX を生成

## results.yaml への追加作業

### 基本的な作業手順

基本的な手順は [README.md](README.md) を参照してください。以下は詳細な説明です。

1. **xlsx ファイルのエクスポート**
   - Google スプレッドシートから `results_yyyymmdd.xlsx` をエクスポート
   - カレントディレクトリに配置

2. **YAML への変換**
   ```bash
   uv run xlsx_to_yaml.py results_yyyymmdd.xlsx --output results_new.yaml
   ```

3. **results.yaml への追記**
   - `results_new.yaml` を確認
   - 必要な ID 範囲を抽出して `../as_info/data/results.yaml` に追記

### 重要な注意事項

#### 1. 列構造の違いへの対応

xlsx ファイルには2つの構造があります：

- **43列構造**（既存）: `results_20241010_v2.xlsx` など
- **44列構造**（新規）: `results_20250205.xlsx` など
  - 「視覚閲覧環境、音声閲覧環境の種別」列が追加されている（9番目の列）

`xlsx_to_yaml.py` は自動的に列数を検出し、適切にマッピングします。

#### 2. 空フィールドの表記統一

**既存データの形式を維持することが重要です。**

- 既存データ: `key:` （値なしの形式）
- 新規データも同じ形式で出力する必要がある

`xlsx_to_yaml.py` の `dump_yaml_with_empty_keys()` 関数が、`null` を `key:` 形式に変換します。

#### 3. 既存データとの互換性

- 既存の `results.yaml` の形式（`key:`）を変更しない
- 新規データも同じ形式で出力する
- `yaml.safe_dump()` は `null` を出力するため、後処理で `: null` を `:` に変換する必要がある

### コーディングAIへの指示

このリポジトリで作業する際は、以下の点に注意してください：

1. **既存データの形式を維持する**
   - 空フィールドは `key:` 形式（値なし）で出力する
   - `key: null` や `key: ''` ではなく、`key:` とする

2. **列構造の違いに対応する**
   - xlsx ファイルの列数を確認する
   - 44列の場合は「視覚閲覧環境、音声閲覧環境の種別」列を無視する

3. **データの整合性を確認する**
   - 変換後の YAML ファイルを確認する
   - 既存の `results.yaml` と形式が一致しているか確認する
   - git diff で変更内容を確認する

4. **バックアップを作成する**
   - `results.yaml` を更新する前にバックアップを作成する

### トラブルシューティング

#### 問題: 空フィールドが `null` として出力される

**解決方法**: `dump_yaml_with_empty_keys()` 関数が正しく動作しているか確認する。この関数は `: null` を `:` に変換します。

#### 問題: 列数が合わないエラーが発生する

**解決方法**: xlsx ファイルの列数を確認する。44列の場合は自動的に処理されますが、それ以外の場合は警告が表示されます。

#### 問題: 既存データの形式が変わってしまう

**解決方法**: 
1. git で既存の `results.yaml` を確認する
2. `dump_yaml_with_empty_keys()` 関数を使用する
3. git diff で変更内容を確認する

### 開発コマンド

```bash
# xlsx を YAML に変換
uv run xlsx_to_yaml.py results_yyyymmdd.xlsx --output results_new.yaml

# 変換結果を確認
head -50 results_new.yaml

# 既存の results.yaml を確認
head -50 ../as_info/data/results.yaml

# 変更内容を確認
git -C ../as_info diff data/results.yaml
```

### 参考情報

- `as_test/CLAUDE.md` - as_test リポジトリのガイダンス
- `README.md` - 基本的な使用方法

