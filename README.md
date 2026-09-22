# Clink 中文九键布局 · Chinese T9 Layout

给 [Clink: Custom Keyboards](https://github.com/anti-ltd/clink-index) 用的中文拼音九键（T9）键盘布局。

Chinese T9 Pinyin layout for Clink Keyboard.

## 布局 Layout

采用 ITU E.161 国际标准分组（也就是手机九宫格几十年来的那一套），按 2–9 键顺序从左到右、从上到下排列：

```
┌──────┬──────┬──────┐
│ ABC  │ DEF  │ GHI  │
├──────┼──────┼──────┤
│ JKL  │ MNO  │ PQRS │
├──────┼──────┼──────┤
│ TUV  │ WXYZ │
└──────┴──────┘
```

26 个字母各出现一次，无重复、无遗漏。

之所以不做"优化过"的自定义分组：九宫格的价值全在肌肉记忆。任何偏离标准分组的排列，理论上再优也会让熟练用户变慢。

The grouping is standard ITU E.161 (`2=abc` … `9=wxyz`), laid out in key order. All 26 letters appear exactly once. Muscle memory is the whole point of a T9 grid, so the grouping is deliberately not "optimised" away from the standard.

## 安装 Install

1. 打开 Clink → **General → Repositories**，添加本仓库：

   ```
   dayifulalala-del/clink-layout-zh9
   ```

2. 进入 **Customize → Layout → Layout packs**，在本仓库来源下找到「中文九键 Chinese T9」。
3. 下载后它会出现在 **Yours** 里，之后的版本会自动更新同一个布局，不会产生重复项。

> Clink 只接受来自 GitHub release manifest 的布局。本仓库的 GitHub Actions 会在推送到 `main` 后自动构建 manifest 并刷新 `latest` release —— 安装前请确认 release 已经生成。

## 说明 Scope

`.clinklayout` 文件描述的是**字母在键位上的排布**，它是纯数据，不含代码。

- 空格、退格、Shift、地球键、换行等功能键由 Clink 自己绘制，**不写在布局文件里**。
- 中文候选词、拼音分词、联想等由 Clink 的输入引擎和中文语言包负责，本仓库不参与。

首次使用建议先把 `.clinklayout` 文件导入 Clink 实机试打一遍，确认手感和渲染效果符合预期。

## 开发 Development

改完 `Layouts/*.clinklayout` 后推送到 `main` 即可，GitHub Actions 自动发布。不要手写 `manifest.json`，它由工作流生成。

校验布局文件：

```bash
python3 -c "
import json, collections
d = json.load(open('Layouts/zh9-chinese-t9.clinklayout'))
keys = [k for r in d['rows'] for k in r]
letters = ''.join(keys)
assert d['id'].startswith('custom-'), 'id must start with custom-'
assert len(d['rows']) == 3, 'must be exactly three rows'
assert all(k.isalpha() and k.islower() for k in keys), 'labels must be lowercase'
assert collections.Counter(letters) == collections.Counter('abcdefghijklmnopqrstuvwxyz'), 'letter coverage'
print('OK', keys)
"
```

## License

MIT
