# Clink 中文九键布局 · Chinese T9 Layout

给 [Clink: Custom Keyboards](https://github.com/anti-ltd/clink-index) 用的中文拼音九宫格（T9）键盘布局。

Chinese T9 Pinyin layout for Clink Keyboard.

## 布局 Layout

传统 3×3 九宫格，分组采用 ITU E.161 国际标准（`2=abc` … `9=wxyz`），键位与 iOS 九宫格一致 —— ABC 在上排正中，左上角为分词键 `'`：

```
┌──────┬──────┬──────┐
│  '   │ ABC  │ DEF  │
├──────┼──────┼──────┤
│ GHI  │ JKL  │ MNO  │
├──────┼──────┼──────┤
│ PQRS │ TUV  │ WXYZ │
└──────┴──────┴──────┘
```

26 个字母各出现一次，无重复、无遗漏。左上角 `'` 是拼音隔音符（`xi'an` / `xian`），对应 iOS 九宫格的分词键位置。

之所以不做"优化过"的自定义分组：九宫格的价值全在肌肉记忆。任何偏离标准分组的排列，理论上再优也会让熟练用户变慢。

Traditional 3×3 grid using the standard ITU E.161 grouping, positioned to match iOS: ABC top-centre, the pinyin apostrophe separator top-left. All 26 letters appear exactly once.

## 打不出中文？Chinese not working?

**布局文件不负责中文输入。** 它只描述字母落在哪个键位上。

Clink 的中文转换来自**语言包**：`zh.cime` 提供「读音 → 汉字」查表（Pinyin → Hanzi）。没装中文语言包，任何布局都只能打出拉丁字母。

请确认：

1. Clink → **Languages** → 安装 **🇨🇳 Chinese** 语言包
2. 键盘已切换到中文输入
3. 再配合本布局使用

> ⚠️ 已知限制：Clink 的 `.cime` 是**精确读音查表**（`zhong` → 中）。九宫格需要的是「一个键代表 abc 三种可能」的歧义展开，而 `.clinklayout` 格式**没有 T9 分组机制**，所有已知官方与社区布局都是一键一字符。因此本布局能否真正驱动九键中文输入，取决于 Clink 引擎本身是否支持多字母键位 —— 这一点无法从布局文件侧解决。

## 安装 Install

1. 打开 Clink → **General → Repositories**，添加本仓库：

   ```
   dayifulalala-del/clink-layout-zh9
   ```

2. 进入 **Customize → Layout → Layout packs**，在本仓库来源下找到「中文九键 Chinese T9」。
3. 下载后它会出现在 **Yours** 里，之后的版本会自动更新同一个布局，不会产生重复项。

> Clink 只接受来自 GitHub release manifest 的布局。本仓库的 GitHub Actions 会在推送到 `main` 后自动构建 manifest 并刷新 `latest` release。

## 说明 Scope

`.clinklayout` 文件是纯数据，不含代码。

- 空格、退格、Shift、地球键、换行等功能键由 Clink 自己绘制，**不写在布局文件里**。
- 中文候选词、拼音转汉字由 Clink 的输入引擎和中文语言包负责，本仓库不参与。

## 开发 Development

改完 `Layouts/*.clinklayout` 后推送到 `main` 即可，GitHub Actions 自动发布。不要手写 `manifest.json`，它由工作流生成。

校验布局文件：

```bash
python3 -c "
import json, collections
d = json.load(open('Layouts/zh9-chinese-t9.clinklayout'))
rows = d['rows']
keys = [k for r in rows for k in r]
letters = ''.join(k for k in keys if k.isalpha())
assert d['id'].startswith('custom-'), 'id must start with custom-'
assert len(rows) == 3, 'must be exactly three rows'
assert [len(r) for r in rows] == [3, 3, 3], 'must be a 3x3 grid'
assert collections.Counter(letters) == collections.Counter('abcdefghijklmnopqrstuvwxyz'), 'letter coverage'
print('OK', keys)
"
```

## License

MIT
