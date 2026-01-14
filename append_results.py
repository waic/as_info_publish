#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "PyYAML",
# ]
# ///
"""
既存の results.yaml に新規データを追加するスクリプト

使用方法:
  uv run append_results.py <新規データのYAMLファイル> [既存のresults.yamlのパス]

例:
  uv run append_results.py results_new.yaml
  uv run append_results.py results_new.yaml ../as_info/src/content/results/results.yaml
"""
import yaml
import sys
import os
import re

def append_results(new_data_file, results_yaml_path=None):
    """
    新規データを既存の results.yaml に追加する
    
    Args:
        new_data_file: 新規データのYAMLファイルパス
        results_yaml_path: 既存の results.yaml のパス（None の場合はデフォルトパス）
    """
    if results_yaml_path is None:
        results_yaml_path = '../as_info/src/content/results/results.yaml'
    
    # 既存の results.yaml を読み込む
    if not os.path.exists(results_yaml_path):
        print(f"エラー: ファイルが見つかりません: {results_yaml_path}")
        sys.exit(1)
    
    with open(results_yaml_path, 'r', encoding='utf-8') as f:
        existing_data = yaml.safe_load(f)
    
    existing_ids = set([item['id'] for item in existing_data if 'id' in item])
    print(f'既存の results.yaml: {len(existing_data)} 件 (ID {min(existing_ids)} - {max(existing_ids)})')
    
    # 新規データを読み込む
    if not os.path.exists(new_data_file):
        print(f"エラー: ファイルが見つかりません: {new_data_file}")
        sys.exit(1)
    
    with open(new_data_file, 'r', encoding='utf-8') as f:
        new_data = yaml.safe_load(f)
    
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
    
    # 既存データに追加
    existing_data.extend(new_entries)
    
    # IDでソート（オプション）
    existing_data.sort(key=lambda x: x.get('id', 0))
    
    # ファイルに書き込む（既存の形式を保持）
    yaml_str = yaml.safe_dump(
        existing_data,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
    
    # : null を : に変換（既存データの形式に合わせる）
    lines = yaml_str.split('\n')
    result_lines = []
    
    for line in lines:
        # 行末の : null を : に変換
        if re.match(r'^(\s+)([^:]+):\s+null\s*$', line):
            result_lines.append(re.sub(r':\s+null\s*$', ':', line))
        else:
            result_lines.append(line)
    
    with open(results_yaml_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result_lines))
    
    print(f'\n追記完了: {results_yaml_path}')
    print(f'総エントリ数: {len(existing_data)} 件')
    print(f'ID 範囲: {min([item["id"] for item in existing_data])} - {max([item["id"] for item in existing_data])}')

def main():
    if len(sys.argv) < 2:
        print("使用方法: uv run append_results.py <新規データのYAMLファイル> [既存のresults.yamlのパス]")
        print("例: uv run append_results.py results_new.yaml")
        print("例: uv run append_results.py results_new.yaml ../as_info/src/content/results/results.yaml")
        sys.exit(1)
    
    new_data_file = sys.argv[1]
    results_yaml_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    append_results(new_data_file, results_yaml_path)

if __name__ == '__main__':
    main()
