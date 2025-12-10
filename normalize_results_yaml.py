#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "ruamel.yaml",
# ]
# ///
"""
results.yaml を正規化するスクリプト

以下の処理を行います:
- 空文字列を null として扱い、コロンの右を空にする
- バックスラッシュ付き \n を実際の改行に変換
- 改行を含む文字列をリテラルブロック形式 (|-) に統一
"""

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString
import sys
import os


def normalize_results_yaml(input_path, output_path=None):
    """
    results.yaml を正規化する
    
    Args:
        input_path: 入力ファイルパス
        output_path: 出力ファイルパス（None の場合は入力ファイルを上書き）
    """
    if output_path is None:
        output_path = input_path
    
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    
    def none_representer(repr, data):
        # null/空値はコロンの右を空にする
        return repr.represent_scalar('tag:yaml.org,2002:null', '')
    
    yaml.Representer.add_representer(type(None), none_representer)
    
    def normalize(obj):
        if isinstance(obj, dict):
            for k, v in list(obj.items()):
                obj[k] = normalize(v)
            return obj
        if isinstance(obj, list):
            for i, v in enumerate(obj):
                obj[i] = normalize(v)
            return obj
        if isinstance(obj, str):
            if obj == '':
                return None  # 空文字をnull扱いにして空スカラー出力
            s = obj.replace('\\n', '\n') if '\\n' in obj else obj
            if '\n' in s:
                return LiteralScalarString(s)
            return s
        return obj
    
    # ファイルを読み込む
    with open(input_path, 'r', encoding='utf-8') as f:
        data = yaml.load(f)
    
    # 正規化
    data = normalize(data)
    
    # ファイルに書き込む
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)
    
    print(f"正規化完了: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("使用方法: uv run normalize_results_yaml.py <入力ファイル> [出力ファイル]")
        print("例: uv run normalize_results_yaml.py ../as_info/data/results.yaml")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_path):
        print(f"エラー: ファイルが見つかりません: {input_path}")
        sys.exit(1)
    
    normalize_results_yaml(input_path, output_path)


if __name__ == '__main__':
    main()

