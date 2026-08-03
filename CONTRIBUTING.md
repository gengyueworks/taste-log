# 参与贡献 · Contributing

这个库的护城河只有一条：**判断要具体**。链接谁都能列，说不清「喜欢哪一块」的链接不收。

## 怎么提一个站

开一个 [issue](https://github.com/gengyueworks/taste-log/issues/new)，按这个格式：

```
站点：https://example.com
分类：产品与工具界面
喜欢哪一块：（一句话，要具体。「很高级」「很干净」这种不算）
能拿走什么：（可选，比如「它的卡片间距节奏」「它的报错文案语气」）
```

分类从下面选一个：

- 杂志刊物感
- 长文阅读页
- 产品与工具界面
- 字体工作室
- 设计工作室
- 交互与动效
- 品牌识别
- 策展网络
- 个人主页

## 什么算「具体」

❌ 不好：`这个站很好看，很有设计感。`
✅ 好：`首屏只放一个产品名 + 一句副文案，留白压到极致，但正文区又用宽松行距，紧张和松弛在同一屏里共存。`

❌ 不好：`它的动效很丝滑。`
✅ 好：`滚动时图片以 0.8 倍速视差跟进，文字先到、图后到，制造「文字在等图」的呼吸感，不是纯炫技。`

## 什么不收

- 只靠流行渐变和 3D 插画撑起来的
- 只有热闹动效、没有结构判断的
- 标准 SaaS 模板脸
- 链接打不开的（设计再好也按无效处理）
- 说不出「喜欢哪一块」的

## 收录后会怎样

维护者（或每日候选雷达）会把站加进 `data/sites.json`，并在可能的情况下补一条「设计判断」——就是上面那种具体的、能迁移的描述。判断写不出来，说明还没看懂，会先放着。

---

## How to propose a site

Open an [issue](https://github.com/gengyueworks/taste-log/issues/new) with this format:

```
Site: https://example.com
Category: Product & tool UI
Which part you like: (one specific sentence. "Looks premium" doesn't count)
What's transferable: (optional — a module, a rhythm, a decision)
```

Categories: editorial · longform reading · product UI · type foundry · design studio · motion · brand identity · curation · portfolio.

The only bar is **specificity**. A link with no articulated reason for liking it won't be added. "Very clean" is not a reason. "The first screen has one product name and one subline, whitespace pushed to the edge, yet the body uses loose leading — tension and ease share the same screen" is.

收录标准详见 [docs/criteria.md](docs/criteria.md)，审美判断体系详见 [docs/preferences.md](docs/preferences.md)。
