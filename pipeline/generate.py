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
def shade(hex_color, factor):
    h = str(hex_color).lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    if factor >= 0:
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
    else:
        k = 1 + factor
        r, g, b = int(r * k), int(g * k), int(b * k)
    return '#%02x%02x%02x' % (r, g, b)


LANDING_CSS = """:root{
  --accent:#4f46e5;
  --accent-2:#7c3aed;
  --accent-soft:#eef2ff;
  --ink:#161b26;
  --muted:#6b7280;
  --line:#e8eaf2;
  --alt:#f7f8fc;
  --radius:20px;
  --maxw:1160px;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;line-height:1.65;color:var(--ink);background:#fff;-webkit-font-smoothing:antialiased}
a{text-decoration:none;color:inherit}
.container{max-width:var(--maxw);margin:0 auto;padding:0 24px}

/* 顶部导航 */
.nav{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.82);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.nav-inner{display:flex;align-items:center;justify-content:space-between;height:64px}
.brand{font-weight:800;font-size:19px;letter-spacing:.5px;display:flex;align-items:center;gap:8px}
.brand .dot{width:11px;height:11px;border-radius:3px;background:linear-gradient(135deg,var(--accent),var(--accent-2))}
.nav-cta{background:linear-gradient(135deg,var(--accent),var(--accent-2));color:#fff;padding:9px 18px;border-radius:999px;font-weight:600;font-size:14px;transition:.25s}
.nav-cta:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(79,70,229,.28)}

/* 主视觉 */
.hero{position:relative;overflow:hidden;background:linear-gradient(135deg,var(--accent) 0%,var(--accent-2) 100%);color:#fff;padding:96px 0 104px;text-align:center}
.hero-glow{position:absolute;width:640px;height:640px;background:radial-gradient(circle,rgba(255,255,255,.30),transparent 60%);top:-240px;left:50%;transform:translateX(-50%);pointer-events:none}
.hero-inner{position:relative}
.badge{display:inline-block;padding:6px 16px;border:1px solid rgba(255,255,255,.5);border-radius:999px;font-size:13px;letter-spacing:1px;margin-bottom:22px;opacity:.95}
.hero h1{font-size:56px;font-weight:800;letter-spacing:1px;margin-bottom:14px}
.hero-tag{font-size:22px;font-weight:500;opacity:.96;margin-bottom:20px}
.hero-desc{font-size:17px;max-width:720px;margin:0 auto 36px;opacity:.92;line-height:1.85}
.hero-cta{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.btn-primary,.btn-secondary{display:inline-flex;align-items:center;gap:9px;padding:14px 32px;border-radius:999px;font-size:16px;font-weight:600;transition:.25s}
.btn-primary{background:#fff;color:var(--accent-2)}
.btn-primary:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(0,0,0,.2)}
.btn-secondary{background:rgba(255,255,255,.16);color:#fff;border:1.5px solid rgba(255,255,255,.55)}
.btn-secondary:hover{background:rgba(255,255,255,.28);transform:translateY(-3px)}
.hero-trust{margin-top:28px;font-size:14px;opacity:.85}

/* 区块通用 */
.section{padding:88px 0}
.section-alt{background:var(--alt)}
.section-title{text-align:center;font-size:34px;font-weight:800;margin-bottom:12px;letter-spacing:.5px}
.section-subtitle{text-align:center;font-size:16px;color:var(--muted);margin:0 auto 52px;max-width:660px;line-height:1.7}

/* 痛点 -> 解法 */
.pain{background:linear-gradient(180deg,#fbfcff,#fff);padding:80px 0;border-top:1px solid var(--line)}
.pain-grid{display:grid;grid-template-columns:1fr 1fr;gap:32px;max-width:980px;margin:0 auto}
.pain-col{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:34px 30px;box-shadow:0 10px 30px rgba(22,27,38,.05)}
.eyebrow{display:inline-block;font-size:13px;font-weight:700;letter-spacing:1px;padding:4px 12px;border-radius:999px;margin-bottom:16px}
.pain-col .eyebrow{background:#fff0f0;color:#e0483b}
.pain-solve .eyebrow{background:var(--accent-soft);color:var(--accent-2)}
.pain-text{font-size:17px;line-height:1.8;color:#374151}
.pain-list{list-style:none;margin-top:16px}
.pain-list li{position:relative;padding-left:24px;margin-bottom:11px;font-size:15px;color:#374151;line-height:1.6}
.pain-list li::before{content:"✓";position:absolute;left:0;color:var(--accent-2);font-weight:800}

/* 数据条 */
.stats{background:linear-gradient(135deg,var(--accent),var(--accent-2));color:#fff}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;text-align:center;padding:54px 0}
.stats strong{display:block;font-size:38px;font-weight:800;line-height:1.1}
.stats span{font-size:14px;opacity:.9;letter-spacing:1px}

/* 核心功能 */
.features-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px}
.feature-card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:32px 26px;transition:.25s}
.feature-card:hover{transform:translateY(-6px);box-shadow:0 16px 40px rgba(22,27,38,.08);border-color:transparent}
.feature-icon{width:58px;height:58px;display:flex;align-items:center;justify-content:center;font-size:30px;background:var(--accent-soft);border-radius:14px;margin-bottom:18px}
.feature-card h3{font-size:19px;font-weight:700;margin-bottom:10px}
.feature-card p{font-size:15px;color:var(--muted);line-height:1.75}

/* 适用场景 */
.scenes-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px}
.scene-card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:34px 24px;text-align:center;transition:.25s}
.scene-card:hover{transform:translateY(-6px);box-shadow:0 14px 34px rgba(22,27,38,.07);border-color:var(--accent)}
.scene-emoji{font-size:46px;margin-bottom:14px}
.scene-card h3{font-size:19px;font-weight:700;margin-bottom:8px}
.scene-card p{font-size:14px;color:var(--muted);line-height:1.7}

/* 下载 / CTA */
.download-section{background:linear-gradient(135deg,var(--accent-2),var(--accent));color:#fff;text-align:center;padding:92px 0}
.download-section h2{font-size:38px;font-weight:800;margin-bottom:12px}
.download-section .tagline{font-size:18px;opacity:.95;margin-bottom:40px;letter-spacing:1px}
.download-buttons{display:flex;gap:20px;justify-content:center;flex-wrap:wrap}
.download-btn{display:inline-flex;align-items:center;gap:12px;padding:16px 34px;border-radius:14px;font-size:16px;font-weight:600;background:#fff;color:var(--ink);transition:.25s;box-shadow:0 10px 30px rgba(0,0,0,.18)}
.download-btn:hover{transform:translateY(-4px)}
.download-btn .icon{font-size:26px}
.download-btn .text small{display:block;font-size:12px;color:#8b90a0;font-weight:400}

/* FAQ */
.faq-wrapper{max-width:840px;margin:0 auto}
.faq-item{background:#fff;border:1px solid var(--line);border-radius:14px;margin-bottom:14px;overflow:hidden;transition:.25s}
.faq-item:hover{border-color:var(--accent)}
.faq-question{padding:20px 24px;font-size:16px;font-weight:600;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:16px}
.faq-question::after{content:"+";font-size:22px;color:var(--accent-2);transition:transform .3s}
.faq-item.open .faq-question::after{transform:rotate(45deg)}
.faq-answer{max-height:0;overflow:hidden;transition:max-height .35s ease,padding .35s ease;font-size:15px;color:var(--muted);line-height:1.8;padding:0 24px}
.faq-item.open .faq-answer{padding:0 24px 22px;max-height:600px}

/* 页脚 */
footer{background:#0f1220;color:#aeb3c2;padding:52px 0 34px;text-align:center}
.footer-brand{font-size:20px;font-weight:800;color:#fff;margin-bottom:8px}
.footer-slogan{font-size:14px;margin-bottom:18px;letter-spacing:1px;opacity:.8}
.copyright{font-size:13px;opacity:.6;border-top:1px solid #232838;padding-top:18px;margin-top:18px}

@media(max-width:768px){
  .hero{padding:66px 0 78px}.hero h1{font-size:34px}.hero-tag{font-size:18px}.section{padding:56px 0}
  .section-title{font-size:26px}.pain-grid{grid-template-columns:1fr}.stats-grid{grid-template-columns:repeat(2,1fr);gap:18px}
  .features-grid,.scenes-grid{grid-template-columns:1fr}.download-section h2{font-size:28px}
}
"""


def build_landing(cfg):
    name = esc(cfg.get("name", "产品"))
    desc = esc(cfg.get("description", ""))
    tagline = esc(cfg.get("tagline", ""))
    slogan = esc(cfg.get("slogan", ""))
    category = esc(cfg.get("category", "应用"))
    positioning = cfg.get("positioning", "")
    pain_point = cfg.get("pain_point", "")
    os_list = esc(cfg.get("os_list", cfg.get("platform", "")))
    website = esc(cfg.get("website", ""))
    year = esc(cfg.get("copyright_year", ""))
    team = esc(cfg.get("team", ""))
    email = esc(cfg.get("contact_email", ""))
    rating = esc(cfg.get("rating_value", "—"))
    rating_count = esc(cfg.get("rating_count", "0"))

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
        '        <span style="font-size:20px;">%s</span>\n'
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
    n_features = len(cfg.get("features", []))
    n_scenarios = len(cfg.get("scenarios", []))

    # 主题色（可选 accent），注入 CSS 变量
    accent = str(cfg.get("accent", "")).strip()
    if accent:
        theme_style = ('<style>:root{--accent:%s;--accent-2:%s;--accent-soft:%s}</style>'
                       % (accent, shade(accent, -0.18), shade(accent, 0.88)))
    else:
        theme_style = ""

    # 痛点 -> 解法
    pain_solve = esc(positioning) or desc
    pain_list = "\n".join(
        '          <li><b>%s</b> — %s</li>' % (esc(f.get("title", "")), esc(f.get("desc", "")))
        for f in cfg.get("features", [])[:3]
    )
    nav = chans[0] if chans else {"url": "#", "store": "下载"}
    nav_url = esc(nav.get("url", "#"))
    nav_store = esc(nav.get("store", "下载"))

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

    tpl = '''<!DOCTYPE html>
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
<style>__CSS__</style>
%(theme_style)s
<script type="application/ld+json">
%(app_ld)s
</script>
<script type="application/ld+json">
%(faq_ld)s
</script>
</head>
<body>
<header class="nav">
  <div class="container nav-inner">
    <div class="brand"><span class="dot"></span>%(name)s</div>
    <a class="nav-cta" href="%(nav_url)s" target="_blank" rel="noopener">%(nav_store)s ↗</a>
  </div>
</header>

<section class="hero">
  <div class="hero-glow"></div>
  <div class="container hero-inner">
    <span class="badge">%(category)s</span>
    <h1>%(name)s</h1>
    <p class="hero-tag">%(tagline)s</p>
    <p class="hero-desc">%(desc)s</p>
    <div class="hero-cta">
%(hero_btns)s
    </div>
    <p class="hero-trust">已支持 %(os_list)s · 评分 %(rating)s ★（%(rating_count)s 条评价）</p>
  </div>
</section>

<section class="pain">
  <div class="container">
    <h2 class="section-title">你是否在为这件事发愁？</h2>
    <p class="section-subtitle">%(name)s的存在，正是为了把这件难事变简单。</p>
    <div class="pain-grid">
      <div class="pain-col">
        <span class="eyebrow">痛点</span>
        <p class="pain-text">%(pain_point)s</p>
      </div>
      <div class="pain-col pain-solve">
        <span class="eyebrow">解法</span>
        <p class="pain-text">%(pain_solve)s</p>
        <ul class="pain-list">
%(pain_list)s
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="stats">
  <div class="container stats-grid">
    <div><strong>%(rating)s</strong><span>用户评分</span></div>
    <div><strong>%(rating_count)s+</strong><span>真实评价</span></div>
    <div><strong>%(n_features)s</strong><span>核心能力</span></div>
    <div><strong>%(n_scenarios)s</strong><span>适用场景</span></div>
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
    <p class="section-subtitle">%(name)s，在真实使用场景中为你所用</p>
    <div class="scenes-grid">
%(scenes)s
    </div>
  </div>
</section>

<section class="download-section">
  <div class="container">
    <h2>立即开始使用 %(name)s</h2>
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
'''
    kws = esc(",".join(kw(cfg, "brand") + kw(cfg, "core") + kw(cfg, "scene")))
    html = tpl % {
        "name": name, "tagline": tagline, "desc": desc, "website": website,
        "theme_style": theme_style, "category": category, "os_list": os_list,
        "rating": rating, "rating_count": rating_count, "pain_point": esc(pain_point),
        "pain_solve": pain_solve, "pain_list": pain_list,
        "n_features": n_features, "n_scenarios": n_scenarios, "feat_titles": esc(feat_titles),
        "feats": feats, "scenes": scenes, "dl_btns": dl_btns, "faq_html": faq_html,
        "hero_btns": hero_btns, "slogan": slogan, "year": year, "team": team,
        "email": email, "kws": kws,
        "app_ld": json.dumps(app_ld, ensure_ascii=False, indent=2),
        "faq_ld": json.dumps(faq_ld, ensure_ascii=False, indent=2),
        "nav_url": nav_url, "nav_store": nav_store,
    }
    html = html.replace("__CSS__", LANDING_CSS)
    return html




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
        name, tagline, cfg.get("positioning", "产品"),
        "、".join(core) or "多项核心能力",
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
    positioning = cfg.get("positioning", "产品")
    category = cfg.get("category", positioning)
    pain = cfg.get("pain_point", "")
    feat_lines = ["- %s：%s" % (f.get("title", ""), f.get("desc", "")) for f in feats]
    scene_lines = ["- %s：%s" % (s.get("title", ""), s.get("desc", "")) for s in scenes]
    qa = ["**%s**\n%s" % (q.get("q", ""), q.get("a", "")) for q in faq]
    feat_bullets = "\n".join("%s %s：%s" % (f.get("icon", "🔹"), f.get("title", ""), f.get("desc", "")) for f in feats) or "🔹 核心能力突出，直击用户真实痛点"
    comp_lines = ["- 与 %s 相比：%s" % (x, tagline) for x in comp] if comp else \
        ["- 与同类方案相比：%s 在%s上更具优势" % (name, "、".join(f.get("title", "") for f in feats[:2]) or "核心体验")]
    scene_titles = [s.get("title", "") for s in scenes]
    os_info = cfg.get("os_list", cfg.get("platform", ""))
    harmony_kw = kw(cfg, "harmony")

    if harmony_kw or ("鸿蒙" in str(os_info) or "HarmonyOS" in str(os_info)):
        tech_angle = "%s 基于 HarmonyOS 原生开发，结合%s，把核心能力暴露到系统级入口。" % (
            name, "、".join(harmony_kw) or "服务卡片")
    else:
        tech_angle = "%s 以%s为运行环境，重点打磨核心链路与稳定性。" % (name, os_info or "目标平台")

    blocks = []
    # 1 知乎
    blocks.append("\n".join([
        "# 多平台文案包 · %s" % name, "",
        "> 生成时间：%s ｜ 已按平台调性分开写，可直接复制粘贴。" % TODAY, "",
        "---", "", "## 1. 知乎（问答式长文，结论前置 + 分层标题）", "",
        "### 标题", "%s 值得用吗？真实体验与方案实测" % name, "",
        "### 正文", "", "**结论前置**：%s。%s" % (tagline or desc, desc), "",
        "**它解决了什么问题**", "",
        (pain or "在%s这件事上，用户往往面临「想用却用不顺手」的困境，%s 的思路值得一看。" % (category, name)), "",
        "**核心功能**", ""] + feat_lines + ["", "**适用场景**", ""] + scene_lines + ["", "**常见问题**", ""] + qa + ["", "---", ""]))

    # 2 小红书
    blocks.append("\n".join([
        "## 2. 小红书（短笔记，痛点开头 + emoji + 标签）", "",
        "### 标题", "😭终于把这件事搞定了｜%s 真香" % name, "",
        "### 正文", "",
        (pain or "以前%s相关的需求总被将就，结果总差一口气…" % category),
        "", "直到用了 %s 👇" % name, "", feat_bullets, "",
        "%s，真的可以试试～" % (tagline or "好东西值得被看见"), "",
        "### 标签", "#%s #好物分享 #效率提升 #种草 #实用工具" % name, "", "---", ""]))

    # 3 头条
    blocks.append("\n".join([
        "## 3. 今日头条（资讯式，分段短句）", "",
        "### 标题", "%s 上线：%s" % (name, tagline or "一款值得关注的新品"), "",
        "### 正文", "", desc, "",
        "据介绍，%s 覆盖了%s等常见场景，并提供贴合需求的解决方案。" % (name, "、".join(scene_titles[:3]) or category), "",
        "与传统同类方案不同，%s 在%s上形成了自己的差异化。" % (name, "、".join(f.get("title", "") for f in feats[:2]) or "核心体验"), "",
        "目前该%s已在对应渠道提供。" % positioning, "", "---", ""]))

    # 4 百家号
    blocks.append("\n".join([
        "## 4. 百家号（偏科普，先说概念再说产品）", "",
        "### 标题", "什么是%s？%s 给出了一个答案" % (category, name), "",
        "### 正文", "",
        "「%s」指的是围绕%s形成的一类专业解决方案。" % (category, category), "",
        "这类方案的价值在于两点：一是降低使用门槛，二是提升实际效果。", "",
        "%s 的做法是%s。" % (name, (pain or "把%s的关键环节做到极致" % category)), "",
        "**核心能力**", ""] + feat_lines + ["", "---", ""]))

    # 5 华为开发者社区
    blocks.append("\n".join([
        "## 5. 华为开发者社区（技术视角，强调生态适配）", "",
        "### 标题", "%s 的技术实践：面向鸿蒙生态的%s" % (name, positioning), "",
        "### 正文", "",
        "**背景**：%s 的核心体验瓶颈在于「触达」与「留存」，而非功能堆砌。" % name, "",
        "**方案**：%s" % tech_angle, "",
        "**功能构成**", ""] + feat_lines + ["", "**适配说明**", "",
        "- 系统：%s" % os_info, "- 生态：%s" % ("、".join(harmony_kw) or "通用生态"), "", "---", ""]))

    # 6 CSDN
    blocks.append("\n".join([
        "## 6. CSDN（开发者视角，问题—方案—结论）", "",
        "### 标题", "%s 开发要点与上架记录" % name, "",
        "### 正文", "",
        "1. **要解决的问题**：%s" % (pain or "%s 在%s场景下体验不佳" % (category, category)),
        "2. **技术选型**：%s" % (os_info or "主流技术栈"),
        "3. **上架流程**：对应应用市场配置 → 资质材料 → 提交审核。",
        "4. **优化重点**：标题与描述的关键词布局直接影响搜索曝光。", "",
        "**对比同类方案**", ""] + comp_lines + ["", "---", ""]))

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
