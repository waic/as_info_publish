import csv
from pathlib import Path
from dataclasses import dataclass
from typing import List
import sys
import yaml
import argparse

def get_value_or_none(value):
    if value:
        return value
    return None

results = []

fieldnames = [s.strip() for s in """
テスト結果 ID,タイムスタンプ,テストケースの番号,テスト実施日,氏名,メールアドレス,OS,ブラウザ,支援技術,支援技術に対する追加の設定,
期待される結果(1),操作内容(1),得られた結果(1),期待される結果(1)を満たしているか?,
期待される結果(2),操作内容(2),得られた結果(2),期待される結果(2)を満たしているか?,
期待される結果(3),操作内容(3),得られた結果(3),期待される結果(3)を満たしているか?,
期待される結果(4),操作内容(4),得られた結果(4),期待される結果(4)を満たしているか?,
期待される結果(5),操作内容(5),得られた結果(5),期待される結果(5)を満たしているか?,
備考,dummy1,レビュアー,レビュー結果,想定されるテストケース番号,dummy2
""".split(',')]
# print(fieldnames)

parser = argparse.ArgumentParser()
parser.add_argument('master_file', type=str, 
                    help='マスターCSVファイル')
args = parser.parse_args()
master_file = args.master_file  # '200213 AS情報作成マスター - シート1.csv'

# AS検証結果一覧の出力?
with open(master_file, encoding='utf-8', newline='') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=fieldnames, dialect='excel')
    for num, row in enumerate(reader):
        if num == 0:
            continue
        # ユーザエージェント 検証結果 操作手順 備考
        # print(row.keys())
        test_id = row['テストケースの番号']
        test_result_id = row['テスト結果 ID']
        contents = []
        for index in range(1, 6):
            expected = row[f'期待される結果({index})']
            procedure = row[f'操作内容({index})']
            actual = row[f'得られた結果({index})']
            judgment = row[f'期待される結果({index})を満たしているか?']
            if any([expected, procedure, actual, judgment]):
                contents.append(
                    dict(
                        expected=expected,
                        procedure=procedure,
                        actual=actual,
                        judgment=judgment
                    )
                )
        results.append(dict(
            id=int(test_result_id),
            test=test_id,
            os=row['OS'].strip().replace(' Mojave', '').replace(' 17134.472', '').replace(', Build 17763.195', '').replace('71.0.3578.94(64bit)Acer C720P', '71').replace('High Sierra ', '').replace('mac OS', 'macOS').replace('、', ' ').replace('エディション：', '').replace(' OSビルド：17134.556', '').replace('windows10', 'Windows 10'),
            user_agent=row['ブラウザ'].strip(),
            assistive_tech=get_value_or_none(row['支援技術']),
            assistive_tech_config=get_value_or_none(row['支援技術に対する追加の設定']),
            contents=contents,
            comment=get_value_or_none(row['備考'])
        ))

with open('results.yaml', 'w') as stream:
    yaml.safe_dump(results, stream=stream, sort_keys=False, default_flow_style=False, allow_unicode=True)
