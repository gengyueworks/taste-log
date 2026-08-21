# Taste Log · 一份有判断的网页审美档案

Taste Log 把网页灵感整理成可以再次调用的判断：每条记录包含站点、分类、收录日期、标签，以及「为什么好看」「适合什么场景」「哪个细节值得借鉴」。

它适合三种时刻：每天花两分钟看一个站，做页面前按分类找参考，或者沿着一条具体的设计判断继续深挖。

**[打开在线档案 →](https://gengyueworks.github.io/taste-log/)**

## 先从这里开始

1. 打开[在线档案](https://gengyueworks.github.io/taste-log/)，先看「今日一站」。
2. 点开原站，回到档案后点亮当天的打卡格。
3. 做页面时，在「全部档案」里按分类或关键词搜索。
4. 想找可迁移的细节，继续读[审美卡档案](docs/aesthetic-cards.md)。

打卡记录只保存在当前浏览器的 `localStorage`，不会上传。每日推荐会由 GitHub Actions 生成 issue，并追加到 `data/daily-picks.json`。

## 内容结构

| 入口 | 用途 |
| --- | --- |
| 在线首页 | 今日推荐、全年打卡、搜索、分类筛选、时间线和推荐历史 |
| `data/sites.json` | 站点档案的主数据 |
| `data/daily-picks.json` | 每日推荐的历史记录 |
| `docs/aesthetic-cards.md` | 从具体页面细节提炼出的审美卡片 |
| `docs/criteria.md` | 站点进入主库前要满足的收录标准 |
| `docs/preferences.md` | 个人审美偏好与判断维度 |

## 这份档案的判断方式

每条记录尽量回答四个问题：

1. 第一眼读到的气质是什么？
2. 哪个结构、节奏或交互决定了这种气质？
3. 它适合什么类型的内容或产品？
4. 哪个具体细节值得借鉴到自己的页面？

形容词可以作为入口，具体决策才是记录的核心。完整标准见[收录标准](docs/criteria.md)，判断维度见[审美判断体系](docs/preferences.md)。

## 里面有什么

| 内容 | 说明 |
|------|------|
| **49 个站点** | 每个带分类、收录日期、标签 |
| **15 条设计判断** | 具体到「哪一块好」「适合什么场景」「什么细节能迁移」，持续补 |
| **9 个分类** | 杂志刊物感 / 长文阅读页 / 产品与工具界面 / 字体工作室 / 设计工作室 / 交互与动效 / 品牌识别 / 策展网络 / 个人主页 |
| **4 个精华** | Kinfolk（编辑气质）· Craft（温柔工具感）· Land-book（抓模块）· Linear（科技秩序） |
| **4 个源头站** | 自己找站时从哪进，各自适合干什么 |
| **21 张审美卡** | 一卡一判断：「喜欢哪一块」+「能拿走」，做页面时的细节弹药库 |
| **打卡链** | 全年 365 格，localStorage 本地存，不上传任何数据 |

## 收录标准

一个站需要同时满足以下三点：

1. 第一屏能支持清楚的气质判断。
2. 信息层级、结构和节奏整体成立。
3. 至少有一个模块、节奏、文案或交互决策可以迁移。

以下情况暂不进入主库：链接失效、只有单点效果、结构与内容无法支撑视觉表现、或暂时说不清具体喜欢哪一块。

## 提交一个候选站点

请[新建 issue](https://github.com/gengyueworks/taste-log/issues/new)，提供下面四项信息：

```text
站点：https://example.com
分类：产品与工具界面
喜欢哪一块：一句具体判断，写清楚位置、动作或节奏
能拿走什么：可选，写一个可迁移的模块或决策
```

一句「很高级」无法帮助维护者判断。可以描述首屏的信息量、滚动节奏、导航存在感、文字与图片的关系，或者某个交互如何服务内容。

详细格式见[贡献指南](CONTRIBUTING.md)。

## 本地运行

```bash
git clone https://github.com/gengyueworks/taste-log.git
cd taste-log
python3 -m http.server 8000
```

然后打开 <http://localhost:8000>。首页通过 `fetch` 读取 `data/sites.json`，直接双击 `index.html` 时浏览器会拦截本地文件请求。

## 项目结构

```text
.
├── index.html                    # 在线档案首页
├── data/
│   ├── sites.json                # 站点主数据
│   └── daily-picks.json          # 每日推荐历史
├── docs/
│   ├── aesthetic-cards.md        # 审美卡档案
│   ├── criteria.md               # 收录标准
│   └── preferences.md            # 审美判断体系
├── scripts/
│   ├── candidate-radar.py        # 每日推荐与候选扫描
│   └── test_taste_log.py         # 无网络单元测试
└── .github/workflows/
    └── daily-candidates.yml     # 每日自动任务
```

## 自动化

`.github/workflows/daily-candidates.yml` 每天按北京时间 09:30 运行：

- 从主库挑选当天推荐；
- 发布带 `daily-pick` 标签的 GitHub issue；
- 把推荐追加到 `data/daily-picks.json`；
- 提交并推送当天的数据变化；
- 从几个灵感源头扫描候选链接，候选只进入 issue，等待人工判断。

本地运行脚本时，如果没有 `GITHUB_TOKEN`，脚本会生成推荐内容并打印，不会创建 issue。

## 授权

正文、判断和代码按 [CC BY 4.0](LICENSE) 授权，使用时请保留署名。收录站点的名称和链接归各自所有者所有；本项目只做索引与评述，不保存站点截图或素材。

---

<a name="english"></a>

# Taste Log · A web-design archive with a point of view

Taste Log turns web references into reusable design judgment. Each entry keeps the site, category, date, tags, a reason it works, the context it fits, and a detail worth borrowing.

Use it in three ways: look at one site a day, search the archive before designing a page, or follow a specific design decision into the deeper notes.

**[Open the online archive →](https://gengyueworks.github.io/taste-log/)**

## Start here

1. Open the [online archive](https://gengyueworks.github.io/taste-log/) and read the site of the day.
2. Visit the original site, then return and mark the day complete.
3. Search the archive by category, name, tag, or design note.
4. Read the [Aesthetic Cards](docs/aesthetic-cards.md) when you need a transferable detail.

The streak lives in the current browser's `localStorage`; no data is uploaded. GitHub Actions publishes a daily recommendation issue and appends the record to `data/daily-picks.json`.

## What's inside

- **49 sites**, each with category, date and tag
- **15 design notes** — specific about which part works, what context it fits, what's transferable
- **9 categories** — editorial, longform reading, product UI, type foundries, design studios, motion, brand identity, curation, portfolios
- **4 pinned picks** — Kinfolk, Craft, Land-book, Linear
- **A streak grid** — 365 cells, stored in localStorage, nothing uploaded

| Entry point | Use it for |
| --- | --- |
| Online homepage | Daily pick, yearly streak, search, filters, timeline, and recommendation history |
| `data/sites.json` | Source of truth for the site archive |
| `data/daily-picks.json` | History of daily recommendations |
| `docs/aesthetic-cards.md` | Specific visual and interaction observations |
| `docs/criteria.md` | Inclusion bar for the main archive |
| `docs/preferences.md` | Personal taste and judgment dimensions |

## How entries are judged

Each entry should answer four questions:

1. What character does the first screen establish?
2. Which structure, rhythm, or interaction creates it?
3. What kind of content or product does it suit?
4. Which concrete detail could transfer to another page?

Descriptors are a starting point. Concrete decisions are the archive's core. See the [inclusion criteria](docs/criteria.md) and the [taste system](docs/preferences.md) for the full method.

## Contribute a site

Open a [new issue](https://github.com/gengyueworks/taste-log/issues/new) with:

```text
Site: https://example.com
Category: Product & tool UI
Which part you like: One specific observation about a location, action, or rhythm
What's transferable: Optional — a module or decision worth carrying forward
```

“Looks premium” is too vague to review. Describe the first screen, scroll rhythm, navigation, relationship between type and image, or the way an interaction serves the content.

See [Contributing](CONTRIBUTING.md) for the complete format.

## Run locally

```bash
git clone https://github.com/gengyueworks/taste-log.git
cd taste-log
python3 -m http.server 8000
```

Open <http://localhost:8000>. The homepage loads `data/sites.json` with `fetch`, so opening `index.html` directly will be blocked by the browser's local-file policy.

## Automation

`.github/workflows/daily-candidates.yml` runs every day at 09:30 China Standard Time. It publishes the daily pick, records it in `data/daily-picks.json`, commits the change, and scans a few inspiration sources for candidates awaiting human review.

Without `GITHUB_TOKEN`, the local script prints the generated recommendation and skips issue creation.

## License

Text, judgment notes, and code are released under [CC BY 4.0](LICENSE). Keep attribution when you use them. Linked sites and their names belong to their respective owners; this project indexes and comments on them without storing screenshots or assets.
