# Taste Log · 一份有判断的网页审美档案

> 我收藏过很多好看的网站。收藏夹里躺着几百个链接，真到要做页面的时候，一个都想不起来。就算翻到了，也只剩一个域名——当时到底是被哪一块打动的，早忘干净了。
>
> 2026 年 3 月我开始认真做这件事：每天挑几个站，不光存链接，还写清楚为什么好看、适合什么内容、哪个细节以后能拿走用。攒了 47 个站，还整理出一套自己的判断标准。做到第 10 天，断了。
>
> 断掉的原因不是内容不好，是没有每天回来的理由。库藏在硬盘里，不打开就等于不存在。所以这次我把 Seinfeld 的「别断链」打卡法直接焊进首页——每天推一个站，看完点亮一格，断了自己看得见。链接谁都能列，值钱的是判断；判断谁都能写，难的是坚持写。

[English version ↓](#english)

**[打开档案 →](https://gengyueworks.github.io/taste-log/)**

---

## 这是什么

一份网页设计的策展档案。和普通的「设计灵感网站合集」有三点不一样：

**一、每条都有判断，不只有链接。** 收录标准是能回答「你具体喜欢哪一块」。写不出来的，说明还没看懂，先不收。

**二、中文语境的设计判断。** Awwwards、Land-book、Godly 这些站都很好，但它们给的是图。「为什么这个留白舒服」「这个蓝为什么只能出现在这几个位置」——这层中文圈基本没人写。

**三、带机制，不只是内容。** 站点里内置一个全年打卡格子（在「今日一站」下方），看完点亮一格；另外每天会在 GitHub 上发一条「今日推荐」issue，推一个站给你。这套机制就是这个库上次死掉的反面——没有每天回来的理由，库就等于不存在。

## 怎么用

- **每天 GitHub 上会多一条「今日推荐」**：自动发的，点开看一眼，顺手去站点点亮打卡格。
- **每天两分钟**：打开首页，看「今日一站」，点开原站扫一眼，回来点亮。
- **做页面时**：按分类筛（长文阅读页 / 产品界面 / 字体工作室 / 交互动效 / 品牌识别……），找对标。
- **想深挖**：读 [收录标准](docs/criteria.md) 和 [审美判断体系](docs/preferences.md)。

## 里面有什么

| 内容 | 说明 |
|------|------|
| **47 个站点** | 每个带分类、收录日期、标签 |
| **15 条设计判断** | 具体到「哪一块好」「适合什么场景」「什么细节能迁移」，持续补 |
| **9 个分类** | 杂志刊物感 / 长文阅读页 / 产品与工具界面 / 字体工作室 / 设计工作室 / 交互与动效 / 品牌识别 / 策展网络 / 个人主页 |
| **4 个精华** | Kinfolk（编辑气质）· Craft（温柔工具感）· Land-book（抓模块）· Linear（科技秩序） |
| **4 个源头站** | 自己找站时从哪进，各自适合干什么 |
| **打卡链** | 全年 365 格，localStorage 本地存，不上传任何数据 |

## 收录标准

一个站至少满足下面三条中的三条才收（是的，三条全要）：

1. 第一屏能说出明确的气质判断
2. 结构和节奏足够成熟，不是靠单点效果撑
3. 有能拿走用的东西——某个模块、某种节奏、某个决策

**明确不收：**

- 只靠流行渐变和 3D 插画撑起来的
- 只有热闹动效、没有结构判断的
- 标准 SaaS 模板脸
- 链接打不开的（设计再好也按无效处理）

完整标准见 [docs/criteria.md](docs/criteria.md)。

## 一条记录长什么样

不是这样：

> Kinfolk — 生活方式杂志，很好看。

是这样：

> **Kinfolk** · 杂志刊物感 · 精华
> 主站气质的母本。图片、文字、留白之间的关系是被编辑过的，不是排出来的。生活世界感来自内容本身，不靠滤镜和字体撑。

再比如：

> **Machines of Loving Grace** · 长文阅读页
> 目录跟着阅读状态走，但存在感压得很低——像安静地陪读，不是不断打断。这类页面的设计目标不是展示花样，是保护注意力。适合 manifesto、作者观点页、需要建立信任感的深度内容。

## 参与

看到该收的站，[开个 issue](https://github.com/gengyueworks/taste-log/issues/new)，按这个格式：

```
站点：https://example.com
分类：产品与工具界面
喜欢哪一块：（一句话，要具体。「很高级」这种不算）
能拿走什么：（可选）
```

只有链接、说不出喜欢哪一块的，会先放着不收。这不是挑剔，是这个库唯一的护城河。

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 本地运行

```bash
git clone https://github.com/gengyueworks/taste-log.git
cd taste-log
python3 -m http.server 8000
# 打开 http://localhost:8000
```

直接双击 `index.html` 会因为浏览器 CORS 策略读不到 `data/sites.json`，得起个本地服务。

## 授权

内容采用 [CC BY 4.0](LICENSE)。随便拿去用、改、商用，署名就行。

收录的网站链接和站名属于各自所有者，本库只做索引和评述，不存任何截图或素材。

---

<a name="english"></a>

# Taste Log · A curated archive of web design, with opinions

> I've bookmarked hundreds of beautiful websites. When it's actually time to design a page, I can't recall a single one. And even when I dig one up, all that's left is a domain name — whatever it was that struck me back then is long gone.
>
> In March 2026 I started doing this properly: pick a few sites each day, and instead of just saving the link, write down why it works, what kind of content it suits, and which detail is worth stealing later. I got to 47 sites and a working set of criteria. On day ten, it died.
>
> It didn't die because the content was bad. It died because there was no reason to come back. A library buried on a hard drive doesn't exist. So this time I welded Seinfeld's "don't break the chain" straight into the homepage — one site a day, mark it when you've looked, and a broken streak is impossible to ignore. Anyone can list links. The judgment is the value. Writing the judgment is easy; keeping it up is the hard part.

**[Open the archive →](https://gengyueworks.github.io/taste-log/)**

## What this is

A curated archive of web design. Three things make it different from a typical "design inspiration" list:

**1. Every entry carries a judgment, not just a URL.** The bar for inclusion is being able to answer "which specific part do you like?" If I can't articulate it, I haven't understood it yet — so it doesn't go in.

**2. Design criticism in Chinese.** Awwwards, Land-book and Godly are great, but they give you images. *Why* this whitespace feels right, *why* that blue only works in three specific places — almost nobody writes this layer in Chinese.

**3. It ships with a mechanism, not just content.** The homepage has a full-year grid. One site per day, mark it when you've looked. That's not a gimmick — the lack of it is exactly what killed this project the first time.

## What's inside

- **47 sites**, each with category, date and tag
- **15 design notes** — specific about which part works, what context it fits, what's transferable
- **9 categories** — editorial, longform reading, product UI, type foundries, design studios, motion, brand identity, curation, portfolios
- **4 pinned picks** — Kinfolk, Craft, Land-book, Linear
- **A streak grid** — 365 cells, stored in localStorage, nothing uploaded

## Inclusion criteria

A site must meet all three:

1. The first screen supports a clear read on its character
2. Structure and pacing are mature — not carried by one trick
3. Something is transferable: a module, a rhythm, a decision

**Automatic no:** trend gradients and 3D illustrations doing all the work; motion without structural thinking; generic SaaS template face; dead links (a great design behind a broken URL counts as invalid).

## Contributing

Open an [issue](https://github.com/gengyueworks/taste-log/issues/new) with the site URL, a category, and — required — one specific sentence on which part you like. "Looks premium" doesn't count. That specificity is the only moat this archive has.

## License

Content under [CC BY 4.0](LICENSE). Use it, remix it, sell it — just credit.

Linked sites and their names belong to their respective owners. This archive indexes and comments; it stores no screenshots or assets.
