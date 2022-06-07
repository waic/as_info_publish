from collections import OrderedDict
import yaml
import pandas as pd
import click
import yaml_dumpers


@click.command()
@click.option(
    "--src",
    "-s",
    default="results_master.xlsx",
    help="name of input csv or xlsx file",
    show_default=True,
)
@click.option(
    "--sheet",
    "-t",
    default="results.yaml",
    help="sheet name of input Excel file",
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
def main(src, dest, excel, sheet):
    if excel or src.endswith(".xlsx"):
        df = pd.read_excel(src, sheet_name=sheet, index_col=[0]).dropna(how="all")
    else:
        df = pd.read_csv(src, encoding="utf-8-sig", index_col=[0])
    df.sort_index(inplace=True)
    df.reset_index(inplace=True)
    # df = df[df["id"] != 407]
    items = df.to_dict(orient="records", into=OrderedDict)
    for item in items:
        for key in list(item.keys()):
            if key not in (
                "id",
                "test",
                "date",
                "tester",
                "os",
                "user_agent",
                "assistive_tech",
                "assistive_tech_config",
                "expected1",
                "procedure1",
                "actual1",
                "judgment1",
                "expected2",
                "procedure2",
                "actual2",
                "judgment2",
                "expected3",
                "procedure3",
                "actual3",
                "judgment3",
                "expected4",
                "procedure4",
                "actual4",
                "judgment4",
                "comment",
            ):
                del item[key]
        new_item = OrderedDict()
        for key in item.keys():
            if str(item[key]) == "nan":
                item[key] = None
            if key in ("comment", "tester", "date"):
                new_item[key] = item[key]
        contents = []
        for i in range(1, 7):
            data = {}
            for field in ("expected", "procedure", "actual", "judgment"):
                name = f"{field}{i}"
                if item.get(name):
                    value = item.get(name)
                    if field == "judgment":
                        if value == "○":
                            value = "満たしている"
                        elif value == "×":
                            value = "満たしていない"
                    data[field] = value
                if name in item:
                    del item[name]
            if data:
                contents.append(data)
        item["contents"] = contents
        for key in ("comment", "tester", "date"):
            del item[key]
            if key == "tester" and not new_item[key]:
                continue
            item[key] = new_item[key]
    yaml.add_representer(OrderedDict, yaml_dumpers.represent_odict)
    yaml.add_representer(str, yaml_dumpers.represent_str)
    yaml.add_representer(pd._libs.tslibs.timestamps.Timestamp, yaml_dumpers.represent_timestamp)
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
