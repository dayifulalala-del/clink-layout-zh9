#!/usr/bin/env python3
"""Rebuild Panels/zh9-t9-pinyin.clinkpanel from upstream open data.

Downloads three MIT-licensed datasets, derives a T9 digit-sequence ->
ranked-candidate dictionary, and emits the panel. See THIRD-PARTY-NOTICES.md.

    python3 tools/build-panel.py [--words 14500]

WORD_BUDGET trades file size against coverage. The panel must stay well
under the 256 KB ceiling that Clink applies to sibling asset types.
"""
import argparse, collections, hashlib, json, pathlib, unicodedata, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache"
SOURCES = {
    "char-pinyin.txt": "https://raw.githubusercontent.com/mozillazg/pinyin-data/master/pinyin.txt",
    "phrase-pinyin.txt": "https://raw.githubusercontent.com/mozillazg/phrase-pinyin-data/master/pinyin.txt",
    "jieba.txt": "https://raw.githubusercontent.com/fxsjy/jieba/master/jieba/dict.txt",
}

T9 = {}
for _d, _ls in [("2", "abc"), ("3", "def"), ("4", "ghi"), ("5", "jkl"),
                ("6", "mno"), ("7", "pqrs"), ("8", "tuv"), ("9", "wxyz")]:
    for _c in _ls:
        T9[_c] = _d


def fetch(name, url):
    CACHE.mkdir(exist_ok=True)
    path = CACHE / name
    if not path.exists():
        print(f"  downloading {name} ...")
        with urllib.request.urlopen(url, timeout=120) as r:
            path.write_bytes(r.read())
    return path


def detone(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if not unicodedata.combining(c)).lower()


def to_digits(py):
    out = []
    for ch in py:
        if ch not in T9:
            return None
        out.append(T9[ch])
    return "".join(out)


def is_han(w):
    return all("\u4e00" <= c <= "\u9fff" for c in w)


def build_tables(word_budget):
    char_py = {}
    for line in fetch("char-pinyin.txt", SOURCES["char-pinyin.txt"]).read_text("utf-8").splitlines():
        if line.startswith("#") or ":" not in line:
            continue
        code, rest = line.split(":", 1)
        code = code.strip()
        if not code.startswith("U+"):
            continue
        readings = rest.split("#")[0].strip()
        if readings:
            first = detone(readings.split(",")[0].strip())
            if first:
                char_py[chr(int(code[2:], 16))] = first

    phrase_py = {}
    for line in fetch("phrase-pinyin.txt", SOURCES["phrase-pinyin.txt"]).read_text("utf-8").splitlines():
        if line.startswith("#") or ":" not in line:
            continue
        phrase, rest = line.split(":", 1)
        phrase = phrase.strip()
        sylls = [detone(p) for p in rest.strip().split()]
        if phrase and len(sylls) == len(phrase):
            phrase_py[phrase] = sylls

    freq = {}
    for line in fetch("jieba.txt", SOURCES["jieba.txt"]).read_text("utf-8").splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        w = parts[0]
        if not w.isdigit() and is_han(w) and 1 <= len(w) <= 4:
            try:
                freq[w] = max(freq.get(w, 0), int(parts[1]))
            except ValueError:
                pass

    def syllables_for(w):
        if w in phrase_py:
            return phrase_py[w]
        out = []
        for c in w:
            if c not in char_py:
                return None
            out.append(char_py[c])
        return out

    by_digits = collections.defaultdict(list)
    syllable_set = set()
    for w, n in freq.items():
        sylls = syllables_for(w)
        if not sylls:
            continue
        digits = to_digits("".join(sylls))
        if not digits:
            continue
        syllable_set.update(sylls)
        by_digits[digits].append((n, w))

    ranked = sorted(((n, w) for v in by_digits.values() for n, w in v), reverse=True)
    total = sum(n for n, _ in ranked)
    keep = set(w for _, w in ranked[:word_budget])
    coverage = sum(n for n, w in ranked if w in keep) / total * 100

    DICT = {}
    for k, v in by_digits.items():
        cands = [w for _, w in sorted(v, reverse=True) if w in keep][:8]
        if cands:
            DICT[k] = " ".join(cands)

    SYL = {}
    for s in sorted(syllable_set):
        k = to_digits(s)
        SYL[k] = (SYL[k] + " " + s) if k in SYL else s

    return DICT, SYL, coverage


PANEL_SOURCE = r"""
KEYS = ["'", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"]
DIGIT = {"abc": "2", "def": "3", "ghi": "4", "jkl": "5", "mno": "6", "pqrs": "7", "tuv": "8", "wxyz": "9"}
LETTER = {"a": "2", "b": "2", "c": "2", "d": "3", "e": "3", "f": "3", "g": "4", "h": "4", "i": "4", "j": "5", "k": "5", "l": "5", "m": "6", "n": "6", "o": "6", "p": "7", "q": "7", "r": "7", "s": "7", "t": "8", "u": "8", "v": "8", "w": "9", "x": "9", "y": "9", "z": "9"}
PUNC = ["，", "。", "？", "！", "、", "：", "；", "“", "”", "（", "）", "《", "》", "—", "…", "·"]
NUMS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]


def initial():
    return {"seq": "", "text": "", "mode": "zh", "lock": "", "mt": "", "mti": 0, "page": "main"}


def words_of(v):
    res = []
    cur = ""
    for ch in v:
        if ch == " ":
            if cur != "":
                res.append(cur)
            cur = ""
        else:
            cur = cur + ch
    if cur != "":
        res.append(cur)
    return res


def first_word(v):
    out = ""
    for ch in v:
        if ch == " ":
            return out
        out = out + ch
    return out


def prefixes_desc(seq):
    res = []
    acc = seq
    for ch in seq:
        if acc != "":
            res.append(acc)
            acc = acc[:-1]
    return res


def compose(seq):
    out = ""
    rest = seq
    for step in seq:
        if rest != "":
            best = ""
            bestlen = 0
            acc = ""
            for ch in rest:
                acc = acc + ch
                v = DICT.get(acc, "")
                if v != "":
                    best = first_word(v)
                    bestlen = len(acc)
            if bestlen == 0:
                rest = ""
            else:
                out = out + best
                rest = rest[bestlen:]
    return out


def candidates(state):
    seq = state["seq"]
    lock = state["lock"]
    out = []
    seen = {}
    if seq == "":
        return out
    if lock != "":
        for w in words_of(DICT.get(lock, "")):
            if seen.get(w, 0) == 0:
                seen[w] = 1
                out.append([w, len(lock)])
        return out
    full = compose(seq)
    if len(full) > 1:
        seen[full] = 1
        out.append([full, len(seq)])
    for p in prefixes_desc(seq):
        for w in words_of(DICT.get(p, "")):
            if seen.get(w, 0) == 0:
                seen[w] = 1
                out.append([w, len(p)])
    return out


def syllables(state):
    seq = state["seq"]
    if seq == "":
        return []
    for p in prefixes_desc(seq):
        v = SYL.get(p, "")
        if v != "":
            return words_of(v)
    return []


def pending(state):
    if state["seq"] == "":
        return ""
    return compose(state["seq"])


def view(state):
    rows = []
    page = state["page"]
    buf = state["text"] + pending(state)

    # ---- candidate bar ----
    cands = candidates(state)
    bar = []
    if state["mode"] == "en":
        bar.append(text("英文 · 连按同一键切换字母", size=11, color="gray"))
    elif len(cands) == 0:
        if buf == "":
            bar.append(text("九宫格拼音 · 点击按键开始输入", size=11, color="gray"))
        else:
            bar.append(text(buf, size=14, weight="bold", color="blue"))
    else:
        cbtns = []
        shown = 0
        for c in cands:
            if shown < 7:
                shown = shown + 1
                cbtns.append(button(c[0], set={"text": state["text"] + c[0], "seq": state["seq"][c[1]:], "lock": ""}))
        bar.append(hstack(cbtns, spacing=2))
    rows.append(vstack(bar, spacing=2))

    # ---- current buffer ----
    if buf != "":
        rows.append(text(buf, size=13, color="blue"))
    rows.append(divider())

    if page == "sym":
        prow = []
        for p in PUNC:
            prow.append(button(p, set={"text": state["text"] + p}))
        rows.append(grid(prow, columns=8))
        rows.append(button("返回", set={"page": "main"}, style="primary"))
        return vstack(rows, spacing=4)

    if page == "num":
        nrow = []
        for n in NUMS:
            nrow.append(button(n, set={"text": state["text"] + n}))
        rows.append(grid(nrow, columns=5))
        rows.append(button("返回", set={"page": "main"}, style="primary"))
        return vstack(rows, spacing=4)

    # ---- left syllable column ----
    left = []
    for s in syllables(state):
        if len(left) < 5:
            kd = ""
            for ch in s:
                kd = kd + LETTER.get(ch, "")
            left.append(button(s, set={"lock": kd}))
    if len(left) == 0:
        left.append(text(" ", size=11))

    # ---- 3x3 grid ----
    grid_rows = []
    line = []
    for k in KEYS:
        if k == "'":
            line.append(button("'词", set={"text": state["text"] + pending(state), "seq": "", "lock": ""}))
        elif state["mode"] == "en":
            ni = 0
            drop = 0
            if state["mt"] == k:
                ni = state["mti"] + 1
                if ni >= len(k):
                    ni = 0
                drop = 1
            base = state["text"]
            if drop == 1:
                base = base[:-1]
            line.append(button(k.upper(), set={"text": base + k[ni], "mt": k, "mti": ni}))
        else:
            line.append(button(k.upper(), set={"seq": state["seq"] + DIGIT.get(k, ""), "lock": "", "mt": "", "mti": 0}))
        if len(line) == 3:
            grid_rows.append(hstack(line, spacing=3))
            line = []

    # ---- right function column ----
    if state["seq"] != "":
        back = button("⌫", set={"seq": state["seq"][:-1], "lock": ""})
    else:
        back = button("⌫", set={"text": state["text"][:-1], "mt": "", "mti": 0})
    right = [
        back,
        button("重输", set={"seq": "", "text": "", "lock": "", "mt": "", "mti": 0}),
        button("确定", insert=buf, set={"seq": "", "text": "", "lock": "", "mt": "", "mti": 0}, style="primary"),
    ]

    rows.append(hstack([
        vstack(left, spacing=2),
        vstack(grid_rows, spacing=3),
        vstack(right, spacing=2),
    ], spacing=4))

    # ---- bottom row ----
    if state["mode"] == "zh":
        mode_label = "中 / 英"
        next_mode = "en"
    else:
        mode_label = "英 / 中"
        next_mode = "zh"
    if state["seq"] != "" and len(cands) > 0:
        space = button("空格", set={"text": state["text"] + cands[0][0], "seq": state["seq"][cands[0][1]:], "lock": ""})
    else:
        space = button("空格", set={"text": state["text"] + " "})
    rows.append(hstack([
        button("符号", set={"page": "sym"}),
        button("123", set={"page": "num"}),
        space,
        button(mode_label, set={"mode": next_mode, "seq": "", "lock": "", "mt": "", "mti": 0}),
    ], spacing=3))

    return vstack(rows, spacing=4)
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", type=int, default=14500)
    args = ap.parse_args()

    DICT, SYL, coverage = build_tables(args.words)
    source = ("DICT = " + json.dumps(DICT, ensure_ascii=False, separators=(",", ":")) + "\n"
              + "SYL = " + json.dumps(SYL, ensure_ascii=False, separators=(",", ":")) + "\n"
              + PANEL_SOURCE)
    panel = {
        "id": "zh9-t9-pinyin",
        "name": "\u4e2d\u6587\u4e5d\u952e T9",
        "icon": "keyboard",
        "summary": "\u4f20\u7edf\u4e5d\u5bab\u683c\u62fc\u97f3\u8f93\u5165\uff0c\u5e26\u5019\u9009\u8bcd\u4e0e\u97f3\u8282\u6d88\u6b67",
        "placement": "default",
        "enabled": True,
        "source": source,
    }
    blob = json.dumps(panel, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
    out = ROOT / "Panels" / "zh9-t9-pinyin.clinkpanel"
    out.write_text(blob, encoding="utf-8")
    size = len(blob.encode())
    print(f"  digit keys : {len(DICT)}")
    print(f"  syllables  : {len(SYL)} digit groups")
    print(f"  coverage   : {coverage:.2f}% of word-frequency mass")
    print(f"  written    : {out.relative_to(ROOT)}  {size / 1024:.1f} KB")
    print(f"  sha256     : {hashlib.sha256(blob.encode()).hexdigest()}")
    if size > 256 * 1024:
        raise SystemExit(f"panel is {size / 1024:.1f} KB, over the 256 KB ceiling")


if __name__ == "__main__":
    main()
