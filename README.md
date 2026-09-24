# Clink 中文九键 · Chinese T9 Panel

给 [Clink: Custom Keyboards](https://github.com/anti-ltd/clink-index) 用的**传统九宫格拼音输入面板**，带候选词、音节消歧和完整功能键。

A traditional nine-key (T9) Chinese pinyin input panel for Clink.

## 界面 Layout

```
┌─────────────────────────────────────────────┐
│  普通  如同  去  如  区  入  取      ← 候选词  │
├──────┬────────┬────────┬────────┬──────────┤
│  pu  │  '词   │  ABC   │  DEF   │    ⌫     │
│  qu  ├────────┼────────┼────────┼──────────┤
│  ru  │  GHI   │  JKL   │  MNO   │   重输    │
│  su  ├────────┼────────┼────────┼──────────┤
│  ↑   │  PQRS  │  TUV   │  WXYZ  │   确定    │
│ 音节  ├────────┴───┬────┴────┬───┴──────────┤
│ 消歧  │ 符号  123  │  空格   │    中 / 英    │
└──────┴────────────┴─────────┴──────────────┘
```

- **3×3 主网格** —— ITU E.161 标准分组（`2=abc` … `9=wxyz`），与所有九宫格一致
- **候选词栏** —— 按词频排序，最长匹配优先
- **左侧音节列** —— 按下 `PQRS`+`TUV` 会列出 `pu / qu / ru / su`，点选即锁定该音节，候选收窄到单字
- **`'词`** —— 分词键，提交当前已拼内容并开始新词
- **`⌫`** —— 有拼音时删一位按键，无拼音时删一个已上屏的字
- **`重输`** —— 清空当前全部输入
- **`确定`** —— 把缓冲区文字上屏
- **`空格`** —— 有候选时选中第一个候选，否则输入空格
- **`中 / 英`** —— 切英文后为传统多击输入：连按同一键在 `a→b→c` 间循环，换键即确认
- **`符号` / `123`** —— 中文标点与数字面板

## 安装 Install

1. Clink → **General → Repositories**，添加：

   ```
   dayifulalala-del/clink-layout-zh9
   ```

2. Clink → **Tools → Custom Panels**，选择本仓库，下载「中文九键 T9」。

> ⚠️ 面板包含可执行逻辑，Clink 会单独要求一次信任授权，这比纯数据的布局包更强。面板离线运行，不联网、不读文件。

## 为什么是面板，不是布局

早先本仓库提供的是 `.clinklayout` 布局文件，**打不出中文**。原因是结构性的：

- `.clinklayout` 是**一键一字符**的线性键盘格式，没有任何 T9 分组机制。把 `abc` 写进键标，Clink 会原样插入字面字符串 `abc`。
- Clink 的中文转换来自语言包的 `zh.cime` 表，是**精确读音查表**（`zhong` → 中）；九宫格需要的「一个键代表三种可能」的歧义展开，不在这套机制里。

面板是 Clink 里唯一能自绘网格、自行累积按键序列并输出候选词的机制，所以九宫格只能做成面板。原布局文件已移除。

## 输入法数据

候选词来自三个 MIT 数据集合成的词典，内嵌在面板里，完全离线：

| 来源 | 用途 |
|---|---|
| [pinyin-data](https://github.com/mozillazg/pinyin-data) | 单字 → 拼音 |
| [phrase-pinyin-data](https://github.com/mozillazg/phrase-pinyin-data) | 词语 → 拼音（正确处理多音字） |
| [jieba](https://github.com/fxsjy/jieba) | 词频，决定候选排序 |

署名与许可见 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)。

当前词典：**8,265 个按键序列**，覆盖 **87.6%** 的词频，面板 228.6 KB。

### 已知取舍

整句组合用的是**最长匹配贪心**，没有语言模型。多音歧义时首选可能不是你要的词 —— 例如 `fa`（键 `32`）的首选是「大」而不是「法」，因为「大」词频更高。从候选栏点选即可，这是九宫格固有的歧义，不是故障。

## 开发 Development

```bash
python3 tools/build-panel.py          # 重建词典与面板（首次会下载约 7 MB 源数据）
python3 tools/test-panel.py           # 执行面板逻辑，模拟打字验证
python3 tools/build-manifest.py       # 重建 manifest.json
```

`tools/test-panel.py` 用桩件实现受限 UI 原语后真正执行面板代码，模拟按键序列并断言候选词、状态迁移与上屏结果。CI 在发布前会跑这套测试。

改完推送到 `main`，GitHub Actions 自动发布 `latest` release。

## License

MIT（面板代码）。内嵌词典数据的署名见 THIRD-PARTY-NOTICES.md。
