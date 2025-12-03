# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "PyYAML",
# ]
# ///
import os
import yaml
import re
from collections import OrderedDict
import yaml_dumpers


def extract_info_from_md(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Extracting the required fields using regex
    id_match = re.search(r"# テスト ID\s*\n\s*(.*?)\s*\n", content, re.DOTALL)
    title_match = re.search(r"# テストのタイトル\s*\n\s*(.*?)\s*\n", content, re.DOTALL)
    criteria_match = re.search(
        r"# テストの対象となる達成基準 \(複数\)\s*\n\s*(.*?)\s*\n", content, re.DOTALL
    )
    techs_match = re.search(
        r"# 関連する達成方法 \(複数\)\s*\n\s*(.*?)\s*\n", content, re.DOTALL
    )
    code_link_match = re.search(
        r"# テストコード \(テストファイルへのリンク\)\s*\n\s*\[(.*?)\]\((.*?)\)",
        content,
        re.DOTALL,
    )

    if id_match and title_match and code_link_match:
        test_id = id_match.group(1).strip().replace("WAIC-TEST-", "")
        title = title_match.group(1).strip()
        # Split by newlines first, then by commas, and flatten the list
        criteria = []
        if criteria_match:
            for line in criteria_match.group(1).split("\n"):
                if line.strip():
                    # Split by comma and add each item
                    for item in line.split(","):
                        item = item.strip()
                        if item:
                            criteria.append(item)
        
        techs = []
        if techs_match:
            for line in techs_match.group(1).split("\n"):
                if line.strip():
                    # Split by comma and add each item
                    for item in line.split(","):
                        item = item.strip()
                        if item:
                            techs.append(item)
        code_link = code_link_match.group(2).strip()

        return test_id, OrderedDict(
            {
                "title": title,
                "code": code_link,
                "document": f"https://github.com/waic/as_test/blob/master/WAIC-TEST/HTML/{os.path.basename(file_path)}",
                "criteria": criteria,
                "techs": techs,
            }
        )
    return None, None


def generate_tests_yaml(directory):
    tests = OrderedDict()
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".md"):
            file_path = os.path.join(directory, filename)
            test_id, info = extract_info_from_md(file_path)
            if test_id and info:
                tests[test_id] = info

    yaml.add_representer(OrderedDict, yaml_dumpers.represent_odict)
    yaml.add_representer(str, yaml_dumpers.represent_str)
    yaml.add_representer(type(None), yaml_dumpers.represent_none)
    with open("tests.yaml", "w", encoding="utf-8") as yaml_file:
        yaml.dump(
            tests,
            yaml_file,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
        )


# Directory containing the markdown files
directory = "../as_test/WAIC-TEST/HTML"
generate_tests_yaml(directory)
