#!/usr/bin/env python3
"""Run the plugin against a simulated Clink keyboard: real field, real key taps."""
import sys, pathlib

path = sys.argv[1] if len(sys.argv) > 1 else "zh9-t9.py"
raw = pathlib.Path(path).read_text(encoding="utf-8")
if path.endswith(".clinkplugin"):
    # the packed artifact: run exactly the source Clink would import
    import json as _json
    src = _json.loads(raw)["source"]
else:
    lines = raw.split("\n")
    if lines[0].strip() == "# ---":
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "# ---")
        src = "\n".join(lines[end + 1:])
    else:
        src = raw

FIELD = {"text": ""}
LAYOUTS = []

def layout(id, name, icon=None, rows=None, left=None, right=None):
    return {"id": id, "name": name, "rows": rows or []}
def layout_key(glyph, action=None, width=None):
    return {"glyph": glyph, "action": action}
def replace(n, s):
    FIELD["text"] = FIELD["text"][:-n] + s if n else FIELD["text"] + s
def insert(s): FIELD["text"] += s
def vstack(items, spacing=None): return items
def hstack(items, spacing=None): return items
def text(s, size=None, color=None, weight=None): return ("text", s)
def toggle(label, value, action=None): return ("toggle", label, value)
def section(anchor, items, title=None): return items
def context(): return FIELD["text"]

ns = {"layout": layout, "layout_key": layout_key, "replace": replace, "insert": insert,
      "vstack": vstack, "hstack": hstack, "text": text, "toggle": toggle,
      "section": section, "context": context}
exec(src, ns)

initial, layouts, on_key = ns["initial"], ns["layouts"], ns["on_key"]
suggestions = ns["suggestions"]

GLYPH2GROUP = {"ABC": "abc", "DEF": "def", "GHI": "ghi", "JKL": "jkl",
               "MNO": "mno", "PQRS": "pqrs", "TUV": "tuv", "WXYZ": "wxyz"}

def tap(state, glyph):
    """Simulate the keyboard: the key inserts its glyph's letters, then on_key runs."""
    grp = GLYPH2GROUP[glyph]
    FIELD["text"] += grp          # the key's own insert
    return on_key(grp, state)     # plugin collapses it

def word():
    return FIELD["text"]

fails = []
def check(name, got, want):
    if isinstance(want, list):
        ok = got == want
    elif isinstance(got, list):
        ok = want in got
    else:
        ok = got == want
    print(("  PASS  " if ok else "  FAIL  ") + name + f"   got={got!r}")
    if not ok: fails.append(name)

print("=== 1. layouts() 结构 ===")
ls = layouts(initial())
rows = ls[0]["rows"]
print(f"  布局 id={ls[0]['id']} name={ls[0]['name']}")
print(f"  {len(rows)} 行 x {[len(r) for r in rows]}")
for r in rows:
    print("    " + "  ".join(f"{k['glyph']:^6}" for k in r))
check("3 行", len(rows), 3)
check("每行 3 键", [len(r) for r in rows], [3, 3, 3])

print("\n=== 2. 一个键只留一个字母（你要求的）===")
FIELD["text"] = ""; s = initial()
s = tap(s, "ABC")
check("点 ABC 后字段内容", word(), "a")
s = tap(s, "DEF")
check("再点 DEF", word(), "ad")

print("\n=== 3. 普通 (PQRS TUV TUV MNO MNO GHI) ===")
FIELD["text"] = ""; s = initial()
for g in ["PQRS","TUV","TUV","MNO","MNO","GHI"]:
    s = tap(s, g)
check("字段只有 6 个字母", len(word()), 6)
c = suggestions(word(), s)
check("候选含 普通", c, "普通")
check("候选含 如同", c, "如同")
print(f"   完整候选: {c}")

print("\n=== 4. 你好 ===")
FIELD["text"] = ""; s = initial()
for g in ["MNO","GHI","GHI","ABC","MNO"]:
    s = tap(s, g)
c = suggestions(word(), s)
check("候选含 你好", c, "你好")
print(f"   完整候选: {c}")

print("\n=== 5. 中国 / 什么 / 我们 ===")
for name, seq in [("中国", ["WXYZ","GHI","MNO","MNO","GHI","GHI","TUV","MNO"]),
                  ("什么", ["PQRS","GHI","DEF","MNO","MNO","DEF"]),
                  ("我们", ["WXYZ","MNO","MNO","DEF","MNO"])]:
    FIELD["text"] = ""; s = initial()
    for g in seq: s = tap(s, g)
    c = suggestions(word(), s)
    check(f"候选含 {name}", c, name)

print("\n=== 6. 非九宫格输入不返回候选 ===")
FIELD["text"] = "hello"; s = initial()
check("普通英文词无候选", suggestions("hello", s), [])
check("空词无候选", suggestions("", s), [])

print("\n=== 7. 关闭开关后不干预 ===")
FIELD["text"] = ""; s = initial(); s["on"] = False
for g in ["MNO","GHI"]: s = tap(s, g)
check("关闭后无候选", suggestions(word(), s), [])

print("\n=== 8. 长句不崩 ===")
FIELD["text"] = ""; s = initial()
for g in ["PQRS","TUV","TUV","MNO","MNO","GHI","DEF","DEF","PQRS","GHI","TUV","PQRS","TUV","DEF","ABC"]:
    s = tap(s, g)
c = suggestions(word(), s)
print(f"  PASS   {len(word())} 个字母 -> 首候选 {c[0] if c else '(无)'}")

print("\n" + ("ALL PASSED" if not fails else f"FAILED: {fails}"))
sys.exit(1 if fails else 0)
