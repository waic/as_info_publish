import yaml
import pandas as pd
import click


@click.command()
@click.option(
    "--src", "-s", default="../as_info/src/content/results/results.yaml", 
    help="name of input yaml file", show_default=True
)
@click.option(
    "--dest",
    "-d",
    default="results_new.csv",
    help="name of output csv (or xlsx) file",
    show_default=True
)
@click.option(
    "--excel",
    "-e",
    is_flag=True,
    help="use to_excel rather than to_csv",
)
@click.option("--sheet", "-s", default="results", help="output sheet name of xlsx file", show_default=True)
def main(src, dest, excel, sheet):
    with open(src, "r") as y:
        results = yaml.safe_load(y)
    for result in results:
        contents = result.get("contents")
        if contents:
            for index, item in enumerate(contents):
                for name in ("expected", "procedure", "actual", "judgment"):
                    result[f"{name}{index+1}"] = item.get(name)
            del result["contents"]
    df = pd.json_normalize(results)
    columns = "id,test,date,tester,os,user_agent,assistive_tech,assistive_tech_config,expected1,procedure1,actual1,judgment1,expected2,procedure2,actual2,judgment2,expected3,procedure3,actual3,judgment3,expected4,procedure4,actual4,judgment4,comment,reviewer_comment".split(
        ","
    )
    if excel:
        df.to_excel(
            dest,
            sheet,
            index=False,
            columns=columns,
            engine="openpyxl",
        )
    else:
        df.to_csv(dest, encoding="utf-8-sig", index=False, columns=columns, quoting=2)


if __name__ == "__main__":
    main()
