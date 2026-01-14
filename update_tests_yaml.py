#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "ruamel.yaml",
# ]
# ///
"""
生成された tests.yaml を as_info の tests.yaml に更新するスクリプト

使用方法:
  uv run update_tests_yaml.py [生成されたtests.yamlのパス] [既存のtests.yamlのパス]

例:
  uv run update_tests_yaml.py
  uv run update_tests_yaml.py tests.yaml ../as_info/src/content/tests/tests.yaml
"""
from ruamel.yaml import YAML
import sys
import os

def update_tests_yaml(new_tests_file='tests.yaml', existing_tests_path=None):
    """
    生成された tests.yaml を既存の tests.yaml に更新する
    
    Args:
        new_tests_file: 生成された tests.yaml のパス
        existing_tests_path: 既存の tests.yaml のパス（None の場合はデフォルトパス）
    """
    if existing_tests_path is None:
        existing_tests_path = '../as_info/src/content/tests/tests.yaml'
    
    # ruamel.yaml を使用
    yaml_ruamel = YAML()
    yaml_ruamel.preserve_quotes = True
    yaml_ruamel.width = 4096
    yaml_ruamel.indent(mapping=2, sequence=2, offset=0)  # 一貫性のため results.yaml と同じ2スペースに統一
    yaml_ruamel.default_flow_style = False
    yaml_ruamel.allow_unicode = True
    
    # 生成された tests.yaml を読み込む
    if not os.path.exists(new_tests_file):
        print(f"エラー: ファイルが見つかりません: {new_tests_file}")
        print("まず 'uv run make_tests.py' を実行して tests.yaml を生成してください。")
        sys.exit(1)
    
    with open(new_tests_file, 'r', encoding='utf-8') as f:
        new_data = yaml_ruamel.load(f) or {}
    
    print(f'生成された tests.yaml: {len(new_data)} 件')
    
    # 既存の tests.yaml を読み込む（存在する場合）
    existing_data = {}
    if os.path.exists(existing_tests_path):
        with open(existing_tests_path, 'r', encoding='utf-8') as f:
            existing_data = yaml_ruamel.load(f) or {}
        print(f'既存の tests.yaml: {len(existing_data)} 件')
    
    # 更新されたテスト数を確認
    updated_count = 0
    new_count = 0
    for test_id in new_data:
        if test_id in existing_data:
            updated_count += 1
        else:
            new_count += 1
    
    print(f'\n更新されるテスト: {updated_count} 件')
    print(f'新規追加されるテスト: {new_count} 件')
    
    # ファイルに書き込む（既存のインデント形式を維持）
    with open(existing_tests_path, 'w', encoding='utf-8') as f:
        yaml_ruamel.dump(new_data, f)
    
    print(f'\n更新完了: {existing_tests_path}')
    print(f'総テスト数: {len(new_data)} 件')

def main():
    if len(sys.argv) > 1:
        new_tests_file = sys.argv[1]
    else:
        new_tests_file = 'tests.yaml'
    
    if len(sys.argv) > 2:
        existing_tests_path = sys.argv[2]
    else:
        existing_tests_path = None
    
    update_tests_yaml(new_tests_file, existing_tests_path)

if __name__ == '__main__':
    main()
