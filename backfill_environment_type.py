#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "PyYAML",
#     "ruamel.yaml",
# ]
# ///
"""
既存の results.yaml に environment_type をバックフィルするスクリプト

assistive_tech から環境タイプを推測します:
- 「視覚閲覧環境」を含む場合 → 視覚閲覧環境
- NVDA、JAWS、VoiceOver、TalkBack、PC-Talker、ChromeVox など → 音声閲覧環境
- それ以外 → None（判断できない）
"""
import yaml
from collections import OrderedDict
import os
import sys
import re


def infer_environment_type(assistive_tech, comment=None):
    """
    assistive_tech と comment から環境タイプを推測する
    両方が含まれる場合は配列を返す
    """
    env_types = []
    
    # comment から判断
    comment_str = str(comment or '')
    has_visual_in_comment = '視覚閲覧環境' in comment_str
    has_audio_in_comment = '音声閲覧環境' in comment_str
    
    if has_visual_in_comment:
        env_types.append('視覚閲覧環境')
    if has_audio_in_comment:
        env_types.append('音声閲覧環境')
    
    # assistive_tech から判断（comment で判断できなかった場合のみ）
    if not env_types and assistive_tech:
        at_str = str(assistive_tech)
        
        # 視覚閲覧環境のキーワード
        visual_keywords = ['視覚閲覧環境', 'なし（視覚']
        if any(kw in at_str for kw in visual_keywords):
            env_types.append('視覚閲覧環境')
        
        # 音声閲覧環境のキーワード
        audio_keywords = [
            'NVDA', 'JAWS', 'VoiceOver', 'TalkBack', 'PC-Talker', 
            'ChromeVox', 'Narrator', '音声'
        ]
        if any(kw in at_str for kw in audio_keywords):
            env_types.append('音声閲覧環境')
    
    # 結果を返す（1つの場合は文字列、2つの場合は配列、0の場合は None）
    if len(env_types) == 0:
        return None
    elif len(env_types) == 1:
        return env_types[0]
    else:
        return env_types


def backfill_environment_type(input_path, output_path=None):
    """
    results.yaml に environment_type をバックフィルする
    """
    if output_path is None:
        output_path = input_path
    
    # ファイルを読み込む
    with open(input_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if not data:
        print("エラー: データが空です")
        return
    
    # environment_type を追加
    updated_count = 0
    visual_count = 0
    audio_count = 0
    already_exists_count = 0
    
    # データを OrderedDict のリストに変換して順序を保持
    new_data = []
    for item in data:
        assistive_tech = item.get('assistive_tech')
        comment = item.get('comment')
        existing_env_type = item.get('environment_type')
        
        # comment から環境タイプを推測
        env_type_from_comment = None
        if comment:
            comment_str = str(comment)
            has_visual = '視覚閲覧環境' in comment_str
            has_audio = '音声閲覧環境' in comment_str
            if has_visual and has_audio:
                env_type_from_comment = ['視覚閲覧環境', '音声閲覧環境']
            elif has_visual:
                env_type_from_comment = '視覚閲覧環境'
            elif has_audio:
                env_type_from_comment = '音声閲覧環境'
        
        # comment から判断できる場合はそれを優先、そうでなければ assistive_tech から判断
        if env_type_from_comment:
            env_type = env_type_from_comment
        else:
            env_type = infer_environment_type(assistive_tech, comment)
        
        # 既に environment_type が存在し、かつ comment から判断できない場合、かつ assistive_tech からも判断できない場合はスキップ
        if existing_env_type is not None and env_type_from_comment is None and env_type is None:
            already_exists_count += 1
            new_data.append(dict(item))  # OrderedDict を dict に変換
            continue
        
        # comment の前に environment_type を挿入
        new_item = {}
        for key, value in item.items():
            if key == 'comment':
                new_item['environment_type'] = env_type
            new_item[key] = value
        
        # comment が存在しない場合は最後に追加
        if 'comment' not in item:
            new_item['environment_type'] = env_type
        
        new_data.append(new_item)
        
        if env_type:
            updated_count += 1
            if isinstance(env_type, list):
                if '視覚閲覧環境' in env_type:
                    visual_count += 1
                if '音声閲覧環境' in env_type:
                    audio_count += 1
            elif env_type == '視覚閲覧環境':
                visual_count += 1
            elif env_type == '音声閲覧環境':
                audio_count += 1
        else:
            updated_count += 1
    
    data = new_data
    
    # ファイルに書き込む（既存の形式を保持）
    # PyYAML を使用して、既存の xlsx_to_yaml.py と同じ形式で出力
    yaml_str = yaml.safe_dump(
        data,
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
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result_lines))
    
    print(f"バックフィル完了: {output_path}")
    print(f"  既に environment_type が存在: {already_exists_count} 件")
    print(f"  新規に追加: {updated_count} 件")
    print(f"    視覚閲覧環境: {visual_count} 件")
    print(f"    音声閲覧環境: {audio_count} 件")
    print(f"    判断できない: {updated_count - visual_count - audio_count} 件")


def main():
    if len(sys.argv) < 2:
        print("使用方法: uv run backfill_environment_type.py <入力ファイル> [出力ファイル]")
        print("例: uv run backfill_environment_type.py ../as_info/src/content/results/results.yaml")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_path):
        print(f"エラー: ファイルが見つかりません: {input_path}")
        sys.exit(1)
    
    backfill_environment_type(input_path, output_path)


if __name__ == '__main__':
    main()
