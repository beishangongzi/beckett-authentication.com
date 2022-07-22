import os

import pandas as pd

from bs4 import BeautifulSoup


def parser_file(file):
    number = os.path.basename(file).split(".")[0].split("-")[0]
    res = {"number": [number]}
    if os.path.basename(file).__contains__("image"):
        res.update({'image': 1})
    with open(file, "r") as fp:
        content = fp.read()
        table = BeautifulSoup(content, "html.parser")
        titles = table.find_all("td", {"class": "display_title"})
        for title in titles:
            sibling = title.find_next_sibling("td")
            res.update({title.text.strip(): [sibling.text.strip()]})
    return res


data_dir = "data"
df = pd.DataFrame()
for file in os.listdir(data_dir):
    file_path = os.path.join(data_dir, file)
    res = parser_file(file_path)
    res = pd.DataFrame(res, )
    df = pd.concat([df, res])
print(df)

df.to_excel("res.xlsx")
