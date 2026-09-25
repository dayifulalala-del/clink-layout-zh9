#!/usr/bin/env python3
import json, os, pathlib

T9 = {}
for dg, ls in [("2","abc"),("3","def"),("4","ghi"),("5","jkl"),("6","mno"),("7","pqrs"),("8","tuv"),("9","wxyz")]:
    for c in ls:
        T9[c] = dg

BUDGET = int(os.environ.get("WORD_BUDGET", "4000"))
d = json.load(open("by_digits.json"))
allw = sorted(((n, w) for v in d.values() for n, w in v), reverse=True)
total = sum(n for n, _ in allw)
keep = set(w for _, w in allw[:BUDGET])
DICT = {}
for k, v in d.items():
    c = [w for _, w in v if w in keep][:6]
    if c:
        DICT[k] = " ".join(c)

header = """# ---
# name: 中文九键
# icon: keyboard
# summary: 九宫格拼音：ABC 分组键配中文候选词，装进「布局 > 排列」
# version: 1.0
# author: dayifulalala-del
# ---

"""
src = pathlib.Path("plugin_source.py").read_text(encoding="utf-8")
dict_lit = "DICT = " + json.dumps(DICT, ensure_ascii=False, separators=(",", ":")) + "\n\n"
# dictionary goes after the explanatory comment block, before the tables
marker = "GROUPS = "
i = src.index(marker)
body = src[:i] + dict_lit + src[i:]
out = pathlib.Path(os.environ.get("OUT", "zh9-t9.py"))
out.write_text(header + body, encoding="utf-8")
cov = sum(n for n, w in allw if w in keep) / total * 100
print(f"  词数 {BUDGET} -> {len(DICT)} 个按键序列, 覆盖 {cov:.2f}%, {len(out.read_bytes())/1024:.1f} KB -> {out}")
