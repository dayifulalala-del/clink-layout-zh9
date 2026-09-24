#!/usr/bin/env python3
"""Execute the panel source with mock UI helpers and simulate real typing."""
import json, sys

import pathlib
panel = json.load(open(pathlib.Path(__file__).resolve().parents[1] / "Panels" / "zh9-t9-pinyin.clinkpanel"))

# --- mock the constrained UI helpers, recording the widget tree ---
class W:
    def __init__(self, kind, **kw):
        self.kind = kind; self.kw = kw
    def __repr__(self):
        return f"{self.kind}({self.kw})"

def button(label, insert=None, set=None, style=None):
    return W("button", label=label, insert=insert, set=set, style=style)
def text(s, size=None, color=None, weight=None):  return W("text", s=s)
def vstack(items, spacing=None):  return W("vstack", items=items)
def hstack(items, spacing=None):  return W("hstack", items=items)
def grid(items, columns=None):    return W("grid", items=items)
def divider():                    return W("divider")

ns = {"button": button, "text": text, "vstack": vstack,
      "hstack": hstack, "grid": grid, "divider": divider}
exec(panel["source"], ns)

initial, view = ns["initial"], ns["view"]

def buttons(node, acc):
    if isinstance(node, W):
        if node.kind == "button": acc.append(node)
        for v in node.kw.values():
            buttons(v, acc)
    elif isinstance(node, list):
        for v in node: buttons(v, acc)
    return acc

def press(state, label):
    """Find a button by label in the rendered tree and apply its `set`."""
    for b in buttons(view(state), []):
        if b.kw["label"] == label:
            new = dict(state)
            if b.kw["set"]: new.update(b.kw["set"])
            return new, b.kw["insert"]
    raise AssertionError(f"no button {label!r}; have {[x.kw['label'] for x in buttons(view(state), [])][:24]}")

def cand_labels(state):
    node = view(state)
    bar = node.kw["items"][0]
    return [b.kw["label"] for b in buttons(bar, [])]

fails = []
def check(name, got, want):
    ok = want in got if isinstance(got, list) else got == want
    print(("  PASS  " if ok else "  FAIL  ") + name + f"   got={got!r}")
    if not ok: fails.append(name)

print("=== 1. render empty state ===")
s = initial(); view(s); print("  PASS   initial render ok")

print("\n=== 2. type ni hao -> 你好 ===")
s = initial()
for k in ["MNO", "GHI"]:          # n=6, i=4  -> "64"
    s, _ = press(s, k)
check("seq after MNO,GHI", s["seq"], "64")
check("candidates contain 你", cand_labels(s), "你")

print("\n=== 3. full phrase: ni hao (64 426) ===")
s = initial()
for k in ["MNO","GHI","GHI","ABC","MNO"]:   # n i h a o -> 6 4 4 2 6
    s, _ = press(s, k)
check("seq", s["seq"], "64426")
check("composed candidate 你好", cand_labels(s), "你好")

print("\n=== 4. screenshot case: pu tong (78 8664) ===")
s = initial()
for k in ["PQRS","TUV","TUV","MNO","MNO","GHI"]:   # p u t o n g
    s, _ = press(s, k)
check("seq", s["seq"], "788664")
check("candidate 普通", cand_labels(s), "普通")
check("candidate 如同", cand_labels(s), "如同")

print("\n=== 5. syllable column shows pu/qu/ru/su ===")
s = initial()
for k in ["PQRS","TUV"]:
    s, _ = press(s, k)
labels = [b.kw["label"] for b in buttons(view(s), [])]
for want in ["pu","qu","ru","su"]:
    check(f"syllable {want}", labels, want)

print("\n=== 6. select a candidate consumes the right digits ===")
s = initial()
for k in ["PQRS","TUV","TUV","MNO","MNO","GHI"]:
    s, _ = press(s, k)
s2, _ = press(s, "普通")
check("text after picking 普通", s2["text"], "普通")
check("seq fully consumed", s2["seq"], "")

print("\n=== 7. backspace removes one digit ===")
s = initial()
for k in ["MNO","GHI"]:
    s, _ = press(s, k)
s, _ = press(s, "⌫")
check("seq after backspace", s["seq"], "6")

print("\n=== 8. 确定 inserts the composed text ===")
s = initial()
for k in ["MNO","GHI","GHI","ABC","MNO"]:
    s, _ = press(s, k)
s2, ins = press(s, "确定")
check("确定 inserts 你好", ins, "你好")
check("state cleared", s2["seq"] + s2["text"], "")

print("\n=== 9. 重输 clears everything ===")
s = initial()
for k in ["MNO","GHI"]:
    s, _ = press(s, k)
s, _ = press(s, "重输")
check("cleared", s["seq"] + s["text"], "")

print("\n=== 10. English multi-tap: same key cycles ===")
s = initial()
s, _ = press(s, "中 / 英")
check("mode", s["mode"], "en")
s, _ = press(s, "ABC"); check("first tap -> a", s["text"], "a")
s, _ = press(s, "ABC"); check("second tap -> b", s["text"], "b")
s, _ = press(s, "ABC"); check("third tap -> c", s["text"], "c")
s, _ = press(s, "ABC"); check("wraps back to a", s["text"], "a")
s, _ = press(s, "DEF"); check("different key commits", s["text"], "ad")

print("\n=== 11. symbol and number pages ===")
s = initial()
s, _ = press(s, "符号"); check("sym page", s["page"], "sym")
s, _ = press(s, "，");  check("punct inserted", s["text"], "，")
s, _ = press(s, "返回"); check("back to main", s["page"], "main")
s, _ = press(s, "123"); check("num page", s["page"], "num")
s, _ = press(s, "7");   check("digit inserted", s["text"], "，7")

print("\n=== 12. 空格 picks the first candidate ===")
s = initial()
for k in ["MNO","GHI"]:
    s, _ = press(s, k)
top = cand_labels(s)[0]
s2, _ = press(s, "空格")
check("空格 commits top candidate", s2["text"], top)

print("\n=== 13. syllable lock filters candidates ===")
s = initial()
for k in ["PQRS","TUV"]:
    s, _ = press(s, k)
s2, _ = press(s, "su")
check("lock set", s2["lock"], "78")
print("   locked candidates:", cand_labels(s2)[:6])

print("\n=== 14. long input does not crash ===")
s = initial()
for k in ["PQRS","TUV","TUV","MNO","MNO","GHI","DEF","DEF","PQRS","GHI","TUV","PQRS","TUV","DEF","ABC"]:
    s, _ = press(s, k)
view(s)
print(f"  PASS   composed: {ns['compose'](s['seq'])!r}")

print("\n" + ("ALL PASSED" if not fails else f"FAILED: {fails}"))
sys.exit(1 if fails else 0)
