# DESIGN.md 工具指南 · getdesign.md 使用手册

> 收录日期：2026-08-21
>
> 一句话：getdesign.md 是一个「设计系统说明书」目录库——把知名网站的配色、字体、间距、组件规则拆成一份 AI 能直接读懂的 markdown（叫 DESIGN.md），丢进项目根目录，AI 编程工具就能按同一套视觉语言出页面，而不是每次都生成千篇一律的「通用 AI 布局」。

---

## 一、它解决我们的什么问题

我们的痛点：用 AI 做网站，页面功能没问题，但视觉总是「AI 默认味」——居中 hero、紫色渐变、圆角卡片三件套。

taste-log 记的是「哪个网站好看、为什么好看」（判断层），DESIGN.md 是把这种判断变成 **agent 可执行的形式**（执行层）：

| 文件 | 谁来读 | 定义什么 |
|------|--------|----------|
| `AGENTS.md` | 编程 agent | 项目怎么建 |
| `DESIGN.md` | 设计 agent | 项目长什么样 |

这是 Google Stitch 提出的开放规范，就是普通 markdown，不需要 Figma、不需要 JSON、不需要任何工具解析。

## 二、一份 DESIGN.md 里有什么

每份按 Stitch 规范扩展成 9 个部分：

1. **视觉主题与氛围** —— 密度、气质、设计哲学
2. **色板与角色** —— 语义命名 + 色值 + 功能角色
3. **字体规则** —— 字族 + 完整字号层级表
4. **组件样式** —— 按钮 / 卡片 / 输入框 / 导航，含各状态
5. **布局原则** —— 间距刻度、栅格、留白哲学
6. **深度与层级** —— 阴影体系、表面层级
7. **Do's and Don'ts** —— 设计护栏与反模式清单
8. **响应式行为** —— 断点、触控目标、折叠策略
9. **Agent Prompt 指南** —— 速查色表 + 即用 prompt

## 三、三条获取路径

### 路径 1：免费目录直接拿（首选）

- 目录页：https://getdesign.md/design-md （300+ 站点分析，网页可看）
- 开源仓库：https://github.com/VoltAgent/awesome-design-md （MIT 协议，raw 文件直接复制，含每站的 `preview.html` 视觉目录）

值得看的对标：Linear（极简精准）、Stripe（紫渐变优雅）、Notion（暖极简衬线）、WIRED（报纸密度杂志感）、The Verge（酸薄荷编辑风）、Kinfolk 类的可以自己提。

### 路径 2：让 agent 给我们自己的站写一份（最实用）

照上面 9 部分的格式，让 agent 从现有站点反向提取。我们已经有一批「风格已固化」的站可以直接提取：

- ai-news 的克莱因蓝风格（目前固化在 `build.py` 顶部 CSS 常量）
- shikang-reading 的宋体纸感阅读排版（宋体 Songti SC、米白 #fbf9f4、陶土红 #a8432b、17px/行高 2/首行缩进 2em）

提取成 DESIGN.md 后，新页面就不用每次翻 build.py 找颜色了。

### 路径 3：付费私人定制（暂不需要）

官方提供「指定任意网站定制 DESIGN.md」的付费服务（Catalog Pass / Private Request）。开源仓库 + 自己提取已经够用，先不花这个钱。

## 四、怎么用（3 步）

```
1. 复制一份 DESIGN.md 到项目根目录
2. 告诉 AI agent：「按照 DESIGN.md 构建/美化这个页面」
3. 之后所有新页面自动沿用同一套视觉语言
```

配合 taste-log 的完整工作流：

```
翻审美卡（docs/aesthetic-cards.md）→ 定对标方向
→ 去 getdesign.md 找最接近的 DESIGN.md（或自己提取）
→ 放进项目根目录 → agent 开工
→ 新的判断再写回审美卡
```

## 五、注意事项

- **借鉴原则，不照搬整套**：拿来的 DESIGN.md 是起点，要按自己的审美偏好改（见 docs/preferences.md），否则会变成「别人网站的复刻」。
- **版权边界**：这些文件提取的是公开可见的 CSS 值，MIT 协议可用；但整站视觉识别不要原样冒充自己的品牌。
- **DESIGN.md 不是银弹**：它管「一致性」，不管「品味」。选哪份对标、改哪些细节，还是靠 taste-log 里攒的判断。
- **中英双语铁律**：给我们自己的站写 DESIGN.md 时，同样要双语交付。

## 六、链接清单

- 主站目录：https://getdesign.md/
- 全部目录：https://getdesign.md/design-md
- 规范说明：https://getdesign.md/what-is-design-md
- Google Stitch 官方规范：https://stitch.withgoogle.com/docs/design-md/overview/
- 开源仓库（MIT）：https://github.com/VoltAgent/awesome-design-md
- 本库对应条目：data/sites.json → sources → getdesign.md

---

## English Version

**What it is**: getdesign.md is a catalog of DESIGN.md files — plain-markdown design system documents (a spec introduced by Google Stitch) that AI coding agents read to generate visually consistent UI. Drop one into a project root and every new page follows that visual language instead of generic AI defaults.

**Each file covers 9 sections**: visual theme & atmosphere, color palette & roles, typography rules, component stylings, layout principles, depth & elevation, do's and don'ts, responsive behavior, and an agent prompt guide.

**Three ways to get one**:

1. Free: browse https://getdesign.md/design-md or copy raw files from the MIT-licensed repo https://github.com/VoltAgent/awesome-design-md
2. Best for us: have an agent reverse-extract a DESIGN.md from our own sites whose styles are already settled (ai-news klein-blue, shikang-reading paper-reading typography)
3. Paid private requests exist — not needed while free routes work

**How it fits taste-log**: taste-log stores aesthetic judgments ("why this looks good"); a DESIGN.md is the executable form of such a judgment. Workflow: browse aesthetic cards → pick a reference direction → grab or extract a DESIGN.md → let the agent build → log new judgments back.

**Caveats**: borrow principles rather than cloning a whole identity; DESIGN.md enforces consistency, not taste — the taste still comes from this archive.
