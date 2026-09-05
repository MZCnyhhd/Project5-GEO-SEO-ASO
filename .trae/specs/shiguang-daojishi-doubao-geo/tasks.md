# 闪光倒计时 · 豆包GEO推广落地 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 确认App核心信息并产出《全平台信源规范手册》
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 基于用户回答 Open Questions，确认闪光倒计时的：App全称、一句话描述、核心功能（至少5点）、品牌Slogan、开发者/公司全称、各应用商店官方下载链接
  - 将以上 6 项核心信息整理为不可变的《信源规范手册》Markdown 文档，包含每项的标准文本和使用规则
  - 生成一份核查清单，供后续全平台一致性检查使用
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 核查手册中 6 项核心信息均已填写且无空值
  - `programmatic` TR-1.2: 手册文件保存至项目目录，文件名规范，可随时查阅
  - `human-judgement` TR-1.3: 核查清单覆盖所有计划中的平台类型，每类平台有明确的核查项和预期值
- **Notes**: 此任务是后续所有平台账号搭建和内容发布的前提，若 App 核心信息未确认，需先向用户澄清再推进

---

## [x] Task 2: 构建四维关键词矩阵（≥50条）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于《闪光倒计时-豆包推广方案.md》中第四章的分类框架，产出：疑问类≥9条、对比类≥4条、场景类≥25条（按考试/情感/职场/生活四子类拆分）、避坑类≥4条
  - 每条关键词标注：优先级（P0/P1/P2）、预估搜索意图强度（1-5星）、对应内容形式（横评/评测/场景指南/问答/清单）、首发建议平台
  - 额外产出 P0 关键词的「豆包真实问句模拟」列表，即用户在豆包中可能使用的口语化完整提问（不少于20条）
  - 以结构化表格（Markdown 或 CSV）形式交付
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 统计矩阵总条目数，要求 ≥50 条，且四类词都满足最低数量要求
  - `programmatic` TR-2.2: 每条关键词均已标注优先级、意图强度、内容形式、首发平台四项元数据
  - `programmatic` TR-2.3: P0 口语化问句清单条目数 ≥20
  - `human-judgement` TR-2.4: 抽查 10 条关键词与闪光倒计时实际功能的匹配度，错位率应 ≤10%（即不超过1条明显不相关）
- **Notes**: 场景类关键词要覆盖学生党、职场人、情侣、宝妈四类核心人群

---

## [x] Task 3: 搭建品牌官网/落地页并嵌入 Schema 结构化标记
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 若已有官网：在官网产品页首页嵌入 Schema 标记
  - 若无官网：搭建简易静态落地页（可使用 GitHub Pages / Vercel / Netlify 免费托管或极简 Wordpress 模板），落地页包含：首屏Banner介绍、核心功能分点、使用场景展示、下载按钮、FAQ板块
  - 嵌入两类 JSON-LD Schema 标记：① MobileApplication：包含 name、applicationCategory（UtilitiesApplication）、operatingSystem（iOS, Android）、offers（免费）、aggregateRating（基于实际评分填写）、description（与信源规范一致）；② FAQPage：至少包含 5 条关于闪光倒计时的常见问题与标准回答
  - 部署上线后使用 Schema 校验工具（Google Rich Results Test 或 schema.org 校验器）检测无错误
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 访问落地页/官网实际地址可正常打开，无 404/500 错误
  - `programmatic` TR-3.2: 查看页面源代码可找到 `<script type="application/ld+json">` 包含 MobileApplication 类型对象，字段齐全
  - `programmatic` TR-3.3: 源代码中同样存在 FAQPage 类型对象，且 mainEntity 数组长度 ≥5
  - `programmatic` TR-3.4: 使用 Schema.org Validator 或等价工具校验，无 error 级报错
  - `human-judgement` TR-3.5: 落地页内容与《信源规范手册》100%一致，视觉整洁、布局清晰、下载按钮醒目
- **Notes**: 若技术资源紧张，优先选择零代码方案（如使用 Notion 发布公开页 + Cloudflare Workers 代理，或 Carrd/上线了 等工具），Schema 标记可通过页面嵌入 HTML 代码块实现

---

## [x] Task 4: 注册并完善 6 个核心平台官方账号（交付操作手册+登记表模板，实际注册为用户后置动作）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 注册并完成以下 6 个平台官方账号搭建：① 抖音企业号（建议蓝V认证）、② 今日头条企业头条号、③ 知乎机构号、④ 小红书官方企业号、⑤ 西瓜视频官方号（可与抖音企业号打通）、⑥ 百度百家号企业号
  - 每个账号必须完成：头像上传（统一品牌 Logo）、昵称（含「闪光倒计时」品牌词）、简介填写（严格使用《信源规范手册》标准描述）、背景图/头图设置（含App名称与下载引导）、跳转链接配置（跳转官网或下载页）
  - 汇总交付一份《账号矩阵登记表》，包含平台名、账号主页URL、登录账号/密码、运营负责人、创建日期
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: 对照登记表逐一访问 6 个账号主页 URL，全部可正常打开且不显示「账号不存在/封禁」
  - `programmatic` TR-4.2: 每个账号的简介文本与《信源规范手册》标准描述做文本比对，完全一致（不允许错别字或改写）
  - `human-judgement` TR-4.3: 抽查 3 个账号的头像、背景图、昵称视觉是否符合品牌调性且包含 App 名称标识
  - `human-judgement` TR-4.4: 每个账号均已发布至少 1 条测试内容（如App简介）以证明发布功能正常
- **Notes**: 抖音企业号蓝V认证需营业执照；知乎机构号可能需对公验证，提前准备好资质材料

---

## [x] Task 5: 产出并发布 P0 级基石内容（3篇）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 产出 3 篇 P0 级基石内容，每篇 1500-3000 字：
    - C001《2026年十大时间管理工具推荐：闪光倒计时凭什么入选？》
    - C002《倒计时APP深度横评：闪光倒计时 vs Days Matter vs 倒数日》（含对比表格）
    - C003《闪光倒计时产品白皮书：让每一个重要日子都有闪光时刻》（PDF + 网页双版本）
  - 每篇内容严格通过 AI 友好格式 5 项审核（见 AC-4）
  - 以官网为首发信源，先发布至官网产品博客或新闻板块
- **Acceptance Criteria Addressed**: AC-4 (部分), AC-6 (前置条件)
- **Test Requirements**:
  - `programmatic` TR-5.1: 3 篇内容字数均达标（C001/C002 ≥1500字，C003白皮书 ≥2500字）
  - `human-judgement` TR-5.2: 按 AI 友好格式 5 项逐项审核每篇内容：① 结论前置点名闪光倒计时 ✅ ② H2/H3 分层 ✅ ③ 含表格/清单 ✅ ④ 数据有出处 ✅ ⑤ FAQ 模块 5+ 条 ✅
  - `programmatic` TR-5.3: 3 篇内容均可在官网对应 URL 访问到，无加密或权限限制
  - `human-judgement` TR-5.4: C002 的对比表格维度不少于 6 个（功能完整性、视觉设计、广告情况、跨平台、数据同步、价格），闪光倒计时在差异化维度明确胜出
- **Notes**: C003 白皮书若资源允许可设计为可下载 PDF，并在官网提供下载入口，白皮书本身也是一级高权重信源

---

## [x] Task 6: 执行 48 小时黄金窗口分发（交付分发手册+适配文案+记录表模板）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 按照「Day1 10:00 官网首发 → Day1 15:00 字节生态（抖音/头条/西瓜）同步 → Day2 09:00 知乎/小红书 → Day2 18:00 百家号/搜狐号/简书/豆瓣等长尾平台」的节奏，对 C001、C002、C003 三篇内容逐一进行全平台分发
  - 每篇内容按不同平台特性做轻度适配（如小红书配精美截图+短文案，抖音剪为15秒功能演示视频并挂载链接，知乎用问答形式包装）
  - 汇总每篇内容的各平台发布 URL 形成《发布记录表》，记录发布时间以验证是否符合 24h / 48h 时间窗口
- **Acceptance Criteria Addressed**: AC-6, AC-4 (分发完成)
- **Test Requirements**:
  - `programmatic` TR-6.1: 每篇内容覆盖平台数量 ≥8 个，三篇总计发布条目数 ≥24
  - `programmatic` TR-6.2: 每篇内容的字节生态（抖音/头条/西瓜）发布时间 - 官网首发时间 ≤24 小时；长尾平台发布时间 - 官网首发时间 ≤48 小时
  - `human-judgement` TR-6.3: 抽查 6 条平台适配内容（每个平台 1 条），确认内容未出现与《信源规范手册》不一致的表述，且适配后未丢失闪光倒计时的核心推荐结论
  - `programmatic` TR-6.4: 《发布记录表》中 100% 的 URL 可正常打开访问
- **Notes**: 字节生态内容建议额外挂适量信息流小额投放（单篇100-300元），提升初始互动量，抓取权重会更高

---

## [x] Task 7: 产出并发布 P1 级场景内容（交付5篇Markdown+3平台适配包）
- **Priority**: medium
- **Depends On**: Task 2, Task 4
- **Description**:
  - 产出并跨平台发布 5 篇 P1 级场景内容：
    - C101 高考倒计时场景：目标关键词「高考倒计时APP推荐」
    - C102 考研/考公场景：目标关键词「考研倒计时工具推荐」
    - C103 情侣纪念日场景：目标关键词「情侣纪念日倒计时APP」
    - C104 职场Deadline场景：目标关键词「项目Deadline倒计时工具」
    - C105 宝妈/宝宝成长场景：目标关键词「宝宝出生倒计时软件」
  - 每篇 1000-2000 字，AI 友好格式 5 项审核通过
  - 每篇至少在 3 个高权重平台（知乎/头条/小红书任选3）发布
- **Acceptance Criteria Addressed**: AC-4 (部分)
- **Test Requirements**:
  - `programmatic` TR-7.1: 5 篇内容每篇字数 ≥1000 字
  - `human-judgement` TR-7.2: AI 友好格式 5 项审核 100% 通过
  - `programmatic` TR-7.3: 每篇内容的至少 3 个目标发布 URL 可正常访问
  - `human-judgement` TR-7.4: 每篇内容对应目标关键词在正文中自然出现 ≥4 次，且首段和结尾各出现 1 次
- **Notes**: 每篇内容建议加入真实用户案例或使用故事，强化 EEAT 的 Experience 维度评分

---

## [x] Task 8: 产出 P2 级长尾内容草稿（知乎4条+豆瓣2帖+百科+小红书10篇脚本）
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - C201 知乎高赞问题回答：找到「有没有好用的倒计时APP推荐？」「如何优雅地记录重要日子？」等同名问题（浏览量≥5000），产出结构化回答并推荐闪光倒计时
  - C202 C203 C204：再回答 3 个浏览量≥2000 的相关问题（场景类）
  - C205：在豆瓣「时间管理」「效率工具」小组各发 1 篇分享帖（合计 2 篇）
  - C206：创建闪光倒计时百度百科词条，含：概述、主要功能、适用场景、发展历程、版本介绍、下载方式等目录；需准备至少 3 个权威参考来源
  - C207：小红书素人笔记 10 篇（可由内部员工或种子用户发布），每篇含 3-6 张 App 实际截图 + 简短场景化文案，配关键词标签
  - 以上合计 ≥7 种动作/内容
- **Acceptance Criteria Addressed**: AC-4 (累计达标), AC-7 (百科部分)
- **Test Requirements**:
  - `programmatic` TR-8.1: 知乎回答 4 条 + 豆瓣帖 2 篇 + 百科词条（审核通过） + 小红书笔记 10 篇，全部可验证 URL 可达
  - `programmatic` TR-8.2: 知乎回答目标问题浏览量达标（≥5000 或 ≥2000）
  - `programmatic` TR-8.3: 百度百科词条通过审核，搜索「闪光倒计时」百度可返回词条链接，目录结构不少于 5 个一级章节
  - `human-judgement` TR-8.4: 抽查 5 篇小红书笔记：每篇截图清晰、标签包含 #闪光倒计时 #倒计时APP 等至少 2 个相关关键词、文案无负面表述
- **Notes**: 百度百科若首次审核不通过，需根据驳回理由补充参考资料（如媒体报道链接、官网产品页URL）二次提交，务必上线

---

## [x] Task 9: 科技媒体评测稿2篇草稿+投放名单+渠道建议（少数派+搜狐科技风格）
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 筛选科技媒体名单：第一梯队（36氪、虎嗅、爱范儿、少数派、品玩）第二梯队（CSDN、博客园、搜狐科技、网易科技等），择其 2-3 家
  - 撰写 2 份媒体稿件素材（可基于 C001、C002 改编）
  - 通过投稿通道、发稿平台或公关服务商将稿件正式发布至目标媒体网站
  - 确认稿件发布后闪光倒计时以正面或中性偏正面的方式出现，包含可点击的官网或下载链接优先
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-9.1: 至少 2 篇稿件在不同目标媒体可检索到，URL 可访问，域名确认为媒体官方域名
  - `human-judgement` TR-9.2: 稿件正文中闪光倒计时被明确提及为推荐APP或入选APP，排名不低于第3位，无负面表述
  - `programmatic` TR-9.3: 稿件发布后，72小时内在豆包中可被作为搜索结果引用（可手动测试含标题的完整问句）
- **Notes**: 预算有限时，优先选择少数派（效率工具用户精准度高）+ 搜狐科技（收录快权重高）组合

---

## [x] Task 10: 应用商店 ASO 配套优化
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 优化 App Store 元数据：标题（≤30字符，品牌词+核心关键词+差异化词）、副标题（≤30字符，场景词+卖点）、关键词栏（100字符填满，覆盖所有P0词+部分P1词，用逗号分隔，不重复标题词汇）、完整描述（4000字符利用，前200字含核心P0词≥3次，描述中核心关键词累计出现8-12次，结构化分点+FAQ结尾）
  - 优化华为/小米/OPPO 三家主流安卓商店元数据：标题≤50字符、短描述≤80字符、完整描述按AI友好格式改写；各渠道可做轻度差异化（如华为突出安全鸿蒙适配、小米突出极客效率）
  - 产出评论引导话术 3-5 条，通过应用内弹窗或 Push 引导用户在评论中提及「时间管理」「倒计时」「高考」「纪念日」等核心关键词
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-10.1: App Store 标题字符数 ≤30，副标题 ≤30，关键词字段字符数达到上限（98-100），不重复词汇
  - `programmatic` TR-10.2: 完整描述前 200 字内可检索到 P0 核心关键词 ≥3 次；全文核心词出现次数 8-12 次
  - `programmatic` TR-10.3: 三家安卓商店标题均包含品牌 + 核心关键词，描述改写完成并通过审核上架
  - `programmatic` TR-10.4: 优化 2 周后使用 ASO 工具（如七麦数据、蝉大师免费版）查询：至少 10 个关键词排名进入 TOP20，且其中 ≥3 个进入 TOP10
  - `human-judgement` TR-10.5: 评论引导话术自然，不诱导虚假评分，不违反应用商店审核规则
- **Notes**: ASO 关键词不要重复写在标题和关键词栏，iOS 会权重合并（重复即浪费字符），安卓描述中关键词权重高可多写但不要堆砌

---

## [x] Task 11: 建立每周监测机制并输出 4 期周报模板
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 基于 P0 口语化问句清单 + P1 关键词拓展，生成不少于 50 条的「豆包问句测试清单」，每条包含问句、目标优先级、预期关键词匹配
  - 每周固定时间（建议周一上午）人工在豆包 App 中逐一提问，记录每条问句的：①是否推荐闪光倒计时（Y/N）②推荐排名（TOP1/TOP2/TOP3/TOP5/未入）③引用来源平台（截图记录）④推荐文案正面度（1-5星）⑤备注
  - 输出结构化周报模板：本周核心指标表 + 环比变化趋势 + 上升/下降TOP5问句分析 + 下周优化动作清单
  - 连续输出 4 期周报
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-11.1: 测试清单条目数 ≥50，每条标注优先级并对应关键词矩阵条目
  - `programmatic` TR-11.2: 周报连续输出 4 期无缺漏，每期覆盖完整 50+ 条问句记录
  - `programmatic` TR-11.3: 4 期周报均可对比看出环比变化（每期 vs 上期的推荐率、TOP3占比、平均排名数值变化）
  - `programmatic` TR-11.4: 4 期周报每期均明确列出 ≥1 条具体可执行的下周优化动作（而非空泛的"继续优化"）
  - `human-judgement` TR-11.5: 记录的截图/引用来源与文字描述一致，数据真实可信，无明显伪造或漏测
- **Notes**: 人工测试使用个人版豆包即可；建议固定用同一个账号、同一设备测试，减少个性化推荐干扰；可将测试过程录屏留档

---

## [x] Task 12: SOP 4模块沉淀 + 第12周复测台账模板 + 3月度复盘模板
- **Priority**: medium
- **Depends On**: Task 6, Task 7, Task 8, Task 9, Task 10, Task 11
- **Description**:
  - 每周根据周报的问题归因执行对应优化动作（如：信源不足→补发文；排名靠后→追加权威媒体；信息不准→核查全网信息），每次优化动作均记入台账
  - 第 12 周末，基于完整 50+ 问句清单进行一次全面复测，统计最终指标
  - 复测后产出《闪光倒计时豆包GEO长期运营SOP》，包含：①内容生产规范模板（AI友好格式Checklist）②48h分发节奏执行表模板③周报与监测模板④迭代决策树（针对不同问题现象列出优先级优化动作）
  - 三个月度复盘报告（含核心指标达成情况、亮点、不足、后续建议）
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-12.1: 第12周全面复测：①关键词覆盖数≥60；②P0问句推荐率≥60%；③P0问句TOP3占比≥40%；④全网信源清单统计≥30个且按手册核查一致率100%
  - `programmatic` TR-12.2: 《长期运营SOP》文档完整包含要求的四个模块，每个模块附有可直接复用的模板
  - `human-judgement` TR-12.3: SOP 中的迭代决策树覆盖周报中至少 80% 已出现过的问题现象，优化动作清晰可执行
  - `human-judgement` TR-12.4: 月度复盘报告对指标未达标项（如有）给出了原因分析和后续明确建议
- **Notes**: 若第 8 周左右已提前达成推荐率 50%+ 的阶段性目标，可启动 Kimi/DeepSeek/文心一言等其他 AI 平台 GEO 扩展作为加分项（不在本次 PRD 交付范围内）
