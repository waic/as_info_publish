from collections import OrderedDict
import yaml
import pandas as pd
import click
import yaml_dumpers

@click.command()
@click.option(
    "--src",
    "-s",
    default="results_new.csv",
    help="name of input csv (or xlsx) file",
    show_default=True,
)
@click.option(
    "--dest",
    "-d",
    default="results_new.yaml",
    help="name of output yaml file",
    show_default=True,
)
@click.option(
    "--excel",
    "-e",
    is_flag=True,
    help="use read_excel rather than read_csv",
)
def main(src, dest, excel):
    if excel:
        df = pd.read_excel(src)
    else:
        df = pd.read_csv(src, encoding="utf-8-sig")
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
    yaml.add_representer(OrderedDict, yaml_dumpers.represent_odict)
    yaml.add_representer(str, yaml_dumpers.represent_str)
    yaml.add_representer(type(None), yaml_dumpers.represent_none)
    with open(dest, "w") as stream:
        yaml.dump(
            items,
            stream=stream,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )


if __name__ == "__main__":
    main()
