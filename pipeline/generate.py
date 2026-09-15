# -*- coding: utf-8 -*-
"""
产品推广流水线 · 零依赖生成器（Python 3 标准库）

用法：
    python pipeline/generate.py                     # 使用 product.example.json
    python pipeline/generate.py 我的产品.json        # 使用自定义配置

产物（全部写入 pipeline/out/<slug>/）：
    index.html        产品落地页（含 MobileApplication / FAQPage 结构化数据）——即「修改网页产品介绍」
    content.md        多平台文案包（知乎 / 小红书 / 头条 / 百家号 / 华为开发者社区 / CSDN）
    aso.md            各应用商店 ASO 元数据 + 字符数校验
    keywords.md       四维关键词矩阵
    monitor.md        AI 搜索监测问句清单
    distribution.md   48 小时分发排期表
    checklist.md      人工必做清单（备案 / 软著 / 上架 / 资质 …）
    REPORT.md         流水线执行报告
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.join(HERE, "out")
TODAY = datetime.date.today().isoformat()

# ---------------------------------------------------------------- 商店字段规则
# 字符数上限为该商店公开字段规格，规则会变动，上架前请以商店后台为准。
STORE_RULES = [
    ("华为应用市场", [("标题", 64), ("一句话简介", 80), ("后台关键词", 100), ("应用描述", 8000)]),
    ("App Store", [("标题", 30), ("副标题", 30), ("关键词栏", 100), ("描述", 4000)]),
    ("Google Play", [("标题", 30), ("简短说明", 80), ("完整说明", 4000)]),
]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def chars(s):
    return len(str(s).replace(" ", ""))


def slugify(cfg):
    if cfg.get("slug"):
        return cfg["slug"]
    name = cfg.get("name", "product")
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return ascii_part or "product-" + str(abs(hash(name)) % 10000)


def kw(cfg, key):
    return [w for w in (cfg.get("keywords", {}) or {}).get(key, []) if w]


def all_p0(cfg):
    """P0 = 品牌词 + 核心词"""
    return kw(cfg, "brand") + kw(cfg, "core")


# ---------------------------------------------------------------- 落地页
LANDING_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif; line-height:1.6; color:#333; background:#fff; }
.container { max-width:1200px; margin:0 auto; padding:0 24px; }
a { text-decoration:none; color:inherit; }
.hero { background:linear-gradient(135deg,#FFD700 0%,#FFA500 35%,#FF8C00 70%,#FF6B35 100%); color:#fff; padding:96px 0 110px; text-align:center; }
.hero h1 { font-size:54px; font-weight:800; margin-bottom:14px; letter-spacing:2px; }
.hero .subtitle { font-size:23px; font-weight:500; margin-bottom:24px; opacity:.95; }
.hero .desc { font-size:17px; max-width:720px; margin:0 auto 44px; opacity:.92; line-height:1.8; }
.hero-buttons { display:flex; gap:18px; justify-content:center; flex-wrap:wrap; }
.btn-primary,.btn-secondary { display:inline-flex; align-items:center; gap:10px; padding:15px 36px; border-radius:50px; font-size:17px; font-weight:600; transition:all .3s ease; box-shadow:0 8px 24px rgba(0,0,0,.15); }
.btn-primary { background:#fff; color:#FF8C00; }
.btn-primary:hover { transform:translateY(-3px); }
.btn-secondary { background:rgba(255,255,255,.2); color:#fff; border:2px solid rgba(255,255,255,.6); }
.btn-secondary:hover { background:rgba(255,255,255,.35); transform:translateY(-3px); }
.slogan { margin-top:32px; font-size:18px; font-weight:500; letter-spacing:3px; opacity:.9; }
.section { padding:84px 0; }
.section-alt { background:#FFF9F2; }
.section-title { text-align:center; font-size:36px; font-weight:700; color:#222; margin-bottom:14px; }
.section-subtitle { text-align:center; font-size:17px; color:#777; margin:0 auto 56px; max-width:640px; }
.features-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:26px; }
.feature-card { background:#fff; border-radius:20px; padding:34px 28px; box-shadow:0 4px 20px rgba(255,140,0,.08); border:1px solid rgba(255,140,0,.1); transition:all .3s ease; }
.feature-card:hover { transform:translateY(-8px); box-shadow:0 12px 40px rgba(255,140,0,.18); }
.feature-icon { font-size:50px; margin-bottom:18px; display:inline-block; }
.feature-card h3 { font-size:20px; font-weight:700; color:#FF8C00; margin-bottom:12px; }
.feature-card p { font-size:15px; color:#666; line-height:1.7; }
.scenes-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:22px; }
.scene-card { background:linear-gradient(145deg,#fff,#FFF9F2); border-radius:18px; padding:38px 26px; text-align:center; border:2px solid transparent; transition:all .3s ease; }
.scene-card:hover { border-color:#FFA500; transform:scale(1.03); }
.scene-emoji { font-size:60px; margin-bottom:18px; }
.scene-card h3 { font-size:21px; font-weight:700; color:#333; margin-bottom:10px; }
.scene-card p { font-size:15px; color:#777; line-height:1.7; }
.download-section { background:linear-gradient(135deg,#FF6B35 0%,#FF8C00 50%,#FFD700 100%); color:#fff; text-align:center; padding:92px 0; }
.download-section h2 { font-size:40px; font-weight:700; margin-bottom:14px; }
.download-section .tagline { font-size:19px; opacity:.95; margin-bottom:44px; letter-spacing:1px; }
.download-buttons { display:flex; gap:22px; justify-content:center; flex-wrap:wrap; }
.download-btn { display:inline-flex; align-items:center; gap:12px; padding:17px 40px; border-radius:14px; font-size:17px; font-weight:600; background:#fff; color:#333; transition:all .3s ease; box-shadow:0 8px 28px rgba(0,0,0,.2); }
.download-btn:hover { transform:translateY(-4px); }
.download-btn .icon { font-size:27px; }
.download-btn .text small { display:block; font-size:12px; color:#888; font-weight:400; }
.faq-wrapper { max-width:860px; margin:0 auto; }
.faq-item { background:#fff; border-radius:14px; margin-bottom:14px; box-shadow:0 2px 12px rgba(0,0,0,.06); overflow:hidden; border:1px solid #F0E6D8; }
.faq-question { padding:20px 26px; font-size:17px; font-weight:600; color:#333; background:linear-gradient(90deg,#FFF9F2,#fff); cursor:pointer; display:flex; justify-content:space-between; align-items:center; }
.faq-question::after { content:"+"; font-size:24px; color:#FF8C00; transition:transform .3s ease; }
.faq-item.open .faq-question::after { transform:rotate(45deg); }
.faq-answer { padding:0 26px; max-height:0; overflow:hidden; transition:all .35s ease; font-size:15px; color:#666; line-height:1.8; }
.faq-item.open .faq-answer { padding:0 26px 22px; max-height:420px; }
footer { background:#1a1a1a; color:#aaa; padding:44px 0 30px; text-align:center; }
footer .footer-brand { font-size:20px; font-weight:700; color:#FFD700; margin-bottom:10px; }
footer .footer-slogan { font-size:14px; margin-bottom:20px; letter-spacing:2px; }
footer .copyright { font-size:13px; opacity:.7; border-top:1px solid #333; padding-top:18px; margin-top:18px; }
@media (max-width:768px){
  .hero { padding:66px 0 84px; } .hero h1 { font-size:36px; } .hero .subtitle { font-size:19px; }
  .hero .desc { font-size:15px; } .section { padding:56px 0; } .section-title { font-size:27px; }
  .download-section h2 { font-size:29px; } .features-grid,.scenes-grid { grid-template-columns:1fr; }
}
"""


def build_landing(cfg):
    name = esc(cfg.get("name", "产品"))
    feats = "\n".join(
        '      <div class="feature-card">\n'
        '        <div class="feature-icon">%s</div>\n'
        '        <h3>%s</h3>\n'
        '        <p>%s</p>\n'
        '      </div>' % (f.get("icon", "✨"), esc(f.get("title", "")), esc(f.get("desc", "")))
        for f in cfg.get("features", [])
    )
    scenes = "\n".join(
        '      <div class="scene-card">\n'
        '        <div class="scene-emoji">%s</div>\n'
        '        <h3>%s</h3>\n'
        '        <p>%s</p>\n'
        '      </div>' % (s.get("icon", "📌"), esc(s.get("title", "")), esc(s.get("desc", "")))
        for s in cfg.get("scenarios", [])
    )
    faq = cfg.get("faq", [])
    faq_html = "\n".join(
        '      <div class="faq-item">\n'
        '        <div class="faq-question">%s</div>\n'
        '        <div class="faq-answer"><p>%s</p></div>\n'
        '      </div>' % (esc(q.get("q", "")), esc(q.get("a", "")))
        for q in faq
    )
    chans = cfg.get("channels", [])
    hero_btns = "\n".join(
        '      <a href="%s" class="%s" target="_blank" rel="noopener">\n'
        '        <span style="font-size:22px;">%s</span>\n'
        '        <span>%s</span>\n'
        '      </a>' % (esc(c.get("url", "#")), "btn-primary" if i == 0 else "btn-secondary",
                      c.get("icon", "⬇"), esc(c.get("store", "下载")))
        for i, c in enumerate(chans[:2])
    )
    dl_btns = "\n".join(
        '      <a href="%s" class="download-btn" target="_blank" rel="noopener">\n'
        '        <span class="icon">%s</span>\n'
        '        <span class="text">%s<small>%s</small></span>\n'
        '      </a>' % (esc(c.get("url", "#")), c.get("icon", "⬇"),
                      esc(c.get("store", "")), esc(c.get("note", "")))
        for c in chans
    )
    feat_titles = " · ".join(f.get("title", "") for f in cfg.get("features", [])[:5])
    app_ld = {
        "@context": "https://schema.org", "@type": "MobileApplication",
        "name": cfg.get("name", ""),
        "applicationCategory": cfg.get("category", "UtilitiesApplication"),
        "operatingSystem": cfg.get("os_list", cfg.get("platform", "")),
        "offers": {"@type": "Offer", "price": str(cfg.get("price", "0")), "priceCurrency": cfg.get("currency", "CNY")},
        "description": cfg.get("description", ""),
    }
    if cfg.get("rating_value"):
        app_ld["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(cfg["rating_value"]),
            "ratingCount": str(cfg.get("rating_count", "0")),
        }
    faq_ld = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q.get("q", ""),
                        "acceptedAnswer": {"@type": "Answer", "text": q.get("a", "")}} for q in faq],
    }

    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(name)s - %(tagline)s</title>
<meta name="description" content="%(desc)s">
<meta name="keywords" content="%(kws)s">
<meta property="og:title" content="%(name)s - %(tagline)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="website">
<link rel="canonical" href="%(website)s">
<style>%(css)s</style>
<script type="application/ld+json">
%(app_ld)s
</script>
<script type="application/ld+json">
%(faq_ld)s
</script>
</head>
<body>

<section class="hero">
  <div class="container">
    <h1>%(name)s</h1>
    <div class="subtitle">%(tagline)s</div>
    <p class="desc">%(desc)s</p>
    <div class="hero-buttons">
%(hero_btns)s
    </div>
    <div class="slogan">%(slogan)s</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="section-title">核心功能</h2>
    <p class="section-subtitle">%(feat_titles)s</p>
    <div class="features-grid">
%(feats)s
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="container">
    <h2 class="section-title">适用场景</h2>
    <p class="section-subtitle">%(name)s，陪你记录每一个重要节点</p>
    <div class="scenes-grid">
%(scenes)s
    </div>
  </div>
</section>

<section class="download-section">
  <div class="container">
    <h2>立即使用 %(name)s</h2>
    <p class="tagline">%(slogan)s</p>
    <div class="download-buttons">
%(dl_btns)s
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="section-title">常见问题 FAQ</h2>
    <p class="section-subtitle">你想知道的都在这里</p>
    <div class="faq-wrapper">
%(faq_html)s
    </div>
  </div>
</section>

<footer>
  <div class="container">
    <div class="footer-brand">%(name)s</div>
    <div class="footer-slogan">%(slogan)s</div>
    <div class="copyright">© %(year)s %(team)s 版权所有 | %(email)s</div>
  </div>
</footer>

<script>
document.querySelectorAll('.faq-question').forEach(function(q){
  q.addEventListener('click', function(){
    var item = this.parentElement;
    var isOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item').forEach(function(i){ i.classList.remove('open'); });
    if (!isOpen) item.classList.add('open');
  });
});
</script>

</body>
</html>
""" % {
        "name": name,
        "tagline": esc(cfg.get("tagline", "")),
        "desc": esc(cfg.get("description", "")),
        "kws": esc(",".join(kw(cfg, "brand") + kw(cfg, "core") + kw(cfg, "scene"))),
        "website": esc(cfg.get("website", "")),
        "css": LANDING_CSS,
        "app_ld": json.dumps(app_ld, ensure_ascii=False, indent=2),
        "faq_ld": json.dumps(faq_ld, ensure_ascii=False, indent=2),
        "hero_btns": hero_btns,
        "slogan": esc(cfg.get("slogan", "")),
        "feat_titles": esc(feat_titles),
        "feats": feats,
        "scenes": scenes,
        "dl_btns": dl_btns,
        "faq_html": faq_html,
        "year": esc(cfg.get("copyright_year", "")),
        "team": esc(cfg.get("team", "")),
        "email": esc(cfg.get("contact_email", "")),
    }


# ---------------------------------------------------------------- ASO 元数据
def build_aso(cfg):
    name = cfg.get("name", "")
    tagline = cfg.get("tagline", "")
    desc = cfg.get("description", "")
    p0 = all_p0(cfg)
    L = ["# ASO 元数据清单 · %s" % name, "",
         "> 生成时间：%s ｜ 字符数上限为公开字段规格，上架前请以商店后台为准。" % TODAY, ""]

    # 华为应用市场（鸿蒙主渠道）
    core = kw(cfg, "core")
    scene_titles = [s.get("title", "") for s in cfg.get("scenarios", [])]
    title = "%s - %s" % (name, tagline) if tagline and tagline not in name else name
    short = ("%s ｜ %s" % (tagline, "、".join(core[:2]))) if (tagline and core) else (tagline or desc[:40])
    backkw = ",".join(dict.fromkeys(kw(cfg, "core") + kw(cfg, "scene") + kw(cfg, "longtail") + kw(cfg, "harmony")))[:100]
    # 描述首段必须自然带上 P0 核心词，否则搜索与 AI 抽取都抓不到重点
    lead = "%s（%s）是一款%s，核心能力包括%s%s。" % (
        name, tagline, cfg.get("positioning", "应用"),
        "、".join(core) or "事件记录与提醒",
        ("，覆盖%s等场景" % "、".join(scene_titles)) if scene_titles else "",
    )
    long_desc = "%s\n\n%s\n\n%s\n\n%s" % (
        lead, desc,
        "核心功能：" + "；".join(f.get("title", "") for f in cfg.get("features", [])),
        "适用场景：" + "；".join(scene_titles),
    )
    L += ["## 一、华为应用市场（AppGallery）", "",
          "鸿蒙应用的主分发渠道，搜索入口贡献大部分下载量。", "",
          "| 字段 | 内容 | 字符数 | 上限 | 校验 |", "|---|---|---:|---:|---|"]
    for label, val, limit in [("标题", title, 64), ("一句话简介", short, 80),
                              ("后台关键词", backkw, 100), ("应用描述", long_desc, 8000)]:
        c = chars(val)
        L.append("| %s | %s | %d | %d | %s |" % (label, val.replace("\n", "<br>"), c, limit,
                                                 "✅" if c <= limit else "❌ 超限"))

    # 描述前 200 字 P0 覆盖
    head200 = long_desc[:200]
    hit = [w for w in p0 if w in head200]
    L += ["", "- 描述前 200 字含 P0 核心词：%d/%d %s" % (len(hit), len(p0), "✅" if hit else "⚠️ 建议补入核心词"),
          "- 关键词密度建议 3%–5%，避免堆砌",
          "", "### 应用描述全文", "", "```", long_desc, "```", ""]

    # 其他商店
    L += ["## 二、其他商店（如多端发行）", ""]
    L += ["### App Store", "",
          "| 字段 | 内容 | 字符数 | 上限 | 校验 |", "|---|---|---:|---:|---|"]
    for label, val, limit in [("标题", "%s-%s" % (name, tagline), 30),
                              ("副标题", tagline, 30),
                              ("关键词栏", ",".join(dict.fromkeys(kw(cfg, "core") + kw(cfg, "scene"))), 100)]:
        c = chars(val)
        L.append("| %s | %s | %d | %d | %s |" % (label, val, c, limit, "✅" if c <= limit else "❌ 超限"))
    L += ["", "### Google Play", "",
          "| 字段 | 内容 | 字符数 | 上限 | 校验 |", "|---|---|---:|---:|---|"]
    for label, val, limit in [("标题", name, 30), ("简短说明", tagline, 80),
                              ("完整说明（前 200 字）", desc[:200], 4000)]:
        c = chars(val)
        L.append("| %s | %s | %d | %d | %s |" % (label, val, c, limit, "✅" if c <= limit else "❌ 超限"))
    L += ["", "## 三、鸿蒙生态适配（2026 华为新增权重项）", "",
          "华为应用市场排序中「鸿蒙生态适配」为独立权重项，以下内容建议体现在标题/描述中：", ""]
    for w in kw(cfg, "harmony") or ["鸿蒙原生", "元服务", "服务卡片"]:
        L.append("- %s" % w)
    L += ["", "## 四、视觉与转化素材（需人工产出）", "",
          "- 应用图标：高对比、贴合华为用户审美，建议 A/B 测试",
          "- 截图：前 3 张突出核心功能与鸿蒙适配，第 4 张放用户好评，第 5 张引导下载",
          "- 视频：15–30 秒，展示服务卡片与提醒效果", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- 关键词矩阵
def build_keywords(cfg):
    name = cfg.get("name", "")
    L = ["# 四维关键词矩阵 · %s" % name, "",
         "> 按「用户在 AI 面前提问的方式」反推，而非堆搜索量。", ""]
    groups = [
        ("疑问类", kw(cfg, "core"), "用户直接求推荐，拦截需求"),
        ("对比类", kw(cfg, "competitor"), "拦截竞品流量"),
        ("场景类", kw(cfg, "scene") + kw(cfg, "longtail"), "吃长尾，覆盖真实使用场景"),
        ("避坑类", kw(cfg, "avoid"), "承接决策前疑虑"),
    ]
    L += ["| 维度 | 数量 | 作用 | 关键词 |", "|---|---:|---|---|"]
    total = 0
    for gname, words, role in groups:
        total += len(words)
        L.append("| %s | %d | %s | %s |" % (gname, len(words), role, "、".join(words) if words else "—"))
    L += ["| **合计** | **%d** |  |  |" % total, ""]
    L += ["## 品牌词与鸿蒙生态词", "",
          "- 品牌词：%s" % ("、".join(kw(cfg, "brand")) or "—"),
          "- 鸿蒙生态词：%s" % ("、".join(kw(cfg, "harmony")) or "—"), ""]
    L += ["## 优先级分层", "",
          "- P0（品牌 + 核心）：%s" % ("、".join(all_p0(cfg)) or "—"),
          "- P1（场景 + 长尾）：%s" % ("、".join(kw(cfg, "scene") + kw(cfg, "longtail")) or "—"),
          "- P2（对比 + 避坑）：%s" % ("、".join(kw(cfg, "competitor") + kw(cfg, "avoid")) or "—"), ""]
    L += ["## 布局规范", "",
          "- 标题承担最高权重：格式建议「品牌名 + 核心功能词 + 场景词」，通顺不堆砌",
          "- 简述嵌入 1 个核心词 + 1 个长尾词，核心信息前置",
          "- 后台关键词填满字符上限，补充标题未覆盖的近义词与鸿蒙相关词",
          "- 描述前 200 字必须出现核心词，全篇密度 3%–5%", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- 监测问句
def build_monitor(cfg):
    name = cfg.get("name", "")
    engines = cfg.get("ai_engines", ["小艺", "华为搜索"])
    p0 = all_p0(cfg)
    qs = []
    for w in kw(cfg, "brand"):
        qs.append(("P0", "疑问类", "%s 是什么" % w))
    for w in kw(cfg, "core"):
        qs.append(("P0", "疑问类", "%s 推荐" % w))
        qs.append(("P1", "疑问类", "%s 哪个好用" % w))
    for c in cfg.get("competitors", []):
        qs.append(("P2", "对比类", "%s 和 %s 哪个好" % (name, c)))
    for w in kw(cfg, "scene"):
        qs.append(("P1", "场景类", "%s 用什么工具" % w))
    for w in kw(cfg, "longtail"):
        qs.append(("P1", "场景类", w))
    for w in kw(cfg, "avoid"):
        qs.append(("P2", "避坑类", w))
    for w in kw(cfg, "harmony"):
        qs.append(("P1", "场景类", "鸿蒙 %s 相关应用推荐" % w))

    L = ["# AI 搜索监测问句清单 · %s" % name, "",
         "> 三固定原则：固定账号、固定设备、固定时段。每条记录「是否推荐 / 排名 / 引用来源 / 截图」。", "",
         "## 监测引擎与抓取偏好", "",
         "| 引擎 | 抓取偏好 | 备注 |", "|---|---|---|"]
    pref = {
        "小艺": ("华为生态内容优先（开发者社区 / 官方文档 / 权威媒体）", "鸿蒙生态核心入口"),
        "华为搜索": ("7 天内时效 > 权威来源 > 高互动 > 原创 > 结构化", "与 AppGallery 联动"),
        "豆包": ("时效 > 权威 > 高互动 > 原创 > 结构化（EEAT 评估）", "通用 AI 搜索入口"),
        "DeepSeek": ("权威来源与长文结构化内容权重高", "技术类问题优势"),
    }
    for e in engines:
        p = pref.get(e, ("权威来源 > 时效 > 互动 > 原创", "通用"))
        L.append("| %s | %s | %s |" % (e, p[0], p[1]))
    L += ["", "## 问句清单（共 %d 条）" % len(qs), "",
          "| # | 优先级 | 维度 | 问句 | %s |" % " | ".join(engines),
          "|---:|:--:|---|---|%s" % ("---|" * len(engines))]
    for i, (pri, dim, q) in enumerate(qs, 1):
        L.append("| %d | %s | %s | %s |%s" % (i, pri, dim, q, " |" * len(engines)))
    L += ["", "## 记录字段", "",
          "问句编号 / 优先级 / 引擎 / 是否推荐 / 品牌排名 / TOP3 竞品 / 引用来源平台 / 截图文件名 / 日期", "",
          "## 目标值", "",
          "- 核心问句推荐率 ≥60%（第 3 个月）", "- TOP3 占比 ≥40%",
          "- 关键词覆盖 60+，P0 覆盖度 100%", "- 行业共识 GEO 认知建设周期 3–6 个月", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- 多平台文案
def build_content(cfg):
    name = cfg.get("name", "")
    tagline = cfg.get("tagline", "")
    desc = cfg.get("description", "")
    feats = cfg.get("features", [])
    scenes = cfg.get("scenarios", [])
    faq = cfg.get("faq", [])
    comp = cfg.get("competitors", [])
    feat_lines = [("- %s：%s" % (f.get("title", ""), f.get("desc", ""))) for f in feats]
    scene_lines = [("- %s：%s" % (s.get("title", ""), s.get("desc", ""))) for s in scenes]
    qa = ["**%s**\n%s" % (q.get("q", ""), q.get("a", "")) for q in faq]

    blocks = []
    blocks.append("\n".join([
        "# 多平台文案包 · %s" % name, "",
        "> 生成时间：%s ｜ 每条已按平台调性分开写，可直接复制粘贴。" % TODAY, "",
        "---", "", "## 1. 知乎（问答式长文，结论前置 + 分层标题）", "",
        "### 标题", "%s 值得用吗？鸿蒙用户的事件提醒方案实测" % name, "",
        "### 正文", "", "**结论前置**：%s。%s" % (tagline, desc), "",
        "**它解决了什么问题**", "",
        "在手机上记录重要日子这件事，问题从来不是「记不下来」，而是「记了但看不着」。%s 把事件放在鸿蒙服务卡片上，抬眼即可见。" % name, "",
        "**核心功能**", ""] + feat_lines + ["", "**适用场景**", ""] + scene_lines + ["", "**常见问题**", ""] + qa + ["", "---", ""]))

    blocks.append("\n".join([
        "## 2. 小红书（短笔记，痛点开头 + emoji + 标签）", "",
        "### 标题", "😭终于把重要日子都记明白了｜鸿蒙党狂喜", "",
        "### 正文", "",
        "以前重要日子全靠脑记，结果总在最后一刻才想起来…",
        "",
        "直到用了 %s 👇" % name,
        "",
        "🧩 服务卡片直接放桌面，还剩多少天抬眼就见",
        "🔔 提前 30 天就开始提醒，不慌",
        "🎨 主题随便换，记录也要好看",
        "🔄 倒数和正数都能记，纪念日超合适",
        "",
        "鸿蒙用户真的可以试试～",
        "",
        "### 标签", "#鸿蒙 #HarmonyOS #时间管理 #效率工具 #纪念日 #桌面小组件", "", "---", ""]))

    blocks.append("\n".join([
        "## 3. 今日头条（资讯式，分段短句）", "",
        "### 标题", "%s 上线：把重要日子放进鸿蒙服务卡片" % name, "",
        "### 正文", "",
        desc, "",
        "据介绍，%s 覆盖了考试、纪念日、职场节点、宝宝成长等常见场景，并提供多级智能提醒。" % name,
        "",
        "与传统记录类应用不同，它把最近的事件直接呈现在鸿蒙服务卡片与负一屏上，用户无需打开应用即可查看剩余天数。", "",
        "目前该应用已在华为应用市场提供下载。", "", "---", ""]))

    blocks.append("\n".join([
        "## 4. 百家号（偏科普，先说概念再说产品）", "",
        "### 标题", "什么是事件记录？鸿蒙应用 %s 给出了一个答案" % name, "",
        "### 正文", "",
        "「事件记录」指的是把生活中需要被记住的时间节点集中管理，并在合适的时间提醒你。", "",
        "这类工具的价值在于两点：一是降低记录成本，二是提高提醒到达率。", "",
        "%s 的做法是把事件放到鸿蒙服务卡片上，用系统级入口解决「看不着」的问题。" % name, "",
        "**核心能力**", ""] + feat_lines + ["", "---", ""]))

    blocks.append("\n".join([
        "## 5. 华为开发者社区（技术视角，强调鸿蒙原生）", "",
        "### 标题", "%s 的技术实践：基于 HarmonyOS 原生的事件提醒应用" % name, "",
        "### 正文", "",
        "**背景**：事件记录类应用的核心体验瓶颈在于「触达」，而非「存储」。", "",
        "**方案**：%s 基于 HarmonyOS 原生开发，使用服务卡片把最近事件暴露到桌面与负一屏；提醒链路走系统级通知，保证到达率。" % name, "",
        "**功能构成**", ""] + feat_lines + ["",
        "**适配说明**", "",
        "- 系统：%s" % cfg.get("os_list", cfg.get("platform", "")),
        "- 生态：%s" % ("、".join(kw(cfg, "harmony")) or "鸿蒙原生"), "", "---", ""]))

    blocks.append("\n".join([
        "## 6. CSDN（开发者视角，问题—方案—结论）", "",
        "### 标题", "鸿蒙应用 %s 开发要点与上架记录" % name, "",
        "### 正文", "",
        "1. **要解决的问题**：重要日子的提醒触达率低。",
        "2. **技术选型**：HarmonyOS 原生 + 服务卡片 + 系统通知。",
        "3. **上架流程**：AppGallery Connect 配置 → 资质材料 → 提交审核。",
        "4. **优化重点**：标题与描述的关键词布局直接影响搜索曝光。", "",
        "**对比同类方案**", ""] + ["- 与 %s 相比：%s" % (c, tagline) for c in comp] + ["", "---", ""]))

    blocks.append("\n".join([
        "## 通投内容规范（所有平台通用）", "",
        "- 结论前置：第一段必须出现产品名 + 一句话定位",
        "- 分层小标题：用 H2/H3 或加粗小标题切分",
        "- 数据/对比：尽量给表格或列表，便于 AI 抽取",
        "- 来源标注：引用数据须注明来源",
        "- 结尾 FAQ：至少 3 条常见问答",
        "- 品牌统一：全平台使用同一产品名、同一 Slogan、同一官网链接", ""]))
    return "\n".join(blocks)


# ---------------------------------------------------------------- 分发排期
def build_distribution(cfg):
    name = cfg.get("name", "")
    plats = cfg.get("dist_platforms", [])
    L = ["# 48 小时分发排期表 · %s" % name, "",
         "> 黄金窗口节奏：官网首发 → 24h 生态/资讯 → 48h 知识社区与长尾全覆盖。", "",
         "| 时间 | 平台 | 内容 | 动作 | 完成 |", "|---|---|---|---|:--:|"]
    n = len(plats)
    for i, p in enumerate(plats):
        if i == 0:
            t, c, a = "T+0", "%s（首发）" % p, "发布落地页与产品公告，提交搜索引擎收录"
        elif i <= max(1, n // 2):
            t, c, a = "T+24h", p, "发布适配文案，@相关话题，挂官网链接"
        else:
            t, c, a = "T+48h", p, "发布长尾/问答内容，评论区引导，收集提问"
        L.append("| %s | %s | %s 相关文案 | %s | ☐ |" % (t, p, name, a))
    L += ["", "## 72 小时互动动作", "",
          "- T+72h：回复所有评论，把高频问题沉淀成新的 FAQ",
          "- 记录每个平台的首日曝光与站外引流数",
          "- 把用户原话摘出来，作为下一轮内容的素材（EEAT 的「经验」维度）", "",
          "## 分发记录字段", "",
          "平台 / 发布时间 / 标题 / 链接 / 首日曝光 / 站外引流 / 评论数 / 备注", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- 人工清单
def build_checklist(cfg):
    name = cfg.get("name", "")
    L = ["# 人工必做清单 · %s" % name, "",
         "> 以下事项流水线无法代办，需要你本人完成（多数涉及主体资质与线下审核）。", "",
         "## 上架前", "",
         "| # | 事项 | 说明 | 状态 |", "|---:|---|---|:--:|",
         "| 1 | 主体资质 | 企业/个人开发者实名认证，需营业执照或身份证 | ☐ |",
         "| 2 | 软件著作权 | 国内商店上架通常需要软著证书（办理周期较长，建议提前） | ☐ |",
         "| 3 | ICP 备案 | 官网域名需完成 ICP 备案才能在国内正常访问 | ☐ |",
         "| 4 | 隐私政策 | 应用内与官网均需提供合规隐私政策，说明数据收集范围 | ☐ |",
         "| 5 | 应用图标 / 截图 / 视频 | 视觉素材必须真人产出，建议 A/B 测试 | ☐ |",
         "| 6 | 应用签名与包体 | 鸿蒙应用需完成签名与包体自测 | ☐ |", "",
         "## 上架与审核", "",
         "| # | 事项 | 说明 | 状态 |", "|---:|---|---|:--:|",
         "| 7 | 应用商店上架提交 | AppGallery Connect 提交审核（审核时长以官方为准） | ☐ |",
         "| 8 | 元数据回填 | 把 aso.md 中的标题/简介/关键词/描述填入商店后台 | ☐ |",
         "| 9 | 审核被打回处理 | 按审核意见修改并重新提交 | ☐ |",
         "| 10 | 版本更新维护 | 后续每次发版同步更新元数据与截图 | ☐ |", "",
         "## 上线后 · 必须真人执行", "",
         "| # | 事项 | 说明 | 状态 |", "|---:|---|---|:--:|",
         "| 11 | 真实用户好评引导 | 应用内引导真实评价（**不得**以利益换取指定星级） | ☐ |",
         "| 12 | 差评回复 | 真人回复差评，态度诚恳并给出解决路径 | ☐ |",
         "| 13 | 评论区运营 | 在知乎/小红书等平台真人互动，回复提问 | ☐ |",
         "| 14 | 媒体与投放 | 联系科技媒体、付费投放（如鲸鸿动能）需人工决策与预算 | ☐ |",
         "| 15 | 编辑推荐申报 | 向应用市场申报「编辑推荐 / 策展空间」 | ☐ |", "",
         "> 提示：合规红线——不得机刷、买量、以红包/权益换取指定星级好评。", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- 报告
def build_report(cfg, files, warnings):
    name = cfg.get("name", "")
    L = ["# 流水线执行报告 · %s" % name, "",
         "- 执行时间：%s" % TODAY,
         "- 产品配置：`pipeline/product.example.json`（或你指定的配置）",
         "- 输出目录：`pipeline/out/%s/`" % slugify(cfg), "",
         "## 已自动生成的产物", "",
         "| 文件 | 内容 | 对应原项目环节 |", "|---|---|---|"]
    mapping = {
        "index.html": ("产品落地页（含 2 类 JSON-LD 结构化数据）", "03 官网 Schema / 修改网页产品介绍"),
        "content.md": ("多平台文案包（6 个平台口吻）", "12 内容包 / 语义内容"),
        "aso.md": ("各应用商店 ASO 元数据 + 字符数校验", "07 ASO 优化"),
        "keywords.md": ("四维关键词矩阵 + 优先级分层", "02 关键词矩阵"),
        "monitor.md": ("AI 搜索监测问句 + 抓取偏好", "08 监测问句清单"),
        "distribution.md": ("48 小时分发排期 + 72h 互动动作", "05-06 分发执行"),
        "checklist.md": ("人工必做清单（备案/软著/上架/资质）", "需人工完成的部分"),
    }
    for f in files:
        d = mapping.get(f, ("—", "—"))
        L.append("| `%s` | %s | %s |" % (f, d[0], d[1]))
    L += ["", "## 自动校验结果", ""]
    L += warnings if warnings else ["- 全部通过 ✅"]
    L += ["", "## 自动化边界", "",
          "**流水线自动完成**：文案生成、落地页生成、ASO 元数据与字符数校验、关键词矩阵、监测问句、分发排期表。", "",
          "**必须人工完成**：主体资质、软件著作权、ICP 备案、隐私政策、图标/截图/视频素材、应用商店上架提交与审核、真人好评与评论运营、媒体投放决策。详见 `checklist.md`。", "",
          "## 下一步", "",
          "1. 打开 `index.html` 检查落地页文案，替换 `XXXXXXX` 占位下载链接",
          "2. 按 `checklist.md` 准备资质材料并提交上架",
          "3. 上架后按 `aso.md` 回填商店元数据",
          "4. 按 `distribution.md` 执行分发，按 `monitor.md` 每周监测", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- 主流程
def main():
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "product.example.json")
    if not os.path.isabs(cfg_path):
        cfg_path = os.path.join(HERE, cfg_path)
    if not os.path.exists(cfg_path):
        print("找不到配置文件：%s" % cfg_path)
        return 1
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    out = os.path.join(OUT_ROOT, slugify(cfg))
    os.makedirs(out, exist_ok=True)

    warnings = []
    if not cfg.get("name"):
        warnings.append("- ❌ 缺少 `name`：落地页与文案将不完整")
    if len(cfg.get("features", [])) < 3:
        warnings.append("- ⚠️ `features` 少于 3 条，落地页会显得单薄")
    if len(cfg.get("faq", [])) < 5:
        warnings.append("- ⚠️ `faq` 少于 5 条，结构化数据 FAQPage 建议 ≥5 条")

    arts = {
        "index.html": build_landing(cfg),
        "content.md": build_content(cfg),
        "aso.md": build_aso(cfg),
        "keywords.md": build_keywords(cfg),
        "monitor.md": build_monitor(cfg),
        "distribution.md": build_distribution(cfg),
        "checklist.md": build_checklist(cfg),
    }
    files = []
    for fn, body in arts.items():
        with open(os.path.join(out, fn), "w", encoding="utf-8") as f:
            f.write(body)
        files.append(fn)
        print("  生成 %-18s %6d 字符" % (fn, len(body)))

    with open(os.path.join(out, "REPORT.md"), "w", encoding="utf-8") as f:
        f.write(build_report(cfg, files, warnings))
    print("  生成 %-18s" % "REPORT.md")

    print("\n✅ 流水线完成：%s" % out)
    print("   共 %d 个文件。人工必做事项见 checklist.md" % (len(files) + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
