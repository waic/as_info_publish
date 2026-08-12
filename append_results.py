#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "PyYAML",
# ]
# ///
"""
既存の as_info results 分割ファイルに新規データを追加するスクリプト

as_info リポジトリでは results データを ID ごとの分割ファイル
（src/content/results/{NNNN}/{NNNN}.yaml、100件ごとにサブフォルダ分割）で
管理しています。本スクリプトは新規データを直接、既存の分割ファイルに
追記・作成します（単一 results.yaml は使いません）。

使用方法:
  uv run append_results.py <新規データのYAMLファイル> [as_infoのresultsディレクトリ]

例:
  uv run append_results.py results_new.yaml
  uv run append_results.py results_new.yaml ../as_info/src/content/results
"""
import yaml
import sys
import os
import re
from yaml_dumpers import represent_str, represent_none

# safe_dump で改行あり文字列をリテラルブロック（|）で、空値を key: で出力する
yaml.SafeDumper.add_representer(str, represent_str)
yaml.SafeDumper.add_representer(type(None), represent_none)


def folder_for(id_num):
    """id 1..100 -> 0001, id 101..200 -> 0101, ..."""
    start = (id_num - 1) // 100 * 100 + 1
    return f"{start:04d}"


def normalize_value(obj):
    """
    値の正規化（normalize_yaml.py の normalize() 相当）。
    - 空文字列 → None（空スカラーとして出力）
    - '\\n' エスケープ → 実際の改行に変換
    - 改行を含む文字列はリテラルブロック（|）形式で出力
    """
    if isinstance(obj, dict):
        return {k: normalize_value(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_value(v) for v in obj]
    if isinstance(obj, str):
        if obj == '':
            return None
        s = obj.replace('\\n', '\n') if '\\n' in obj else obj
        return s
    return obj


def dump_single_entry(entry):
    """
    1エントリを分割ファイル形式で出力する。

    既存の分割ファイル形式に合わせる:
      - 配列の先頭 `-` プレフィックスを付けない（単一オブジェクト）
      - 空フィールドは `key:` 形式（値なし）
      - 改行を含む文字列はリテラルブロック（|）形式
    """
    # 正規化を適用（空文字→None、\n→実改行）
    entry = normalize_value(entry)

    yaml_str = yaml.safe_dump(
        entry,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
    # : null を : に変換（既存データの形式に合わせる）
    lines = yaml_str.split('\n')
    result_lines = []
    for line in lines:
        # 行末の : null を : に変換
        if re.match(r'^(\s*)([^:]+):\s+null\s*$', line):
            result_lines.append(re.sub(r':\s+null\s*$', ':', line))
        else:
            result_lines.append(line)
    return '\n'.join(result_lines)


def append_results(new_data_file, results_dir=None):
    """
    新規データを既存の分割ファイルに追加する

    Args:
        new_data_file: 新規データのYAMLファイルパス
        results_dir: as_info の results ディレクトリ（None の場合はデフォルトパス）
    """
    if results_dir is None:
        results_dir = '../as_info/src/content/results'

    if not os.path.isdir(results_dir):
        print(f"エラー: ディレクトリが見つかりません: {results_dir}")
        sys.exit(1)

    # 新規データを読み込む
    if not os.path.exists(new_data_file):
        print(f"エラー: ファイルが見つかりません: {new_data_file}")
        sys.exit(1)

    with open(new_data_file, 'r', encoding='utf-8') as f:
        new_data = yaml.safe_load(f)

    # 既存の ID を収集（全フォルダの分割ファイルを走査）
    existing_ids = set()
    existing_count = 0
    for folder in sorted(os.listdir(results_dir)):
        folder_path = os.path.join(results_dir, folder)
        if not os.path.isdir(folder_path) or not re.match(r'^\d{4}$', folder):
            continue
        for fname in os.listdir(folder_path):
            if re.match(r'^\d{4}\.yaml$', fname):
                existing_count += 1
                existing_ids.add(int(fname[:4]))

    if existing_ids:
        print(f'既存の分割ファイル: {existing_count} 件 (ID {min(existing_ids)} - {max(existing_ids)})')
    else:
        print(f'既存の分割ファイル: 0 件（新規作成）')

    # 新規データから既存にないIDを抽出
    new_entries = []
    for item in new_data:
        if 'id' in item:
            item_id = item['id']
            if item_id not in existing_ids:
                new_entries.append(item)
            else:
                print(f'警告: ID {item_id} は既に存在します。スキップします。')

    if not new_entries:
        print('追加する新規データがありません。')
        return

    print(f'\n追加する新規データ: {len(new_entries)} 件')
    new_ids = [item['id'] for item in new_entries]
    print(f'ID 範囲: {min(new_ids)} - {max(new_ids)}')

    # 各新規エントリを分割ファイルとして書き込む
    written = []
    for entry in new_entries:
        id_num = entry['id']
        folder = folder_for(id_num)
        folder_path = os.path.join(results_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{id_num:04d}.yaml")
        content = dump_single_entry(entry)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        written.append(file_path)

    print(f'\n追加完了: {len(written)} 件')
    print(f'追加されたファイル:')
    for fp in written:
        print(f'  {fp}')


def main():
    if len(sys.argv) < 2:
        print("使用方法: uv run append_results.py <新規データのYAMLファイル> [as_infoのresultsディレクトリ]")
        print("例: uv run append_results.py results_new.yaml")
        print("例: uv run append_results.py results_new.yaml ../as_info/src/content/results")
        sys.exit(1)

    new_data_file = sys.argv[1]
    results_dir = sys.argv[2] if len(sys.argv) > 2 else None

    append_results(new_data_file, results_dir)


if __name__ == '__main__':
    main()
