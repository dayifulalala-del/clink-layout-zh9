# Third-party notices

`Panels/zh9-t9-pinyin.clinkpanel` embeds a pinyin dictionary derived from the
following open datasets. All three are MIT licensed. The derived dictionary is
redistributed under the same terms; these notices are retained as the MIT
licence requires.

Rebuild the dictionary from these sources with `python3 tools/build-panel.py`.

---

## pinyin-data — 汉字拼音数据

<https://github.com/mozillazg/pinyin-data>

```
The MIT License (MIT)

Copyright (c) 2016 mozillazg
```

Used for: single character → pinyin reading.

---

## phrase-pinyin-data — 词语拼音数据

<https://github.com/mozillazg/phrase-pinyin-data>

```
The MIT License (MIT)

Copyright (c) 2017 mozillazg
```

Used for: multi-character phrase → pinyin, which resolves 多音字 correctly
where a per-character lookup would not.

---

## jieba — 结巴中文分词

<https://github.com/fxsjy/jieba>

```
The MIT License (MIT)

Copyright (c) 2013 Sun Junyi
```

Used for: word frequencies, which rank the candidate list so that common
words appear first.

---

Full licence texts are available at each project's repository. The MIT licence
grants permission to use, copy, modify, merge, publish and distribute copies,
subject to the copyright notices above being retained.
