from collections import OrderedDict
import yaml
import pandas as pd

df = pd.read_csv("/mnt/c/Users/nishimotz/Desktop/results_master_210518.csv", encoding="utf-8-sig")
items = df.reset_index().to_dict(orient="records", into=OrderedDict)

for item in items:
    del item["index"]
    new_item = OrderedDict()
    for key in item.keys():
        if str(item[key]) == "nan":
            item[key] = None
        if key in ("comment", "tester", "date", "reviewer_comment"):
            new_item[key] = item[key]
    contents = []
    for i in range(1, 7):
        data = {}
        for field in ("expected", "procedure", "actual", "judgment"):
            name = f"{field}{i}"
            if item.get(name):
                data[field] = item.get(name)
            if name in item:
                del item[name]
        if data:
            contents.append(data)
    item["contents"] = contents
    for key in ("comment", "reviewer_comment", "tester", "date"):
        del item[key]
        if key in ("tester", "reviewer_comment") and not new_item[key]:
            continue
        item[key] = new_item[key]


def represent_odict(dumper, instance):
    return dumper.represent_mapping("tag:yaml.org,2002:map", instance.items())


yaml.add_representer(OrderedDict, represent_odict)

with open("results_master.yaml", "w") as stream:
    yaml.dump(
        items,
        stream=stream,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
