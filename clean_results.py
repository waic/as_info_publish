#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "ruamel.yaml",
# ]
# ///
"""
as_info の results 分割ファイルをクレンジングするスクリプト

過去に取り込んだデータに残っている表記の揺れを、機械的に統一します。
新規データの取り込み（xlsx_to_yaml.py / append_results.py）とは別に、
既存ファイルをまとめて直したいときに使います。

処理内容:
  1. テストケース番号の正規化
     WAIC-TEST-0001-01 / WAIC-CODE-0002-01 → 0001-01 / 0002-01
     tests.yaml に存在しない値は変更せず、警告として報告する
  2. 不可視文字（U+200E など）の除去
  3. 空文字列 → 空値（key: 形式）
  4. 単一行の値の末尾空白の除去（複数行のリテラルブロックは変更しない）

使用方法:
  uv run clean_results.py                     # 対象を表示するだけ（書き込まない）
  uv run clean_results.py --write             # 実際に書き換える
  uv run clean_results.py --write --dry-run   # 変更内容を diff 風に表示

例:
  uv run clean_results.py --write
  uv run clean_results.py --results ../as_info/src/content/results --write
"""
import argparse
import glob
import io
import os
import sys

from ruamel.yaml import YAML

from yaml_dumpers import remove_invisible

TEST_ID_PREFIXES = ("WAIC-TEST-", "WAIC-CODE-")


def make_yaml():
    """既存ファイルの書式を保ったまま読み書きする YAML インスタンスを作る。"""
    y = YAML()
    y.preserve_quotes = True
    y.width = 4096
    # 既存ファイルは mapping=2 / sequence=4 / offset=2（`  - key:`）で書かれている
    y.indent(mapping=2, sequence=4, offset=2)
    return y


def yaml_text_keys(stream):
    """tests.yaml のトップレベルキーを返す。"""
    return YAML(typ="safe").load(stream).keys()


def normalize_test_id(value):
    """テストケース番号を tests.yaml のキー形式（例: 0001-01）に揃える。"""
    text = "" if value is None else str(value)
    text = remove_invisible(text).strip()
    for prefix in TEST_ID_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    return text.strip()


def clean_value(value, path, report):
    """1つの値をクレンジングする。複数行の値は末尾空白を触らない。"""
    if isinstance(value, str):
        cleaned = remove_invisible(value)
        if cleaned != value:
            report["invisible"].append(path)
        if cleaned == "":
            report["empty"].append(path)
            return None
        if "\n" not in cleaned and cleaned != cleaned.rstrip():
            report["trailing"].append(path)
            cleaned = cleaned.rstrip()
        return cleaned
    return value


def clean_entry(entry, test_ids, report):
    """エントリをその場で書き換える（ruamel のコメント・書式を保つため）。"""
    if "test" in entry:
        before = entry["test"]
        normalized = normalize_test_id(before)
        if normalized != before:
            report["test_id"].append((entry.get("id"), before, normalized))
            entry["test"] = normalized
        if normalized not in test_ids:
            report["unknown_test"].append((entry.get("id"), normalized))
    for key in entry:
        if key == "test":
            continue
        if key == "contents" and isinstance(entry[key], list):
            for index, item in enumerate(entry[key]):
                for item_key in item:
                    item[item_key] = clean_value(
                        item[item_key], f"contents[{index}].{item_key}", report
                    )
        else:
            entry[key] = clean_value(entry[key], key, report)
    return entry


def dump_entry(yaml_io, entry):
    buffer = io.StringIO()
    yaml_io.dump(entry, buffer)
    return buffer.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description="results の分割ファイルをクレンジングする")
    parser.add_argument("--results", default="../as_info/src/content/results",
                        help="as_info の results ディレクトリ")
    parser.add_argument("--tests", default="../as_info/src/content/tests/tests.yaml",
                        help="tests.yaml のパス（テストケース番号の検証に使う）")
    parser.add_argument("--write", action="store_true", help="実際にファイルを書き換える")
    parser.add_argument("--dry-run", action="store_true", help="変更前後を表示する")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.results):
        print(f"エラー: ディレクトリが見つかりません: {args.results}")
        return 1
    if not os.path.exists(args.tests):
        print(f"エラー: tests.yaml が見つかりません: {args.tests}")
        return 1

    with open(args.tests, encoding="utf-8") as f:
        test_ids = set(yaml_text_keys(f))

    files = sorted(glob.glob(os.path.join(args.results, "*", "*.yaml")))
    report = {k: [] for k in ("test_id", "unknown_test", "invisible", "empty", "trailing")}
    changed = []
    yaml_io = make_yaml()

    for path in files:
        with open(path, encoding="utf-8", newline="") as f:
            old_text = f.read()
        entry = yaml_io.load(io.StringIO(old_text))
        if not isinstance(entry, dict) or "id" not in entry:
            print(f"警告: 結果エントリではないためスキップします: {path}")
            continue
        cleaned = clean_entry(entry, test_ids, report)
        new_text = dump_entry(yaml_io, cleaned)
        if new_text != old_text:
            changed.append(path)
            if args.dry_run:
                print(f"--- {path}")
                for line in new_text.split("\n"):
                    print(f"+ {line}")
            if args.write:
                # 既存ファイルの改行コードを保つ（Windows のテキストモードで CRLF にしない）
                newline = "\r\n" if "\r\n" in old_text else "\n"
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(new_text.replace("\n", newline))

    print(f"対象ファイル: {len(files)} 件")
    print(f"テストケース番号を正規化: {len(report['test_id'])} 件")
    for entry_id, before, after in report["test_id"]:
        print(f"  id {entry_id}: {before!r} -> {after!r}")
    if report["unknown_test"]:
        print(f"警告: tests.yaml に存在しないテストケース番号: {len(report['unknown_test'])} 件")
        for entry_id, test_id in report["unknown_test"]:
            print(f"  id {entry_id}: {test_id!r}")
    print(f"不可視文字を除去した値: {len(report['invisible'])} 件")
    print(f"空文字列を空値にした値: {len(report['empty'])} 件")
    print(f"末尾空白を除去した値: {len(report['trailing'])} 件")
    print(f"変更が必要なファイル: {len(changed)} 件")
    if changed and not args.write:
        print("（--write を付けると実際に書き換えます）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
