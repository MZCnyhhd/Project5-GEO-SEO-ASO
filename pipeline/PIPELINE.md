# 产品推广流水线（Promotion Pipeline）

把原来散在 12 份文档里的 GEO × SEO × ASO 方法论，固化成**一条可重复执行的流水线**：
填一份产品配置，自动产出全部「内容与结构化」物料；涉及主体资质和平台审核的部分，单独列成清单交给人做。

---

## 一、30 秒上手

```bash
# 1. 复制配置模板，改成你的产品
cp pipeline/product.example.json pipeline/my-product.json

# 2. 跑流水线
python pipeline/generate.py my-product.json

# 3. 产物在 pipeline/out/<slug>/ 下
```

零依赖，只用 Python 3 标准库（`json` / `os` / `re` / `sys` / `datetime`）。

也可以完全不开终端，直接用浏览器控制台：**`pipeline.html`**（打开即用，表单填完点「运行流水线」，
落地页可实时预览并下载，全部文案可一键复制/下载）。

两种用法**共用同一份配置结构**：控制台用来快速试跑和预览，`generate.py` 用来批量产出与进 CI。

---

## 二、输入：一份产品配置

只需改 `pipeline/product.example.json` 一个文件。

| 字段 | 必填 | 说明 |
|---|:--:|---|
| `name` | ✅ | 产品名，用于标题、文案、结构化数据 |
| `tagline` | ✅ | 一句话定位（副标题），也是商店「一句话简介」的素材 |
| `platform` / `os_list` | ✅ | 目标平台，如 `HarmonyOS` |
| `positioning` | ✅ | 产品定位一句话，用于描述首段 |
| `description` | ✅ | 产品描述（60–150 字） |
| `features` | ✅ | 核心功能 3–5 条，`{icon, title, desc}` |
| `scenarios` | ✅ | 适用场景 2–4 条，`{icon, title, desc}` |
| `faq` | ✅ | 常见问题 ≥5 条，`{q, a}`，会同步进 FAQPage 结构化数据 |
| `channels` | ✅ | 下载渠道 ≥1 条，`{store, url, note}` |
| `ai_engines` |  | 要监测的 AI 引擎，如 `["小艺","华为搜索","豆包"]` |
| `competitors` |  | 竞品名，用于生成对比类关键词与文案 |
| `keywords.*` |  | `brand / core / scene / longtail / competitor / avoid / harmony` |
| `category` / `price` / `rating_*` |  | 结构化数据字段，可不填走默认 |
| `website` / `contact_email` / `team` |  | 落地页页脚与 canonical |

> `keywords.harmony` 是为华为应用市场「鸿蒙生态适配」权重项准备的生态词（鸿蒙原生 / 元服务 / 服务卡片）。
> 非鸿蒙产品可以留空。

---

## 三、输出：产物清单

全部写入 `pipeline/out/<slug>/`：

| 文件 | 内容 | 对应原项目环节 |
|---|---|---|
| `index.html` | 产品落地页（含 `MobileApplication` + `FAQPage` 两类 JSON-LD） | 03 官网 Schema |
| `content.md` | 多平台文案包（知乎 / 小红书 / 头条 / 百家号 / 开发者社区 / CSDN） | 12 内容包 |
| `aso.md` | 各商店 ASO 元数据 + **字符数自动校验** | 07 ASO |
| `keywords.md` | 四维关键词矩阵 + P0/P1/P2 分层 | 02 关键词矩阵 |
| `monitor.md` | AI 搜索监测问句 + 各引擎抓取偏好 | 08 监测清单 |
| `distribution.md` | 48 小时分发排期 + 72h 互动动作 | 05-06 分发 |
| `checklist.md` | **人工必做清单**（备案 / 软著 / 上架 / 资质） | 需人工 |
| `REPORT.md` | 执行报告：产物 + 校验结果 + 下一步 | — |

### ASO 字符数校验

流水线会为每个商店的每个字段计算字符数并校验上限（上限为公开字段规格，**上架前请以商店后台为准**）：

| 商店 | 字段与上限 |
|---|---|
| 华为应用市场 | 标题 64 · 一句话简介 80 · 后台关键词 100 · 应用描述 8000 |
| App Store | 标题 30 · 副标题 30 · 关键词栏 100 · 描述 4000 |
| Google Play | 标题 30 · 简短说明 80 · 完整说明 4000 |

另外会检查「描述前 200 字是否包含 P0 核心词」——流水线会把核心词自然写进描述首段，
避免出现「元数据填了关键词但搜索抓不到重点」的常见问题。

---

## 四、流水线 12 个环节与自动化程度

| # | 环节 | 自动化 |
|---:|---|---|
| 01 | 读取产品配置 | 🟢 自动 |
| 02 | 四维关键词矩阵 | 🟢 自动 |
| 03 | 产品落地页生成 | 🟢 自动 |
| 04 | 结构化数据 Schema | 🟢 自动 |
| 05 | 多平台文案 | 🟡 自动 + 人工复核语气 |
| 06 | ASO 元数据 + 字符校验 | 🟢 自动 |
| 07 | AI 搜索监测问句 | 🟢 自动 |
| 08 | 48 小时分发排期 | 🟢 自动 |
| 09 | 执行报告 | 🟢 自动 |
| 10 | 主体资质 / 软著 / ICP 备案 | 🔴 人工 |
| 11 | 应用商店上架与审核 | 🔴 人工 |
| 12 | 真人评论运营与媒体投放 | 🔴 人工 |

---

## 五、自动化边界（重要）

### 流水线能做

- 生成落地页 HTML（可直接部署到 GitHub Pages / Vercel / Netlify）
- 生成多平台文案、ASO 元数据、关键词矩阵、监测问句、分发排期
- 对字符数上限、关键词覆盖、P0 命中做程序化校验
- 输出执行报告与人工待办清单

### 流水线做不了（必须你本人完成）

| 事项 | 为什么必须人工 |
|---|---|
| 开发者实名 / 营业执照 | 涉及主体身份核验 |
| 软件著作权证书 | 需向版权中心申请，有法定周期 |
| 官网域名 ICP 备案 | 需主机与主体材料，走工信部流程 |
| 隐私政策与合规声明 | 需对真实数据处理方式负责 |
| 应用图标 / 截图 / 演示视频 | 需真人设计产出 |
| 应用商店上架提交与审核打回处理 | 需登录开发者后台并承担审核责任 |
| 真实用户好评引导、差评回复 | 必须是真人行为 |
| 科技媒体投放与预算决策 | 涉及商务与资金 |

### 合规红线（流水线不会替你碰）

- ❌ 机刷下载、买量冲榜
- ❌ 以红包 / 权益换取**指定星级**好评
- ✅ 引导评价只能要求「真实评价」，且承诺的权益必须真实可兑付

---

## 六、部署产物

落地页是单文件、零依赖的静态页，直接放到现有站点即可：

```bash
# 例：把生成的落地页作为站点的一个子页面
cp pipeline/out/<slug>/index.html landing-page/index.html
git add -A && git commit -m "promo: 更新产品落地页" && git push
```

### 挂到 GitHub Actions（每次发版自动跑）

```yaml
name: promo-pipeline
on:
  push:
    paths: ["pipeline/product.json"]
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: python pipeline/generate.py pipeline/product.json
      - uses: actions/upload-artifact@v4
        with:
          name: promo-assets
          path: pipeline/out/
```

---

## 七、常见问题

**Q：换一个产品要改多少？**
只改 `product.json`，其余不动。`slug` 变了就会输出到新目录，多产品可以并存。

**Q：文案语气不满意怎么办？**
文案模板在 `generate.py` 的 `build_content()` 里，按平台分段，直接改那一段即可；
控制台版本在同名函数 `genContent()`。

**Q：产物直接能发布吗？**
落地页可以直接发布，但要把 `XXXXXXX` 占位下载链接换成真实链接；
文案建议人工过一遍语气与事实（尤其是数字与承诺类表述）。

**Q：`checklist.md` 里的软著、备案要多久？**
以官方为准，但软著周期通常较长，**建议一立项就并行启动**，不要等开发完才办。
