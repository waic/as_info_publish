import csv
from pathlib import Path
from dataclasses import dataclass
from typing import List
import sys
import yaml

testcases = {}
for test_doc in Path('../../as_test/WAIC-TEST/HTML').glob('*.md'):
    with open(test_doc, encoding='utf-8') as mdfile:
        data = {}
        test_id_pos = None
        title_pos = None
        code_pos = None
        criteria_pos = None
        technique_pos = None
        for num, text in enumerate(mdfile):
            text = text.strip()
            # print(text)
            data[num] = text
            if text == '# テスト ID':
                test_id_pos = num + 1
            elif text == '# テストのタイトル':
                title_pos = num + 1
            elif text == '# テストコード (テストファイルへのリンク)':
                code_pos = num + 1
            elif text == '# テストの対象となる達成基準 (複数)':
                criteria_pos = num + 1
            elif text == '# 関連する達成方法 (複数)':
                technique_pos = num + 1
    test_name = data[test_id_pos]
    test_id = test_name.replace('WAIC-TEST-', '')
    title = data[title_pos]
    code = data[code_pos].split('](')[1][:-1]
    document = f'https://github.com/waic/as_test/blob/master/WAIC-TEST/HTML/{test_name}.md'
    criteria = [s.strip() for s in data[criteria_pos].split(',')]
    techs = [s.strip() for s in data[technique_pos].split(',') if s not in ('なし', '今のところなし')]
    # print(test_id, repr(criteria), repr(technique))
    testcases[test_id] = dict(
        title=title,
        code=code,
        document=document,
        criteria=criteria,
        techs=techs
    )

print(repr(testcases))
with open('tests.yaml', 'w') as stream:
    yaml.dump(testcases, stream=stream, sort_keys=False, default_flow_style=False, allow_unicode=True)
