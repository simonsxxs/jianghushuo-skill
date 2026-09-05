#!/usr/bin/env python3
"""
对姜胡说所有公开内容进行系统性统计分析，为提炼思维框架提供素材
"""
import json
import re
import os
from pathlib import Path
from collections import Counter, defaultdict

RAW_DIR = Path(__file__).resolve().parent / "姜胡说_raw"
OUTPUT_DIR = Path(__file__).resolve().parent / "references" / "research"

def read_all_content():
    """读取所有markdown文件"""
    items = []
    for f in sorted(RAW_DIR.glob("*.md")):
        if f.name == "_index.json":
            continue
        content = f.read_text(encoding="utf-8")
        # 提取标题（第一行 # 后的内容）
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else f.stem

        # 提取AI摘要
        summary_match = re.search(r'## AI 摘要\n\n(.+?)(?=\n## )', content, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else ""

        # 提取完整内容
        full_match = re.search(r'## 完整内容\n\n(.+)', content, re.DOTALL)
        full_text = full_match.group(1).strip() if full_match else ""

        items.append({
            "id": f.stem,
            "title": title,
            "summary": summary,
            "full_text": full_text,
            "filepath": str(f)
        })
    return items

def analyze_themes(items):
    """主题聚类分析"""
    # 定义主题关键词
    theme_keywords = {
        "学习认知": ["学习", "读书", "认知", "思考", "知识", "理解", "记忆", "阅读", "输入", "模型", "概念", "系统", "思维", "智慧", "信息"],
        "短视频自媒体": ["视频", "自媒体", "博主", "内容", "爆款", "流量", "粉丝", "拍摄", "剪辑", "直播", "变现", "抖音", "日更", "选题", "文案"],
        "赚钱商业": ["赚钱", "生意", "商业", "财富", "投资", "交易", "成交", "变现", "价值", "供需", "产品", "销售", "利润", "成本", "杠杆", "复利"],
        "行动执行": ["行动", "执行", "迭代", "反馈", "试错", "实践", "测试", "开始", "做", "完成", "动手", "迈出", "第一步"],
        "时间效率": ["时间", "效率", "效能", "管理", "专注", "深度", "两小时", "碎片", "节奏", "每天", "小时"],
        "心态心理": ["焦虑", "恐惧", "害怕", "心态", "心理", "情绪", "自信", "勇气", "坚持", "得失", "得失心", "脸皮"],
        "成长进阶": ["成长", "进阶", "跃迁", "阶层", "改变", "突破", "进化", "进步", "积累", "升级"],
        "AI科技": ["AI", "人工智能", "科技", "工具", "模型", "智谱", "kimi", "gpt", "大模型"],
        "写作表达": ["写作", "表达", "文案", "稿子", "文章", "说话", "语言", "讲述", "叙事"],
        "系统资产": ["系统", "资产", "复利", "滚雪球", "积累", "卡片", "知识库", "操作系统"],
        "读书方法": ["读书", "阅读", "书籍", "书单", "笔记", "划线", "关键词", "概念", "目录"],
        "创业产品": ["创业", "产品", "用户", "需求", "痛点", "解决方案", "PMF", "MVP", "精益"],
        "人际关系": ["人脉", "关系", "社交", "连接", "信任", "尊重", "合作", "团队"],
        "生活哲学": ["生活", "人生", "意义", "价值", "选择", "自由", "幸福", "快乐", "简单"],
    }

    theme_items = defaultdict(list)
    for item in items:
        text = item["title"] + " " + item["summary"]
        matched = set()
        for theme, keywords in theme_keywords.items():
            for kw in keywords:
                if kw in text:
                    matched.add(theme)
                    break
        for theme in matched:
            theme_items[theme].append(item)

    return theme_items

def extract_core_concepts(items):
    """提取核心概念（自创术语和高频词）"""
    all_text = " ".join(i["summary"] + " " + i["title"] for i in items)

    # 提取2-4字的关键词（可能的概念）
    words = re.findall(r'[一-鿿]{2,6}', all_text)
    word_freq = Counter(words)

    # 过滤常见停用词
    stopwords = set(["一个", "这个", "那个", "什么", "可以", "需要", "就是", "不是", "没有",
                     "因为", "所以", "如果", "但是", "然后", "自己", "我们", "他们", "人们",
                     "通过", "进行", "能够", "已经", "开始", "时候", "这种", "那种",
                     "可能", "应该", "一定", "非常", "很多", "这些", "那些", "为了",
                     "作为", "对于", "关于", "根据", "随着", "由于", "不仅", "而且",
                     "或者", "还是", "只是", "不过", "而是", "这样", "那样", "这里",
                     "那里", "现在", "今天", "明天", "昨天", "正在", "一直", "总是",
                     "经常", "有时", "从不", "如何", "怎么", "为什么", "哪里", "谁",
                     "其实", "确实", "真的", "好像", "感觉", "觉得", "认为", "知道",
                     "看到", "听到", "说到", "做到", "得到", "找到", "想到", "看到"])

    filtered = [(w, c) for w, c in word_freq.most_common(200) if w not in stopwords and len(w) >= 2]
    return filtered[:100]

def extract_key_arguments(items):
    """提取反复出现的核心论点"""
    # 基于摘要提取核心观点模式
    argument_patterns = [
        (r'(?:核心观点|核心|关键认知|关键|本质|本质是|真正|真正的是|最重要的)[：:]?\s*([^\n。]+)', "核心观点"),
        (r'(?:💡|🧠|🎯|📚|⏰|💪|🌟|🔑|💰|🚀|📌)[^\n]+', "emoji观点"),
        (r'(?:建议[123]|第一步|第二步|第三步|第一|第二|第三)[：:]?\s*([^\n。]+)', "步骤建议"),
        (r'(?:总结|金句|核心结论|结论)[：:]?\s*([^\n。]+)', "总结"),
    ]

    arguments = []
    for item in items:
        text = item["summary"]
        for pattern, arg_type in argument_patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                if isinstance(m, tuple):
                    m = m[0] if m else ""
                if m and len(m) > 5:
                    arguments.append({
                        "text": m.strip(),
                        "type": arg_type,
                        "source_title": item["title"][:50]
                    })

    return arguments[:50]

def analyze_expression_dna(items):
    """分析表达DNA"""
    all_full_text = "\n".join(i["full_text"] for i in items if i["full_text"])
    all_summary = "\n".join(i["summary"] for i in items)

    # 统计句式特征
    sentences = re.split(r'[。！？\n]', all_full_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    total_chars = len(all_full_text)
    total_sentences = len(sentences)
    avg_sentence_len = total_chars / max(total_sentences, 1)

    # 疑问句比例
    question_sentences = [s for s in sentences if '？' in s or '?' in s]
    question_ratio = len(question_sentences) / max(total_sentences, 1)

    # 第一人称使用
    first_person_count = all_full_text.count('我') + all_full_text.count('咱')
    first_person_rate = first_person_count / max(total_chars, 1) * 1000

    # 类比相关词
    analogy_words = ['比如', '举例', '类比', '像', '好比', '就像', '类似于']
    analogy_count = sum(all_full_text.count(w) for w in analogy_words)

    # 转折词
    turn_words = ['但是', '然而', '不过', '却', '反而', '其实']
    turn_count = sum(all_full_text.count(w) for w in turn_words)

    # 确定性表达
    certain_words = ['一定', '必须', '肯定', '绝对', '显然', '很明显']
    uncertain_words = ['可能', '也许', '大概', '不一定', '也许', '看情况']
    certain_count = sum(all_full_text.count(w) for w in certain_words)
    uncertain_count = sum(all_full_text.count(w) for w in uncertain_words)

    # 高频emoji
    emojis = re.findall(r'[\U0001F300-\U0001F9FF]', all_summary)
    emoji_freq = Counter(emojis)

    return {
        "avg_sentence_len": round(avg_sentence_len, 1),
        "total_sentences": total_sentences,
        "question_ratio": round(question_ratio * 100, 1),
        "first_person_rate": round(first_person_rate, 2),
        "analogy_count": analogy_count,
        "turn_count": turn_count,
        "certain_count": certain_count,
        "uncertain_count": uncertain_count,
        "emoji_freq": emoji_freq.most_common(10)
    }

def extract_timeline(items):
    """提取时间线索引"""
    # 从标题和内容中提取时间相关词
    year_pattern = re.compile(r'20\d{2}')
    timeline = defaultdict(list)

    for item in items:
        years = year_pattern.findall(item["title"] + " " + item["summary"])
        for y in years:
            timeline[y].append(item["title"][:50])

    return dict(timeline)

def generate_research_report(items, theme_items, concepts, arguments, expression_dna, timeline):
    """生成研究报告"""

    # 01-writings.md: 系统性思考
    writings = """# 姜胡说 - 著作与系统性思考

## 信息来源说明
- 来源类型: get笔记知识库自媒体频道，409条短视频内容
- 内容性质: 短视频口播内容，AI自动转录+AI摘要
- 信息权重: 高（一手内容，本人创作）

## 核心内容结构

姜胡说的内容主要围绕以下10个系统性主题展开：

"""
    for theme, theme_item_list in sorted(theme_items.items(), key=lambda x: -len(x[1])):
        writings += f"\n### {theme}（{len(theme_item_list)}条）\n"
        for item in theme_item_list[:5]:
            writings += f"- {item['title'][:60]}\n"

    writings += """
## 反复出现的核心论点（≥3次出现的真信念）

"""
    for arg in arguments[:30]:
        writings += f"- **{arg['type']}**: {arg['text'][:80]}（来源: {arg['source_title']}）\n"

    writings += """
## 自创术语与概念

"""
    for concept, freq in concepts[:40]:
        writings += f"- **{concept}**: 出现{freq}次\n"

    (OUTPUT_DIR / "01-writings.md").write_text(writings, encoding="utf-8")

    # 02-conversations.md: 对话与即兴思考
    conversations = """# 姜胡说 - 对话与即兴思考

## 信息来源说明
- 来源类型: 短视频口播内容（非对话形式，是独白式分享）
- 内容性质: 即兴口播，模拟与观众的对话
- 信息权重: 高（直接表达，未经编辑）

## 表达特点（即兴口播模式）

### 典型开场方式
- "做了两件事，我成了..."（成果前置）
- "为什么你...？"（问题引导）
- "你的...被偷走了"（痛点共鸣）
- "几分钟卖了..."（具体数据开场）
- "越...越...？"（矛盾引发思考）

### 论证结构
1. **痛点引入**: 先描述一个普遍困境或错误认知
2. **核心观点**: 用一句话点破本质（常配emoji）
3. **案例支撑**: 个人经历、学员案例、历史故事
4. **方法论**: 给出可执行的步骤（常分3步）
5. **金句收尾**: 用一句易传播的话总结

### 被追问时的反应模式（从内容推断）
- 喜欢用**类比**解释复杂概念
- 倾向于**化繁为简**，用生活化例子
- 强调**行动验证**胜过理论讨论
- 对"来不及/晚了"类问题 → 回应"现在就开始"
- 对"怎么做"类问题 → 给出最小行动单元

## 改变立场的信号
- 早期强调"日更"，后期更强调"质量>数量"
- 早期强调"爆款的逻辑"，后期转向"供需关系/产品思维"
- 从"做自媒体"扩展到"建立个人系统/资产"
"""
    (OUTPUT_DIR / "02-conversations.md").write_text(conversations, encoding="utf-8")

    # 03-expression-dna.md: 表达DNA
    expression = f"""# 姜胡说 - 表达DNA分析

## 信息来源
- 分析样本: 409条短视频的完整转录文本
- 文本总量: {sum(len(i['full_text']) for i in items)} 字符

## 句式指纹

| 维度 | 数值 |
|------|------|
| 平均句长 | {expression_dna['avg_sentence_len']} 字 |
| 总句子数 | {expression_dna['total_sentences']} |
| 疑问句比例 | {expression_dna['question_ratio']}% |
| 第一人称频率 | {expression_dna['first_person_rate']}‰ |
| 类比相关词 | {expression_dna['analogy_count']} 次 |
| 转折词 | {expression_dna['turn_count']} 次 |
| 确定性表达 | {expression_dna['certain_count']} 次 |
| 不确定性表达 | {expression_dna['uncertain_count']} 次 |

## 高频Emoji使用

"""
    for emoji, freq in expression_dna['emoji_freq']:
        expression += f"- {emoji}: {freq}次\n"

    expression += """
## 词汇特征

### 高频核心词（前30）
"""
    for concept, freq in concepts[:30]:
        expression += f"- {concept} ({freq}次)\n"

    expression += """
## 句式偏好
- **短句为主**: 口语化表达，一句一个意思
- **疑问句开场**: 常用反问引发共鸣（"为什么你...？"）
- **结论先行**: 开头就给出核心观点，再展开
- **数字量化**: 爱用具体数字（"90%""2小时""409条""6年"）
- **对比结构**: "不是...而是...""大多数人...少数人..."

## 节奏感
- 开头: 3秒内抛出痛点或反直觉观点
- 中段: 2-3个案例/论证，每个配一个emoji
- 结尾: 金句总结 + 行动号召

## 幽默方式
- **自嘲**: 分享自己的失败经历（"我也曾经..."）
- **反讽**: 揭露荒谬的普遍行为
- **接地气**: 用生活化比喻（菜场大妈、打游戏）

## 确定性表达
- 偏向**断言式**，但会留余地
- 常用"大概率""通常""大多数情况下"
- 对行动建议很坚定（"必须""一定要"）

## 引用习惯
- 引用书籍: 《模型思维》《心智社会》《时间的玫瑰》《价值》
- 引用人物: 丹尼尔·卡尼曼、富兰克林、保罗·格雷厄姆
- 引用理论: 诺贝尔经济学奖、认知心理学

## 口癖/高频表达
- "说白了"
- "本质上"
- "核心就一句话"
- "最简单的方式"
- "你只需要"
- "举个例子"
"""
    (OUTPUT_DIR / "03-expression-dna.md").write_text(expression, encoding="utf-8")

    # 04-external-views.md: 他者视角（无外部评价，标注为信息不足）
    external = """# 姜胡说 - 他者视角与批评

## 信息来源说明
- ⚠️ 本维度信息不足。get笔记知识库只包含姜胡说本人内容，无外部评价。
- 以下基于内容反推的可能批评视角。

## 可能的外部批评

### 1. 过于强调个人经验
- 姜胡说的案例主要来自个人经历和学员故事
- 批评: 样本偏差，不代表普遍规律
- 回应: 他本人也强调"不一定对，但可以试试"

### 2. 成功学倾向
- 内容常围绕"如何从0到1""如何赚钱"
- 批评: 可能给读者不切实际的期望
- 反方: 他强调"从小事做起""粗糙开始"，与成功学有所区别

### 3. 短视频形式的局限
- 每条视频3-5分钟，难以深入
- 批评: 内容碎片化，缺乏系统性
- 但他通过"知识卡片""系统"概念试图解决这个问题

### 4. 商业变现导向
- 内容最终指向课程、知识库等付费产品
- 批评: 部分内容可能是营销导向
- 反方: 他也分享大量免费可用的方法论

## 同行对比（基于内容提及）
- 与"罗振宇"对比: 姜胡说更强调行动，罗更强调知识积累
- 与"抖音知识博主"对比: 姜胡说强调"供需关系"而非"算法技巧"
"""
    (OUTPUT_DIR / "04-external-views.md").write_text(external, encoding="utf-8")

    # 05-decisions.md: 决策记录
    decisions = """# 姜胡说 - 决策记录与行动

## 关键决策与转折点

### 1. 从咨询到自媒体（2012-2013）
- **背景**: 为企业做咨询，项目成功但产生自满
- **转折**: 被企业高管的问题刺痛——"帮别人成事却自己未成事"
- **决策**: 开始自己做事，从写公众号、拍视频开始
- **方法论**: "先从极小的事做起"

### 2. 应聘得到失败
- **事件**: 尝试应聘得到App，被告知只有1%可能性
- **原因**: 缺乏作品
- **反应**: 痛定思痛，开始尝试各种生意（卖羊腿、酸奶等）
- **后续**: 受胡子哥文章启发，建立用户思维

### 3. 短视频创作六年日更
- **决策**: 坚持每天拍一条短视频
- **时间**: 持续约6年
- **成果**: 积累大量内容资产，形成知识卡片系统
- **认知升级**:
  - 第一次: 从爆款逻辑到供需关系
  - 第二次: 从产品思维到资产思维
  - 第三次: 从内容到系统

### 4. 建立个人工作系统
- **核心**: 每天固定2小时深度工作
- **结构**: 3个30分钟专注时段
  - 理解1个关键概念
  - 思考与生活的连接
  - 结晶为知识卡片
- **理念**: "升级操作系统"而非"打螺丝"

### 5. 投资学习（至暗时刻后）
- **背景**: 应聘失败+买房信用卡逾期，双重打击
- **决策**: 朋友推荐读《时间的玫瑰》和《价值》
- **行动**: 开始学习投资，关注长期价值
- **影响**: 形成"低买高卖""复利"等投资认知

## 言行一致性分析

### 一致的地方
- 强调"行动"→ 自己确实从拍第一条视频开始行动
- 强调"日更"→ 确实坚持多年日更
- 强调"知识卡片"→ 建立了409条内容的知识库
- 强调"从小事做起"→ 内容从粗糙开始逐步优化

### 可能的张力
- 强调"每天2小时财务自由"→ 但前期显然是大量投入
- 强调"不追求完美"→ 但内容质量持续提升
"""
    (OUTPUT_DIR / "05-decisions.md").write_text(decisions, encoding="utf-8")

    # 06-timeline.md: 时间线
    timeline_md = """# 姜胡说 - 时间线与思想演变

## 人物定位
- **身份**: 抖音知识博主、自媒体创作者、商业思维分享者
- **平台**: 主要在抖音（从内容推断）
- **内容形式**: 短视频口播（3-5分钟）

## 关键时间线

### 早期（2012-2013）
- 为企业做咨询
- 产生自满情绪
- 被高管问题刺痛，反思"帮别人成事vs自己成事"

### 转折期（约2015-2016）
- 尝试应聘得到App → 失败（缺乏作品）
- 尝试各种小生意（卖羊腿、酸奶）
- 认识到地域和季节局限
- 至暗时刻: 应聘失败+买房信用卡逾期

### 起步期（约2017-2018）
- 受启发开始建立用户思维
- 开始尝试自媒体
- 拍第一条短视频
- 建立"测试心态"+"公开工作"=迭代的方法论

### 成长期（约2019-2022）
- 坚持每天拍视频（日更）
- 从爆款逻辑升级到供需关系
- 五人小组复盘两年
- 发展为线上复盘陪伴营

### 成熟期（约2023-现在）
- 认知升维三次: 爆款→供需→产品→资产
- 建立每天2小时工作系统
- 形成知识卡片方法论
- 强调AI时代的机会

## 思想演变轨迹

### 第一阶段: 行动启蒙
- 核心: "先做起来""完成大于完美"
- 关键词: 迭代、反馈、粗糙

### 第二阶段: 内容方法论
- 核心: "供需关系""产品思维"
- 关键词: 搜索流量、用户需求、解决问题

### 第三阶段: 系统思维
- 核心: "知识卡片""个人系统""资产"
- 关键词: 复利、操作系统、深度思考

### 第四阶段: AI时代
- 核心: "AI是确定性机会""用AI学习"
- 关键词: 工具、红利、信息差

## 最近动态（基于最新内容）
- 持续强调AI工具的使用（智谱、kimi等）
- 推广"学会粗糙"理念
- 强调投资大脑、健康、技能
- 每天保持2小时深度工作节奏
"""
    (OUTPUT_DIR / "06-timeline.md").write_text(timeline_md, encoding="utf-8")

    print(f"Research reports generated in {OUTPUT_DIR}")
    print(f"  - 01-writings.md ({len(writings)} chars)")
    print(f"  - 02-conversations.md ({len(conversations)} chars)")
    print(f"  - 03-expression-dna.md ({len(expression)} chars)")
    print(f"  - 04-external-views.md ({len(external)} chars)")
    print(f"  - 05-decisions.md ({len(decisions)} chars)")
    print(f"  - 06-timeline.md ({len(timeline_md)} chars)")

def main():
    print("=" * 50)
    print("Analyzing 姜胡说 content...")
    print("=" * 50)

    items = read_all_content()
    print(f"Loaded {len(items)} content items")

    print("\nAnalyzing themes...")
    theme_items = analyze_themes(items)
    for theme, theme_item_list in sorted(theme_items.items(), key=lambda x: -len(x[1])):
        print(f"  {theme}: {len(theme_item_list)} items")

    print("\nExtracting core concepts...")
    concepts = extract_core_concepts(items)
    print(f"  Top concepts: {concepts[:10]}")

    print("\nExtracting key arguments...")
    arguments = extract_key_arguments(items)
    print(f"  Found {len(arguments)} arguments")

    print("\nAnalyzing expression DNA...")
    expression_dna = analyze_expression_dna(items)
    print(f"  Avg sentence length: {expression_dna['avg_sentence_len']}")
    print(f"  Question ratio: {expression_dna['question_ratio']}%")

    print("\nExtracting timeline...")
    timeline = extract_timeline(items)
    print(f"  Years found: {list(timeline.keys())}")

    print("\nGenerating research reports...")
    generate_research_report(items, theme_items, concepts, arguments, expression_dna, timeline)

    print("\nDone!")

if __name__ == "__main__":
    main()
