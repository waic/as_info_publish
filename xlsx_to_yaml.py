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


def represent_odict(dumper, instance):
    return dumper.represent_mapping("tag:yaml.org,2002:map", instance.items())


def represent_str(dumper, instance):
    if "\n" in instance:
        return dumper.represent_scalar("tag:yaml.org,2002:str", instance, style="|")
    else:
        return dumper.represent_scalar("tag:yaml.org,2002:str", instance)


def represent_none(self, _):
    return self.represent_scalar("tag:yaml.org,2002:null", "")


yaml.add_representer(OrderedDict, represent_odict)
yaml.add_representer(str, represent_str)
yaml.add_representer(type(None), represent_none)

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
    df.columns = FIELDNAMES
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    missing_dates = df["date"].isna()
    if missing_dates.any():
        print("以下の行に欠損日時が存在するため、削除します:")
        print(df[missing_dates])
        df = df.dropna(subset=["date"])
    else:
        print("欠損日時は存在しません。")

    df = df.fillna("")

    results = []
    for _, row in df.iterrows():
        contents = []
        for i in range(1, 11):
            procedure = row[f"procedure{i}"]
            actual = row[f"actual{i}"]
            judgment = row[f"judgment{i}"]
            if any([procedure, actual, judgment]):
                contents.append(
                    dict(procedure=procedure, actual=actual, judgment=judgment)
                )
        results.append(
            dict(
                id=row["id"],
                test=row["test"],
                os=row["os"],
                user_agent=row["user_agent"],
                assistive_tech=row["assistive_tech"],
                assistive_tech_config=row["assistive_tech_config"],
                contents=contents,
                comment=row["tester_comment"],
                tester=row["tester"],
                date=row["date"].strftime("%Y-%m-%d"),
            )
        )

    with open(output_filename, "w") as stream:
        yaml.safe_dump(
            results,
            stream=stream,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )


parser = argparse.ArgumentParser()
parser.add_argument("filename", type=str, help="入力ファイル(XLSX)")
parser.add_argument(
    "--output", type=str, default="results_wip.yaml", help="出力ファイル(YAML)"
)
args = parser.parse_args()

convert_xlsx_to_yaml(args.filename, args.output)
