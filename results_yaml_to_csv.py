import yaml
import pandas as pd

with open("../as_info/data/results.yaml", "r") as y:
    results = yaml.safe_load(y)
for result in results:
    contents = result.get("contents")
    if contents:
        for index, item in enumerate(contents):
            for name in ("expected", "procedure", "actual", "judgment"):
                result[f"{name}{index+1}"] = item.get(name)
        del result["contents"]
df = pd.json_normalize(results)
# print(df.head())
columns = "id,test,date,tester,os,user_agent,assistive_tech,assistive_tech_config,expected1,procedure1,actual1,judgment1,expected2,procedure2,actual2,judgment2,expected3,procedure3,actual3,judgment3,expected4,procedure4,actual4,judgment4,comment,reviewer_comment".split(
    ","
)
df.to_csv("/mnt/c/Users/nishimotz/Desktop/results_master.csv", encoding="utf-8-sig", index=False, columns=columns)
