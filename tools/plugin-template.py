# Nine-key Chinese pinyin, as a layout plus its candidates.
#
# The layout goes into Layout > Arrangement like any other. Each grouped key
# inserts its own letters, and on_key immediately collapses them to a single
# marker letter, so one tap leaves one character in the field rather than
# three. suggestions() decodes those markers back into the key sequence and
# answers with Chinese words from the table below; tapping one replaces the
# markers, which is ordinary suggestion-bar behaviour.

GROUPS = ["abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"]
DIGIT = {"abc": "2", "def": "3", "ghi": "4", "jkl": "5",
         "mno": "6", "pqrs": "7", "tuv": "8", "wxyz": "9"}
MARK = {"a": "2", "d": "3", "g": "4", "j": "5",
        "m": "6", "p": "7", "t": "8", "w": "9"}
FIRST = {"2": "a", "3": "d", "4": "g", "5": "j",
         "6": "m", "7": "p", "8": "t", "9": "w"}
MAX_CANDIDATES = 8


def initial():
    return {"on": True}


def settings(state):
    return vstack([
        toggle("九宫格候选词", state["on"], action="on"),
        text("在 布局 > 排列 里选择「中文九键」。点 ABC 这类分组键只留一个字母，"
             "候选栏会给出中文词，点候选即可上屏。", size=12, color="gray"),
    ])


def on_action(action, value, state):
    if action == "on":
        state["on"] = value
    return state


def layouts(state):
    return [
        layout("zh9-t9", "中文九键", icon="keyboard", rows=[
            [layout_key("'", action="insert"),
             layout_key("ABC", action="insert"),
             layout_key("DEF", action="insert")],
            [layout_key("GHI", action="insert"),
             layout_key("JKL", action="insert"),
             layout_key("MNO", action="insert")],
            [layout_key("PQRS", action="insert"),
             layout_key("TUV", action="insert"),
             layout_key("WXYZ", action="insert")],
        ]),
    ]


def on_key(key, state):
    # A grouped key just put its whole group in. Leave one marker letter.
    low = key.lower()
    if low in DIGIT:
        replace(len(key), FIRST[DIGIT[low]])
    return state


def to_digits(word):
    out = ""
    for ch in word.lower():
        d = MARK.get(ch, "")
        if d == "":
            return ""
        out = out + d
    return out


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


def compose(seq):
    # Longest match, left to right, so a run of keys can read as a phrase.
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


def lookup(seq):
    out = []
    seen = {}
    full = compose(seq)
    if len(full) > 1:
        seen[full] = 1
        out.append(full)
    acc = seq
    for step in seq:
        if acc != "":
            for w in words_of(DICT.get(acc, "")):
                if seen.get(w, 0) == 0 and len(out) < MAX_CANDIDATES:
                    seen[w] = 1
                    out.append(w)
            acc = acc[:-1]
    return out


def suggestions(word, state):
    if not state["on"] or word == "":
        return []
    seq = to_digits(word)
    if seq == "":
        return []
    return lookup(seq)
