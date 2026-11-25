#!/usr/bin/env python3
"""Build an editable 16:9 PPTX from strategy-work-summary content (native shapes/text)."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
from copy import deepcopy
from pathlib import Path

G = RGBColor(0x15, 0x7A, 0x3A)
GD = RGBColor(0x0D, 0x4F, 0x26)
GS = RGBColor(0xE8, 0xF6, 0xEE)
GM = RGBColor(0xB7, 0xDC, 0xC6)
INK = RGBColor(0x17, 0x30, 0x24)
INK2 = RGBColor(0x3D, 0x52, 0x48)
INK3 = RGBColor(0x6B, 0x7D, 0x74)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xD5, 0xE5, 0xDB)


def set_run(run, size=11, bold=False, color=INK, name="Microsoft YaHei"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    # East Asian font
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = parse_xml(f'<a:ea xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{name}"/>')
        rPr.append(ea)
    else:
        ea.set("typeface", name)


def add_textbox(slide, left, top, width, height, text, size=11, bold=False, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    try:
        tf._txBody.bodyPr.set("anchor", {MSO_ANCHOR.TOP: "t", MSO_ANCHOR.MIDDLE: "ctr", MSO_ANCHOR.BOTTOM: "b"}[anchor])
    except Exception:
        pass
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=color)
    return box


def set_fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def set_line(shape, color=GM, width_pt=1):
    shape.line.color.rgb = color
    shape.line.width = Pt(width_pt)


def no_line(shape):
    shape.line.fill.background()


def rect(slide, left, top, width, height, fill=WHITE, line=GM, radius=False):
    shape = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shape, left, top, width, height)
    set_fill(s, fill)
    if line is None:
        no_line(s)
    else:
        set_line(s, line)
    if radius:
        try:
            s.adjustments[0] = 0.08
        except Exception:
            pass
    return s


def pill(slide, left, top, width, height, text, fill=GS, text_color=GD, size=10, bold=True):
    s = rect(slide, left, top, width, height, fill=fill, line=GM, radius=True)
    tf = s.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    set_run(run, size=size, bold=bold, color=text_color)
    try:
        tf._txBody.bodyPr.set("anchor", "ctr")
    except Exception:
        pass
    return s


def header(slide, kicker, title, who_lines):
    add_textbox(slide, Inches(0.35), Inches(0.18), Inches(9.2), Inches(0.28), kicker, size=11, color=INK3)
    add_textbox(slide, Inches(0.35), Inches(0.42), Inches(9.2), Inches(0.4), title, size=20, bold=True, color=INK)
    y = 0.2
    for i, line in enumerate(who_lines):
        add_textbox(
            slide, Inches(10.2), Inches(y + i * 0.22), Inches(2.9), Inches(0.24),
            line, size=10 if i else 12, bold=(i == 0), color=GD if i == 0 else INK2, align=PP_ALIGN.RIGHT,
        )
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.35), Inches(0.9), Inches(12.65), Pt(1.5))
    set_fill(line, GM)
    no_line(line)


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # ---------- Slide 1 ----------
    s = prs.slides.add_slide(blank)
    header(s, "01　业务视角 · 我对业务的贡献", "两年工作在战略屋里的位置",
           ["LEAPMOTOR", "郭静 · 产品经理 · 营销运营部", "现职级 P3-B · 申请 P4-A · 2025.01—2026.11"])

    roof = rect(s, Inches(0.35), Inches(1.05), Inches(12.65), Inches(1.05), fill=GS, line=GM, radius=True)
    add_textbox(s, Inches(0.5), Inches(1.12), Inches(12.3), Inches(0.22), "战略愿景", size=11, bold=True, color=GD)
    add_textbox(s, Inches(0.5), Inches(1.34), Inches(12.3), Inches(0.35),
                "成为驱动零跑全球增长的核心智能引擎，构建超百万级用户与伙伴共赢的数智生态。", size=14, bold=True, color=INK)
    add_textbox(s, Inches(0.5), Inches(1.72), Inches(12.3), Inches(0.3),
                "两年工作只对两条业务组合：公域投放效率、车主服务。前者靠用户在公域发帖形成内容供给；后者靠服务管家 IM 把售后协同做成可自动运转的子系统。",
                size=11, color=INK2)

    stats = [
        ("85", "份方案进入评审或上线\n2025 年 48 份，2026 年去重 37 份"),
        ("2", "条业务组合上的主线\n公域投放 · 车主服务"),
        ("3", "处写清边界的 AI\n审贴、充电 RAG、群机器人"),
        ("6", "个公域分发平台\n抖音、小红书、汽车之家等"),
    ]
    for i, (n, lab) in enumerate(stats):
        x = 0.35 + i * 3.2
        rect(s, Inches(x), Inches(2.25), Inches(3.05), Inches(0.85), fill=WHITE, line=GM, radius=True)
        add_textbox(s, Inches(x + 0.12), Inches(2.32), Inches(2.8), Inches(0.35), n, size=22, bold=True, color=GD)
        add_textbox(s, Inches(x + 0.12), Inches(2.68), Inches(2.8), Inches(0.38), lab, size=10, color=INK2)

    add_textbox(s, Inches(0.35), Inches(3.2), Inches(4), Inches(0.28), "业务组合上的落点", size=13, bold=True, color=GD)
    add_textbox(s, Inches(3.5), Inches(3.22), Inches(9.3), Inches(0.28),
                "对应战略意图「强体验」与「助决策」。其余业务组合不在这两年的主责范围。", size=11, color=INK3)

    # two pillars
    pillars = [
        ("强体验", "提升公域投放效率", "内容供给",
         "公域投放要的不是多开一个站内频道，而是让车主和创作者愿意、并能稳定地在公域发帖。两年从 0 到 1 把供给链建起来。",
         [("创作者平台", "2025 从 0 到 1：达人招募、任务、奖励、站外发帖覆盖六大平台。2026 主投入 13 份：OCR、申诉、AI 审贴、分层配额等。"),
          ("全员营销", "让员工也能在公域发帖并获奖励，与创作者平台共用任务、审核与激励。"),
          ("口碑生产", "问卷改抓汽车之家口碑，口径统一，指标改为点评量与转化。"),
          ("投放工具", "UGC 同步抖音/小红书；专题页 uid/openid 溯源；按渠道看 PV/UV。"),
          ("消息订阅", "补齐潜客消息订阅，关键节点可触达，公域回流后可运营。")]),
        ("助决策", "提升车主服务", "主责子系统",
         "车主服务核心是服务管家 IM：问得到人、跟得上、重复咨询由系统先答。",
         [("服务 IM", "自动建群→运营闭环→移动端→五项自动化（ROI≈7.1）→群机器人可独立回复。"),
          ("充电问答", "充电手册/资讯/素材做成 RAG；置信度不足不答；首响目标≤3 秒。"),
          ("转介绍", "海报进素材库；奖励改绑车核销保养券；试驾车绑车人取消资格。"),
          ("车主课堂", "逐题反馈；功能 code 多选推送；企微批量解锁最多 2000 台。")]),
    ]
    for pi, (intent, h3, flag, why, lines) in enumerate(pillars):
        x = 0.35 + pi * 6.45
        rect(s, Inches(x), Inches(3.55), Inches(6.25), Inches(3.7), fill=WHITE, line=G, radius=True)
        hd = rect(s, Inches(x), Inches(3.55), Inches(6.25), Inches(0.55), fill=GD, line=None)
        add_textbox(s, Inches(x + 0.15), Inches(3.58), Inches(4.5), Inches(0.2), intent, size=10, color=WHITE)
        add_textbox(s, Inches(x + 0.15), Inches(3.78), Inches(4.5), Inches(0.28), h3, size=14, bold=True, color=WHITE)
        add_textbox(s, Inches(x + 4.4), Inches(3.68), Inches(1.7), Inches(0.3), flag, size=10, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)
        add_textbox(s, Inches(x + 0.15), Inches(4.2), Inches(5.95), Inches(0.45), why, size=10, color=INK2)
        y = 4.7
        for tag, body in lines:
            pill(s, Inches(x + 0.15), Inches(y), Inches(1.35), Inches(0.28), tag, fill=GS, text_color=GD, size=9)
            add_textbox(s, Inches(x + 1.6), Inches(y), Inches(4.45), Inches(0.42), body, size=9, color=INK2)
            y += 0.48

    # ---------- Slide 2 ----------
    s = prs.slides.add_slide(blank)
    header(s, "02　用户视角 · 我对用户的贡献", "潜客 · 售前　｜　车主 · 售后",
           ["LEAPMOTOR", "两列重点场景：场景 → 我做了什么 → 满意度", "潜客 · 售前　｜　车主 · 售后"])

    cols = [
        ("潜客", " · 售前", "官方/公域认知 → 感知 → 转化 → 触达",
         "场景 · 看车、看口碑、被内容种草，并完成接受邀请 / 留资转化",
         [("官方认知", "查看口碑", "官方小程序了解零跑：口碑取消问卷，改抓汽车之家，站内直接看真实口碑。"),
          ("公域认知", "内容种草", "创作者与 UGC 触达潜客；专题页溯源，公域种草可回流站内量化。"),
          ("感知", "年终报告", "支持生成、分享与抽奖，售前也能回顾互动成绩并二次传播。"),
          ("转化", "转介绍接受邀请", "接受邀请页先勾隐私再发验证码；邀请码按注册时间起算，减少误伤。"),
          ("触达", "消息订阅通知", "补齐潜客消息订阅能力，关键节点可触达，减少错过通知。")],
         "满意度：官方与公域都能快速了解；品牌印象更深；转化路径清楚有优惠；关键信息不漏接。"),
        ("车主", " · 售后", "下单 → 交付 → 绑定 → 智驾 → 咨询 → 感知",
         "场景 · 沿用车旅程持续参与活动、学功能开权限，并在售后问得到人",
         [("新车下单", "转介绍活动", "海报五版进素材库；奖励改绑车核销保养券；进入专属服务群。"),
          ("新车交付", "口碑活动", "真实用车表达可持续产出，反哺潜客种草与公域内容供给。"),
          ("新车绑定", "创作者活动", "平台 0→1；申诉、AI 审贴、分层配额；车主可持续发帖。"),
          ("智驾功能激活", "车主课堂", "逐题反馈；功能 code 多选推送；企微批量解锁最多 2000 台。"),
          ("售后咨询", "AI 搜索（充电）", "充电手册/资讯/素材做成 RAG，更快找到功能与充电答案。"),
          ("售后咨询", "专属服务群", "答不上来自动建群；运营闭环、移动端、五项自动化与群机器人。"),
          ("品牌感知", "年终报告", "可生成、分享与抽奖，沉淀可晒可邀的情感触点。")],
         "满意度：节点都有可参与活动；学功能即时反馈；搜得到、问得清。目标：响应 5′→2″，待办 60%→95%。"),
    ]
    for ci, (role, stage, em, scene, rows, sat) in enumerate(cols):
        x = 0.3 + ci * 6.5
        rect(s, Inches(x), Inches(1.05), Inches(6.35), Inches(5.85), fill=WHITE, line=G, radius=True)
        hd = rect(s, Inches(x), Inches(1.05), Inches(6.35), Inches(0.55), fill=GD if ci == 0 else G, line=None)
        add_textbox(s, Inches(x + 0.15), Inches(1.1), Inches(3.5), Inches(0.28), role + stage, size=14, bold=True, color=WHITE)
        add_textbox(s, Inches(x + 0.15), Inches(1.38), Inches(6), Inches(0.2), em, size=10, color=WHITE)
        add_textbox(s, Inches(x + 0.15), Inches(1.7), Inches(6.05), Inches(0.35), scene, size=10, color=INK2)
        add_textbox(s, Inches(x + 0.15), Inches(2.05), Inches(2), Inches(0.22), "我做了什么", size=11, bold=True, color=GD)
        y = 2.3
        for st, k, anno in rows:
            pill(s, Inches(x + 0.15), Inches(y), Inches(1.25), Inches(0.26), st, fill=GS, size=8)
            pill(s, Inches(x + 1.5), Inches(y), Inches(1.45), Inches(0.26), k, fill=WHITE, text_color=GD, size=8)
            add_textbox(s, Inches(x + 3.05), Inches(y), Inches(3.1), Inches(0.42), anno, size=8, color=INK2)
            y += 0.48
        add_textbox(s, Inches(x + 0.15), Inches(6.4), Inches(6.05), Inches(0.4), sat, size=9, color=INK2)

    add_textbox(s, Inches(0.35), Inches(7.05), Inches(12.6), Inches(0.3),
                "领导记两句：潜客售前按「官方/公域认知 → 感知 → 转化 → 触达」跑通；车主售后按「下单 → 交付 → 绑定 → 智驾 → 咨询 → 感知」贯穿活动、课堂与服务。",
                size=10, color=INK3)

    # ---------- Slide 3 ----------
    s = prs.slides.add_slide(blank)
    header(s, "03　专业案例 · 我对关键问题的拆解", "创作者平台：公域投放痛点与解决方案",
           ["LEAPMOTOR", "案例 01 / 02", "对齐战略 · 提升公域投放效率"])

    rect(s, Inches(0.3), Inches(1.05), Inches(12.7), Inches(1.55), fill=GS, line=GM, radius=True)
    add_textbox(s, Inches(0.45), Inches(1.1), Inches(12.4), Inches(0.22), "背景与行业 / 业务痛点", size=11, bold=True, color=GD)
    add_textbox(s, Inches(0.45), Inches(1.32), Inches(12.4), Inches(0.35),
                "2025 年初，公域内容仍依赖人工拉群与表格维护达人 / KOC；车主与员工发帖散落多平台，任务、审核、奖励未产品化。",
                size=11, color=INK2)
    pains = [
        ("痛点 1 · 转化难统计", "公域内容素材带来的转化链路断裂，投放效果难闭环。"),
        ("痛点 2 · KOC 难维护", "达人 / KOC 数据靠表格，名单、任务、履约状态难统一管理。"),
        ("痛点 3 · 审核与奖励慢", "审核量大、人工处理，奖励发放延迟严重，创作者体验差。"),
        ("痛点 4 · 运营效率低", "活动难规模化复制，车主与员工供给无法稳定放大。"),
    ]
    for i, (t, b) in enumerate(pains):
        x = 0.45 + i * 3.15
        rect(s, Inches(x), Inches(1.75), Inches(3.0), Inches(0.72), fill=WHITE, line=GM, radius=True)
        add_textbox(s, Inches(x + 0.1), Inches(1.8), Inches(2.8), Inches(0.22), t, size=11, bold=True, color=GD)
        add_textbox(s, Inches(x + 0.1), Inches(2.05), Inches(2.8), Inches(0.38), b, size=9, color=INK2)

    # left solution panel
    rect(s, Inches(0.3), Inches(2.75), Inches(8.55), Inches(4.45), fill=WHITE, line=G, radius=True)
    hd = rect(s, Inches(0.3), Inches(2.75), Inches(8.55), Inches(0.4), fill=GD, line=None)
    add_textbox(s, Inches(0.45), Inches(2.82), Inches(8), Inches(0.28), "创作者平台解决方案", size=13, bold=True, color=WHITE)

    # supply col
    rect(s, Inches(0.45), Inches(3.3), Inches(1.7), Inches(3.7), fill=GS, line=GM, radius=True)
    add_textbox(s, Inches(0.5), Inches(3.35), Inches(1.6), Inches(0.25), "用户 / 供给", size=11, bold=True, color=GD, align=PP_ALIGN.CENTER)
    for i, t in enumerate(["潜客", "车主", "全体员工\n全员营销"]):
        pill(s, Inches(0.55), Inches(3.7 + i * 0.45), Inches(1.5), Inches(0.38), t.replace("\n", " · "), size=10)
    add_textbox(s, Inches(0.5), Inches(5.1), Inches(1.6), Inches(0.22), "平台", size=11, bold=True, color=GD, align=PP_ALIGN.CENTER)
    for i, t in enumerate(["小红书", "懂车帝", "汽车之家", "微博", "今日头条", "抖音"]):
        pill(s, Inches(0.55), Inches(5.35 + i * 0.28), Inches(1.5), Inches(0.25), t, size=9)

    add_textbox(s, Inches(2.25), Inches(4.9), Inches(0.35), Inches(0.35), "→", size=18, bold=True, color=G, align=PP_ALIGN.CENTER)

    # scenes
    rect(s, Inches(2.6), Inches(3.3), Inches(1.7), Inches(3.7), fill=GS, line=GM, radius=True)
    add_textbox(s, Inches(2.65), Inches(3.35), Inches(1.6), Inches(0.25), "业务场景", size=11, bold=True, color=GD, align=PP_ALIGN.CENTER)
    for i, t in enumerate(["招募审核", "活动设置", "达人维护", "帖子审核", "奖励下发", "效果评估", "预算约束"]):
        pill(s, Inches(2.7), Inches(3.7 + i * 0.42), Inches(1.5), Inches(0.35), t, size=10)

    add_textbox(s, Inches(4.4), Inches(4.9), Inches(0.35), Inches(0.35), "→", size=18, bold=True, color=G, align=PP_ALIGN.CENTER)

    mods = [
        ("数据采集与管理", "抖音、小红书、汽车之家、懂车帝、头条、微博——公域发帖统一回流。"),
        ("KOC 管理", "达人 / KOC 名单、分层、履约与合作状态统一维护，替代表格管理。"),
        ("活动中心", "报名、任务、分层配额、奖励发放；员工与车主均可获激励。"),
        ("审核中心", "OCR 验真 + AI 审贴 + 人审 / 申诉，降低积压与错发。"),
    ]
    for i, (t, b) in enumerate(mods):
        col, row = i % 2, i // 2
        x = 4.85 + col * 1.95
        y = 3.3 + row * 1.85
        rect(s, Inches(x), Inches(y), Inches(1.85), Inches(1.7), fill=WHITE, line=GM, radius=True)
        hd = rect(s, Inches(x), Inches(y), Inches(1.85), Inches(0.35), fill=G, line=None)
        add_textbox(s, Inches(x + 0.08), Inches(y + 0.05), Inches(1.7), Inches(0.28), t, size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_textbox(s, Inches(x + 0.1), Inches(y + 0.45), Inches(1.65), Inches(1.15), b, size=10, color=INK2)

    # right empty results
    rect(s, Inches(9.05), Inches(2.75), Inches(3.95), Inches(4.45), fill=WHITE, line=G, radius=True)
    hd = rect(s, Inches(9.05), Inches(2.75), Inches(3.95), Inches(0.4), fill=GD, line=None)
    add_textbox(s, Inches(9.2), Inches(2.82), Inches(3.6), Inches(0.28), "案例成果", size=13, bold=True, color=WHITE)
    add_textbox(s, Inches(9.2), Inches(4.7), Inches(3.6), Inches(0.4), "（待补充截图 / 数据）", size=12, color=INK3, align=PP_ALIGN.CENTER)

    # ---------- Slide 4 ----------
    s = prs.slides.add_slide(blank)
    header(s, "04　专业案例 · 我对关键问题的拆解", "服务 SCRM：车主服务痛点与解决方案",
           ["LEAPMOTOR", "案例 02 / 02", "对齐战略 · 提升车主服务"])

    rect(s, Inches(0.3), Inches(1.05), Inches(12.7), Inches(1.45), fill=GS, line=GM, radius=True)
    add_textbox(s, Inches(0.45), Inches(1.1), Inches(12.4), Inches(0.2), "背景与业务痛点", size=11, bold=True, color=GD)
    add_textbox(s, Inches(0.45), Inches(1.3), Inches(12.4), Inches(0.32),
                "售后咨询与跟进长期依赖一对一沟通和个人经验；门店管家、总部管家、服务运营入口割裂，信息不在同一会话，重复咨询与漏跟进并存。",
                size=11, color=INK2)
    pains = [
        ("痛点 1 · 车主入口", "车主找不到稳定服务入口，问得到人难、体验碎片化。"),
        ("痛点 2 · 门店协同", "门店跟进难协同、难留痕，跨角色靠人肉同步。"),
        ("痛点 3 · 重复咨询", "重复咨询吃掉管家产能，权限 / 自动化 / 质检难做。"),
        ("痛点 4 · 难量化", "响应与待办不可量化，漏跟进难以及时发现。"),
    ]
    for i, (t, b) in enumerate(pains):
        x = 0.45 + i * 3.15
        rect(s, Inches(x), Inches(1.7), Inches(3.0), Inches(0.68), fill=WHITE, line=GM, radius=True)
        add_textbox(s, Inches(x + 0.1), Inches(1.75), Inches(2.8), Inches(0.2), t, size=11, bold=True, color=GD)
        add_textbox(s, Inches(x + 0.1), Inches(1.98), Inches(2.8), Inches(0.35), b, size=9, color=INK2)

    rect(s, Inches(0.3), Inches(2.65), Inches(8.7), Inches(4.55), fill=WHITE, line=G, radius=True)
    hd = rect(s, Inches(0.3), Inches(2.65), Inches(8.7), Inches(0.38), fill=GD, line=None)
    add_textbox(s, Inches(0.45), Inches(2.7), Inches(8.3), Inches(0.28), "服务 SCRM 解决方案 · 架构", size=13, bold=True, color=WHITE)

    # layer 1 business
    rect(s, Inches(0.45), Inches(3.15), Inches(8.4), Inches(1.55), fill=GS, line=GM, radius=True)
    pill(s, Inches(0.55), Inches(3.22), Inches(0.95), Inches(0.26), "业务场景", fill=GD, text_color=WHITE, size=10)
    add_textbox(s, Inches(1.6), Inches(3.24), Inches(6.5), Inches(0.22), "触点接入 → 售后服务过程 → 协同与分析", size=10, color=INK3)

    rect(s, Inches(0.55), Inches(3.55), Inches(1.35), Inches(1.05), fill=WHITE, line=GM, radius=True)
    add_textbox(s, Inches(0.6), Inches(3.58), Inches(1.25), Inches(0.2), "触点 / 角色", size=10, bold=True, color=GD, align=PP_ALIGN.CENTER)
    for i, t in enumerate(["车主", "门店员工", "服务运营", "CC"]):
        pill(s, Inches(0.65), Inches(3.8 + i * 0.2), Inches(1.15), Inches(0.18), t, size=9)

    rect(s, Inches(2.0), Inches(3.55), Inches(5.2), Inches(1.05), fill=WHITE, line=GM, radius=True)
    add_textbox(s, Inches(2.1), Inches(3.57), Inches(5), Inches(0.18), "售后服务过程", size=10, bold=True, color=GD, align=PP_ALIGN.CENTER)
    # temp lane
    pill(s, Inches(2.1), Inches(3.8), Inches(0.7), Inches(0.28), "临时群", fill=GD, text_color=WHITE, size=9)
    steps1 = ["咨询进入", "自动建群", "一对多服务", "问题解决", "结案解散"]
    for i, t in enumerate(steps1):
        x = 2.9 + i * 0.82
        pill(s, Inches(x), Inches(3.8), Inches(0.72), Inches(0.28), t, size=8)
        if i < len(steps1) - 1:
            add_textbox(s, Inches(x + 0.7), Inches(3.8), Inches(0.15), Inches(0.28), "→", size=10, bold=True, color=G)
    # fixed lane
    pill(s, Inches(2.1), Inches(4.18), Inches(0.7), Inches(0.28), "固定群", fill=GD, text_color=WHITE, size=9)
    steps2 = ["专属群绑定", "日常服务", "待办协同", "工单留痕", "闭环回访"]
    for i, t in enumerate(steps2):
        x = 2.9 + i * 0.82
        pill(s, Inches(x), Inches(4.18), Inches(0.72), Inches(0.28), t, size=8)
        if i < len(steps2) - 1:
            add_textbox(s, Inches(x + 0.7), Inches(4.18), Inches(0.15), Inches(0.28), "→", size=10, bold=True, color=G)

    rect(s, Inches(7.3), Inches(3.55), Inches(1.4), Inches(1.05), fill=WHITE, line=GM, radius=True)
    add_textbox(s, Inches(7.35), Inches(3.58), Inches(1.3), Inches(0.18), "分析", size=10, bold=True, color=GD, align=PP_ALIGN.CENTER)
    for i, t in enumerate(["响应时效", "待办及时率", "重复咨询占比", "管家产能"]):
        pill(s, Inches(7.4), Inches(3.8 + i * 0.2), Inches(1.2), Inches(0.18), t, size=8)

    # layer 2 apps
    rect(s, Inches(0.45), Inches(4.85), Inches(8.4), Inches(1.2), fill=GS, line=GM, radius=True)
    pill(s, Inches(0.55), Inches(4.92), Inches(0.95), Inches(0.24), "应用中心", fill=GD, text_color=WHITE, size=10)
    apps = [
        ("专属服务群", ["自动建群", "一对多", "拉人入群", "同屏协同"]),
        ("门店响应", ["问题跟进", "素材库", "客户画像", "离职继承", "通知提醒"]),
        ("总部监管", ["满意度推送", "跟进单审核", "退网继承", "敏感词监控"]),
    ]
    for i, (title, items) in enumerate(apps):
        x = 0.55 + i * 2.7
        rect(s, Inches(x), Inches(5.25), Inches(2.55), Inches(0.7), fill=WHITE, line=GM, radius=True)
        hd = rect(s, Inches(x), Inches(5.25), Inches(2.55), Inches(0.24), fill=G, line=None)
        add_textbox(s, Inches(x), Inches(5.26), Inches(2.55), Inches(0.22), title, size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_textbox(s, Inches(x + 0.08), Inches(5.52), Inches(2.4), Inches(0.4), " · ".join(items), size=8, color=INK2)

    # layer 3 foundation
    rect(s, Inches(0.45), Inches(6.2), Inches(8.4), Inches(0.85), fill=GS, line=GM, radius=True)
    pill(s, Inches(0.55), Inches(6.28), Inches(0.95), Inches(0.24), "能力底座", fill=GD, text_color=WHITE, size=10)
    bases = [
        ("会话中台", "IM 会话 · 群聊 · 存档"),
        ("自动化引擎", "规则触发 · 待办 · 工单"),
        ("业务集成", "APP · 门店 · 知识库"),
    ]
    for i, (t, b) in enumerate(bases):
        x = 0.55 + i * 2.7
        rect(s, Inches(x), Inches(6.58), Inches(2.55), Inches(0.4), fill=WHITE, line=GM, radius=True)
        add_textbox(s, Inches(x + 0.08), Inches(6.6), Inches(2.4), Inches(0.18), t, size=10, bold=True, color=GD)
        add_textbox(s, Inches(x + 0.08), Inches(6.78), Inches(2.4), Inches(0.18), b, size=9, color=INK2)

    # right empty
    rect(s, Inches(9.2), Inches(2.65), Inches(3.8), Inches(4.55), fill=WHITE, line=G, radius=True)
    hd = rect(s, Inches(9.2), Inches(2.65), Inches(3.8), Inches(0.38), fill=GD, line=None)
    add_textbox(s, Inches(9.35), Inches(2.7), Inches(3.5), Inches(0.28), "案例成果", size=13, bold=True, color=WHITE)
    add_textbox(s, Inches(9.35), Inches(4.7), Inches(3.5), Inches(0.4), "（待补充截图 / 数据）", size=12, color=INK3, align=PP_ALIGN.CENTER)

    out = Path("/workspace/strategy-work-summary.pptx")
    out_cn = Path("/workspace/两年工作总结-战略对齐.pptx")
    prs.save(str(out))
    out_cn.write_bytes(out.read_bytes())
    Path("/opt/cursor/artifacts/strategy-work-summary.pptx").write_bytes(out.read_bytes())
    Path("/opt/cursor/artifacts/两年工作总结-战略对齐.pptx").write_bytes(out.read_bytes())
    Path("/cursor/stores/user/文稿").mkdir(parents=True, exist_ok=True)
    Path("/cursor/stores/user/文稿/strategy-work-summary.pptx").write_bytes(out.read_bytes())
    Path("/cursor/stores/user/文稿/两年工作总结-战略对齐.pptx").write_bytes(out.read_bytes())
    print("saved editable pptx", out.stat().st_size, "slides", len(prs.slides))


if __name__ == "__main__":
    build()
