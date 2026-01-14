# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "ruamel.yaml",
# ]
# ///
import os
from ruamel.yaml import YAML
import re
from collections import OrderedDict


def extract_info_from_md(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Extracting the required fields using regex
    id_match = re.search(r"# テスト ID\s*\n\s*(.*?)\s*\n", content, re.DOTALL)
    title_match = re.search(r"# テストのタイトル\s*\n\s*(.*?)\s*\n", content, re.DOTALL)
    criteria_match = re.search(
        r"# テストの対象となる達成基準 \(複数\)\s*\n\s*((?:(?!^#).)*?)(?=\n#|\Z)", content, re.DOTALL | re.MULTILINE
    )
    techs_match = re.search(
        r"# 関連する達成方法 \(複数\)\s*\n\s*((?:(?!^#).)*?)(?=\n#|\Z)", content, re.DOTALL | re.MULTILINE
    )
    code_link_match = re.search(
        r"# テストコード \(テストファイルへのリンク\)\s*\n\s*\[(.*?)\]\((.*?)\)",
        content,
        re.DOTALL,
    )

    if id_match and title_match and code_link_match:
        test_id = id_match.group(1).strip().replace("WAIC-TEST-", "")
        title = title_match.group(1).strip()
        # Split by newlines first, then by commas (both half-width and full-width), and flatten the list
        criteria = []
        if criteria_match:
            for line in criteria_match.group(1).split("\n"):
                if line.strip():
                    # Split by comma (both , and 、) and add each item
                    # Replace full-width comma with half-width comma for splitting
                    line_normalized = line.replace("、", ",")
                    for item in line_normalized.split(","):
                        item = item.strip()
                        # Skip empty items and "なし" variants
                        if item and item not in ("なし", "今のところなし", "無し"):
                            criteria.append(item)
        
        techs = []
        if techs_match:
            for line in techs_match.group(1).split("\n"):
                if line.strip():
                    # Split by comma (both , and 、) and add each item
                    # Replace full-width comma with half-width comma for splitting
                    line_normalized = line.replace("、", ",")
                    for item in line_normalized.split(","):
                        item = item.strip()
                        # Skip empty items and "なし" variants
                        if item and item not in ("なし", "今のところなし", "無し"):
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

    # OrderedDict を通常の dict に変換（順序は保持される）
    tests_dict = dict(tests)
    for key in tests_dict:
        tests_dict[key] = dict(tests_dict[key])

    # ruamel.yaml を使用して既存のインデント形式を維持
    yaml_ruamel = YAML()
    yaml_ruamel.preserve_quotes = True
    yaml_ruamel.width = 4096
    yaml_ruamel.indent(mapping=2, sequence=2, offset=0)  # 一貫性のため results.yaml と同じ2スペースに統一
    yaml_ruamel.default_flow_style = False
    yaml_ruamel.allow_unicode = True
    
    with open("tests.yaml", "w", encoding="utf-8") as yaml_file:
        yaml_ruamel.dump(tests_dict, yaml_file)


# Directory containing the markdown files
directory = "../as_test/WAIC-TEST/HTML"
generate_tests_yaml(directory)
