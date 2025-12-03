# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "PyYAML",
#     "pandas",
#     "openpyxl",
# ]
# ///
import pandas as pd
import yaml
from collections import OrderedDict
import argparse
import re


def represent_odict(dumper, instance):
    return dumper.represent_mapping("tag:yaml.org,2002:map", instance.items())


def represent_str(dumper, instance):
    if "\n" in instance:
        return dumper.represent_scalar("tag:yaml.org,2002:str", instance, style="|")
    else:
        return dumper.represent_scalar("tag:yaml.org,2002:str", instance)


def represent_none(self, _):
    # 既存データの形式（key:）に合わせるため、None を null として出力
    # 後で文字列置換で : null を : に変換する
    return self.represent_scalar("tag:yaml.org,2002:null", "")


yaml.add_representer(OrderedDict, represent_odict)
yaml.add_representer(str, represent_str)
yaml.add_representer(type(None), represent_none)


def dump_yaml_with_empty_keys(data, stream):
    """
    既存データの形式（key:）に合わせて YAML を出力する
    None 値を key: という形式（値なし）で出力する
    """
    # まず通常の YAML を生成
    yaml_str = yaml.safe_dump(
        data,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
    
    # : null を : に変換（既存データの形式に合わせる）
    # ただし、値として "null" という文字列が含まれている場合は置換しない
    # パターン: 行末の : null を : に変換
    # インデントされた行で : null の後に改行または終端が来る場合のみ
    lines = yaml_str.split('\n')
    result_lines = []
    
    for line in lines:
        # 行末の : null を : に変換
        # ただし、文字列値として "null" が含まれている場合は除外
        if re.match(r'^(\s+)([^:]+):\s+null\s*$', line):
            # インデント + キー名 + : null の形式を : に変換
            result_lines.append(re.sub(r':\s+null\s*$', ':', line))
        else:
            result_lines.append(line)
    
    stream.write('\n'.join(result_lines))

# input_fieldnames = [
#     "結果ID(仮)",
#     "テスト実施日",
#     "氏名\n（テスト結果ページへの表示名）",
#     "メールアドレス",
#     "OS\nバージョンは（警告を気にせず）手入力ください",
#     "ブラウザ\nバージョンは（警告を気にせず）手入力ください",
#     "支援技術\nバージョンは（警告を気にせず）手入力ください",
#     "支援技術に対する\n追加の設定",
#     "テストケース番号",
#     "期待される結果 1. に対する操作内容",
#     "得られた結果 1.",
#     "期待される結果 1. を\n満たしているか ?",
#     "期待される結果 2. に対する操作内容",
#     "得られた結果 2. ",
#     "期待される結果 2. を\n満たしているか ?",
#     "期待される結果 3. に対する操作内容",
#     "得られた結果 3. ",
#     "期待される結果 3. を\n満たしているか ?",
#     "期待される結果 4. に対する操作内容",
#     "得られた結果 4. ",
#     "期待される結果 4. を\n満たしているか ?",
#     "期待される結果 5. に対する操作内容",
#     "得られた結果 5.",
#     "期待される結果 5. を\n満たしているか ?",
#     "期待される結果 6. に対する操作内容",
#     "得られた結果 6.",
#     "期待される結果 6. を\n満たしているか ?",
#     "期待される結果 7. に対する操作内容",
#     "得られた結果 7.",
#     "期待される結果 7. を\n満たしているか ?",
#     "期待される結果 8. に対する操作内容",
#     "得られた結果 8.",
#     "期待される結果 8. を\n満たしているか ?",
#     "期待される結果 9. に対する操作内容",
#     "得られた結果 9.",
#     "期待される結果 9. を\n満たしているか ?",
#     "期待される結果 10. に対する操作内容",
#     "得られた結果 10.",
#     "期待される結果 10. を\n満たしているか ?",
#     "備考",
#     "WAIC備考",
# ]

FIELDNAMES = [
    "id",
    "date",
    "tester",
    "email",
    "os",
    "user_agent",
    "assistive_tech",
    "assistive_tech_config",
    "test",
    "procedure1",
    "actual1",
    "judgment1",
    "procedure2",
    "actual2",
    "judgment2",
    "procedure3",
    "actual3",
    "judgment3",
    "procedure4",
    "actual4",
    "judgment4",
    "procedure5",
    "actual5",
    "judgment5",
    "procedure6",
    "actual6",
    "judgment6",
    "procedure7",
    "actual7",
    "judgment7",
    "procedure8",
    "actual8",
    "judgment8",
    "procedure9",
    "actual9",
    "judgment9",
    "procedure10",
    "actual10",
    "judgment10",
    "tester_comment",
    "waic_comment",
    "reviewer1_comment",
    "reviewer2_comment",
]


def convert_xlsx_to_yaml(filename, output_filename):
    df = pd.read_excel(filename, dtype={"テストケース番号": str})
    
    # 列数に応じて FIELDNAMES を調整
    # results_20250205.xlsx には「視覚閲覧環境、音声閲覧環境の種別」列が追加されている
    actual_columns = len(df.columns)
    expected_columns = len(FIELDNAMES)
    
    if actual_columns == expected_columns:
        # 既存の構造（43列）
        df.columns = FIELDNAMES
    elif actual_columns == expected_columns + 1:
        # 新しい構造（44列）: 「視覚閲覧環境、音声閲覧環境の種別」が追加
        # この列は無視して、残りの列を FIELDNAMES にマッピング
        # 列の位置: 0-8 はそのまま、9番目が新規列、10-42 を 9-41 にマッピング
        new_columns = FIELDNAMES[:9] + [None] + FIELDNAMES[9:]
        df.columns = new_columns
        # 新規列を削除（使用しない）
        df = df.drop(columns=[None], errors='ignore')
    else:
        print(f"警告: 予期しない列数です。期待: {expected_columns}, 実際: {actual_columns}")
        print(f"実際の列名: {list(df.columns)}")
        # 可能な限りマッピングを試みる
        min_cols = min(actual_columns, expected_columns)
        df.columns = list(df.columns[:min_cols]) + FIELDNAMES[min_cols:]
        df = df.iloc[:, :min_cols]
    
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    missing_dates = df["date"].isna()
    if missing_dates.any():
        print("以下の行に欠損日時が存在するため、削除します:")
        print(df[missing_dates])
        df = df.dropna(subset=["date"])
    else:
        print("欠損日時は存在しません。")

    df = df.fillna("")

    # None や NaN を None のまま保持するヘルパー関数
    # 既存データの形式（key:）に合わせるため、空文字列ではなく None を保持
    def to_none_if_empty(value):
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        if value == "":
            return None
        return value

    results = []
    for _, row in df.iterrows():
        contents = []
        for i in range(1, 11):
            procedure = to_none_if_empty(row[f"procedure{i}"])
            actual = to_none_if_empty(row[f"actual{i}"])
            judgment = to_none_if_empty(row[f"judgment{i}"])
            if any([procedure, actual, judgment]):
                contents.append(
                    dict(procedure=procedure, actual=actual, judgment=judgment)
                )
        results.append(
            dict(
                id=row["id"],
                test=row["test"],
                os=to_none_if_empty(row["os"]),
                user_agent=to_none_if_empty(row["user_agent"]),
                assistive_tech=to_none_if_empty(row["assistive_tech"]),
                assistive_tech_config=to_none_if_empty(row["assistive_tech_config"]),
                contents=contents,
                comment=to_none_if_empty(row["tester_comment"]),
                tester=to_none_if_empty(row["tester"]),
                date=row["date"].strftime("%Y-%m-%d"),
            )
        )

    with open(output_filename, "w") as stream:
        dump_yaml_with_empty_keys(results, stream)


parser = argparse.ArgumentParser()
parser.add_argument("filename", type=str, help="入力ファイル(XLSX)")
parser.add_argument(
    "--output", type=str, default="results_wip.yaml", help="出力ファイル(YAML)"
)
args = parser.parse_args()

convert_xlsx_to_yaml(args.filename, args.output)
