"""Generate the bilingual concept maps using only Python's standard library."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent
COPY = {
    "en": {
        "title": "From need to something that works",
        "eyebrow": "3D PRINT MODELING / A CONNECTED PRACTICE",
        "need": "Understand the person",
        "needsub": "Purpose / context / constraints",
        "core": "DESIGN AT THE CENTER",
        "model": "Model",
        "modelsub": "Form / interfaces / assembly",
        "visual": "Explain visually",
        "visualsub": "Sketch / section / product view",
        "research": "Research",
        "researchsub": "Mechanisms / alternatives",
        "make": "Manufacture",
        "makesub": "Orientation / seams / supports",
        "proof": "Check the evidence",
        "proofsub": "Geometry / toolpaths / physical use",
        "loop": "Carry the learning forward",
        "loopsub": "Issues > lessons > next use > corrections",
        "footer": "Specialist skills as needed. No fixed sequence.",
    },
    "zh-CN": {
        "title": "从人的诉求，到真正好用的物件",
        "eyebrow": "3D PRINT MODELING / 开放式项目实践",
        "need": "理解人的诉求",
        "needsub": "用途 / 场景 / 约束",
        "core": "设计处于中心",
        "model": "建模",
        "modelsub": "形体 / 接口 / 装配",
        "visual": "视觉表达",
        "visualsub": "草图 / 剖面 / 产品图",
        "research": "研究",
        "researchsub": "机制 / 备选方案",
        "make": "制造",
        "makesub": "朝向 / 接缝 / 支撑",
        "proof": "核对真实证据",
        "proofsub": "几何 / 刀路 / 实物使用",
        "loop": "把经验带入下一次",
        "loopsub": "问题 → 经验 → 下次应用 → 纠错",
        "footer": "按需连接专业技能，不是固定阶段。",
    },
}


def draw(lang, c):
    out = ['''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="1060" viewBox="0 0 960 1060" role="img" aria-labelledby="title desc">
<defs>
  <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#dedbd1" stroke-width="0.7"/></pattern>
  <marker id="arrow" markerWidth="4" markerHeight="4" refX="6" refY="4" viewBox="0 0 8 8" orient="auto-start-reverse"><path d="M0 0L7 4L0 8" fill="none" stroke="#3b756e" stroke-width="1.5"/></marker>
</defs>
<rect width="960" height="1060" rx="24" fill="#f6f3e9"/>
<rect width="960" height="1060" rx="24" fill="url(#grid)"/>
<g font-family="Helvetica Neue, PingFang SC, sans-serif" fill="#193e3b">''']
    out.insert(1, f'<title id="title">{escape(c["title"])}</title><desc id="desc">Concept map / 概念示意. Modeling and visual communication connect to human needs, research, manufacturing, evidence and learning. Not a tested product.</desc>')

    def text(x, y, value, size=30, weight=400, color="#193e3b", anchor="middle"):
        out.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(value)}</text>')

    def rect(x, y, w, h, fill, stroke="none", radius=18):
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')

    def link(d, both=True, dashed=False):
        out.append(f'<path d="{d}" fill="none" stroke="#3b756e" stroke-width="3" marker-end="url(#arrow)"'
                   + (' marker-start="url(#arrow)"' if both else '')
                   + (' stroke-dasharray="8 8"' if dashed else '') + '/>')

    text(48, 52, c['eyebrow'], 20, 600, anchor="start")
    text(48, 108, c['title'], 40, 700, anchor="start")
    rect(180, 150, 600, 110, "#ffffff", "#c5d3cc")
    text(480, 193, c['need'], 34, 600)
    text(480, 232, c['needsub'], 27)
    link("M480 270V303")
    rect(48, 318, 864, 228, "#193e3b")
    text(480, 360, c['core'], 23, 600, "#b7d8cd")
    out.append('<path d="M480 386V510" stroke="#688e82" stroke-width="2"/>')
    text(267, 427, c['model'], 44, 700, "#fff9e8")
    text(267, 479, c['modelsub'], 27, 400, "#d9e7de")
    text(693, 427, c['visual'], 40, 700, "#fff9e8")
    text(693, 479, c['visualsub'], 27, 400, "#d9e7de")
    link("M267 558V592")
    link("M693 558V592")
    rect(48, 608, 414, 110, "#ffffff", "#c5d3cc")
    rect(498, 608, 414, 110, "#ffffff", "#c5d3cc")
    text(255, 652, c['research'], 34, 600)
    text(255, 691, c['researchsub'], 27)
    text(705, 652, c['make'], 34, 600)
    text(705, 691, c['makesub'], 25)
    link("M255 729V750H480V771", both=False)
    link("M705 729V750H480", both=False)
    rect(134, 790, 692, 110, "#dce8df")
    text(480, 834, c['proof'], 34, 600)
    text(480, 875, c['proofsub'], 28)
    # The side return connects evidence back to design, not a mandatory next step.
    link("M837 845H938V343H925", both=False)
    link("M480 907V928", both=False, dashed=True)
    link("M39 976H22V205H167", both=False, dashed=True)
    rect(48, 940, 864, 72, "#e9c77e")
    text(480, 970, c['loop'], 28, 600)
    text(480, 999, c['loopsub'], 24)
    text(480, 1044, c['footer'], 23)
    out.append('</g></svg>')
    path = ROOT / f'project-map.{lang}.svg'
    path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(path.name)


if __name__ == '__main__':
    for language, copy in COPY.items():
        draw(language, copy)
