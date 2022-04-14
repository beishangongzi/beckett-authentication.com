# create by andy at 2022/4/1
# reference:
import json
import os

columns = ["true_number", "query_number", "Item Name", "Signer Name", "Comments"]
fp = open("res.csv", "w")
ls = os.listdir("data")
for l in ls:
    l = "data/" + l
    with open(l, "r", encoding="utf-8") as f:
        res_dict = json.load(f)
        keys = res_dict.keys()
        for k in keys:
            if k not in columns and k != "image":
                columns.append(k)
        res = [res_dict['image']]
        for column in columns:
            try:
                res.append(res_dict[column])
            except KeyError as e:
                res.append("")
        s = ",".join(res)
        fp.write(s)
        fp.write("\n")
fp.close()

if __name__ == '__main__':
    pass
