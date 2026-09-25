# Clink 中文九键

给 [Clink: Custom Keyboards](https://github.com/anti-ltd/clink-plugins) 用的**九宫格拼音插件**。

它做两件事：往 **布局 → 排列** 装一个九宫格布局，并在你敲键时**往候选栏送中文词**。点 `ABC` 只留一个字母，不会吐出三个。

> ⚠️ **插件需要 Clink Pro 会员**才能运行（官方原文：*Plugins run only with a Clink Pro membership*）。

## 布局

```
┌──────┬──────┬──────┐
│  '   │ ABC  │ DEF  │
├──────┼──────┼──────┤
│ GHI  │ JKL  │ MNO  │
├──────┼──────┼──────┤
│ PQRS │ TUV  │ WXYZ │
└──────┴──────┴──────┘
```

ITU E.161 标准分组，与所有九宫格一致。左上 `'` 是拼音隔音符（分词）。

## 怎么用

打「普通」：`PQRS` `TUV` `TUV` `MNO` `MNO` `GHI`

- 每点一个分组键，输入框里**只留一个字母**（插件在 `on_key` 里立刻把 `abc` 折叠成 `a`）
- 候选栏实时给出 `普通`、`如同`、`去`、`如`…
- 点候选即替换上屏 —— 就是普通候选栏的行为

## 安装

**方式一：加仓库**

1. Clink → **General → Repositories**，添加 `dayifulalala-del/clink-layout-zh9`
2. 在**插件**里找到「中文九键」，下载并启用（插件需单独信任授权）
3. 去 **布局 → 排列**，选「中文九键」

**方式二：直接粘贴**（不想加仓库时）

打开 [`Plugins/zh9-t9.py`](Plugins/zh9-t9.py)，全选复制，粘进 Clink 的**新建插件**编辑器，保存即可。文件 54 KB，是为了能粘贴而特意控制的体积。

## 原理

Clink 插件 API 里有三个关键钩子：

| Hook | 本插件的用法 |
|---|---|
| `layouts(state)` | 用 `layout_key(glyph, action=)` 画出 3×3 九宫格，装进「布局 → 排列」 |
| `on_key(key, state)` | 分组键插入 `abc` 后立刻 `replace(3, "a")`，一个键只留一个字母 |
| `suggestions(word, state)` | 把字母标记解码回按键序列，查词库，返回中文候选 |

标记字母一一对应：`a`→2 `d`→3 `g`→4 `j`→5 `m`→6 `p`→7 `t`→8 `w`→9，所以输入框里的字母串就是按键序列。

## 词典

三个 MIT 数据集合成，离线内嵌，2,504 个按键序列，覆盖 72.4% 词频：

| 来源 | 用途 |
|---|---|
| [pinyin-data](https://github.com/mozillazg/pinyin-data) | 单字 → 拼音 |
| [phrase-pinyin-data](https://github.com/mozillazg/phrase-pinyin-data) | 词语 → 拼音（处理多音字） |
| [jieba](https://github.com/fxsjy/jieba) | 词频 → 候选排序 |

署名见 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)。词库体积是为「能粘贴」折衷过的，`tools/build-plugin.py` 可用 `WORD_BUDGET` 调大。

## 已知限制

- **整句组合是最长匹配贪心，没有语言模型。** 长句首候选可能不准，从候选栏点选即可。
- **空格不选词。** 目前只支持点候选上屏；加 `correct()` 钩子会连带插入空格，暂未启用。

## 为什么不是布局、也不是面板

实测走过的两条死路，记录在此免得重走：

| 路线 | 结果 |
|---|---|
| `.clinklayout` 布局 | 能渲染九宫格形状（四行/数字/功能键都接受，上游文档的"恰好三行小写字母"只是投稿规范），但**键标原样输出**，`abc` 就插入字面 "abc"，做不出候选 |
| `.clinkpanel` 面板 | 能做完整 T9 逻辑，但面板是「工具箱」条目，不是日常键盘 |
| **插件** | **能装布局 + 能供候选词**，长在真键盘里 ✅ |

## 开发

```bash
python3 tools/build-plugin.py                        # 重建词库与插件（首次下载约 7 MB 源数据）
python3 tools/build-manifest.py                      # 打包到 build/ 并重建 manifest.json
python3 tools/test-plugin.py build/zh9-t9.clinkplugin # 对打包产物模拟真实键盘跑测试
```

CI 在发布前会打包并跑测试。发布用内容寻址的 tag（`plugins-<sha>`），与官方插件仓库一致。

## License

MIT（插件代码）。内嵌词典数据署名见 THIRD-PARTY-NOTICES.md。
