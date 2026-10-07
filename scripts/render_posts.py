"""Render ELEPHAN Instagram carousel slides as 1080x1350 PNGs."""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated"
W, H = 1080, 1350
BG = "#0B1020"
PANEL = "#121A31"
PANEL_2 = "#17203B"
GOLD = "#D6B36A"
IVORY = "#F6F0E5"
LAVENDER = "#8E7BAE"
MUTED = "#B8B2C2"
LINE = "#2A3042"

FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def font(path, size):
    return ImageFont.truetype(path, size=size)


def wrap(draw, text, fnt, max_width):
    lines = []
    for block in text.split("\n"):
        if not block:
            lines.append("")
            continue
        current = ""
        for ch in block:
            test = current + ch
            if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines


def draw_brand(draw, slide_no):
    draw.ellipse((72, 72, 118, 118), outline=GOLD, width=5)
    draw.arc((82, 80, 108, 109), 35, 310, fill=GOLD, width=4)
    draw.ellipse((101, 87, 108, 94), fill=GOLD)
    draw.text((140, 70), "ELEPHAN", font=font(FONT_BOLD, 34), fill=IVORY)
    draw.text((140, 112), "夜職の仕事運・金運", font=font(FONT_REG, 24), fill=MUTED)
    draw.text((920, 78), f"{slide_no}/5", font=font(FONT_REG, 28), fill=MUTED)


def center_lines(draw, text, fnt, max_width, y, line_h, fill=IVORY):
    lines = wrap(draw, text, fnt, max_width)
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=fnt)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y + i * line_h), line, font=fnt, fill=fill)
    return len(lines)


def render_empathy(draw, text, slide_no):
    # Editorial / quote-led layout: large statement, more breathing room.
    draw.arc((650, -145, 1160, 390), 105, 245, fill=GOLD, width=7)
    draw.ellipse((865, 265, 879, 279), fill=LAVENDER)
    if slide_no == 1:
        draw.text((76, 300), "TONIGHT'S NOTE", font=font(FONT_BOLD, 24), fill=GOLD)
        draw.rounded_rectangle((72, 360, 1008, 975), radius=42, fill=PANEL, outline=LINE, width=2)
        center_lines(draw, text, font(FONT_BOLD, 72), 790, 505, 102)
        draw.text((77, 1025), "大きな決断は、疲れた夜だけで決めない。", font=font(FONT_REG, 27), fill=MUTED)
    else:
        draw.rounded_rectangle((72, 320, 1008, 1020), radius=42, fill=PANEL, outline=LINE, width=2)
        draw.text((115, 390), "CHECK", font=font(FONT_BOLD, 28), fill=GOLD)
        center_lines(draw, text, font(FONT_BOLD, 61), 760, 535, 90)


def render_checklist(draw, text, slide_no):
    # Structured checklist layout with visible modular cards.
    draw.text((76, 295), "CHECK LIST", font=font(FONT_BOLD, 25), fill=GOLD)
    if slide_no == 1:
        draw.rounded_rectangle((72, 345, 1008, 940), radius=36, fill=PANEL, outline=GOLD, width=2)
        center_lines(draw, text, font(FONT_BOLD, 68), 800, 485, 98)
        draw.rounded_rectangle((72, 995, 470, 1065), radius=35, fill=PANEL_2)
        draw.text((105, 1013), "保存してあとで確認", font=font(FONT_BOLD, 28), fill=IVORY)
    else:
        parts = [p for p in text.split("\n") if p.strip()]
        y = 360
        for part in parts[:3]:
            draw.rounded_rectangle((72, y, 1008, y + 165), radius=30, fill=PANEL, outline=LINE, width=2)
            draw.ellipse((110, y + 55, 138, y + 83), fill=GOLD)
            fnt = font(FONT_BOLD, 48)
            lines = wrap(draw, part, fnt, 760)
            for i, line in enumerate(lines):
                draw.text((175, y + 45 + i * 66), line, font=fnt, fill=IVORY)
            y += 195


def render_diagnostic(draw, text, slide_no):
    # Choice / diagnosis layout: split the problem into decision blocks.
    draw.text((76, 292), "SORT THE FLOW", font=font(FONT_BOLD, 25), fill=LAVENDER)
    if slide_no == 1:
        draw.rounded_rectangle((72, 350, 1008, 810), radius=44, fill=PANEL, outline=LINE, width=2)
        center_lines(draw, text, font(FONT_BOLD, 67), 800, 470, 96)
        for i, label in enumerate(("追う", "守る", "動く")):
            x1 = 72 + i * 312
            draw.rounded_rectangle((x1, 885, x1 + 280, 1015), radius=30, outline=GOLD if i == 1 else LINE, width=3)
            bbox = draw.textbbox((0, 0), label, font=font(FONT_BOLD, 35))
            draw.text((x1 + 140 - (bbox[2] - bbox[0]) / 2, 930), label, font=font(FONT_BOLD, 35), fill=IVORY)
    else:
        draw.rounded_rectangle((72, 350, 1008, 1015), radius=44, fill=PANEL, outline=LINE, width=2)
        draw.text((115, 405), f"0{slide_no-1}", font=font(FONT_BOLD, 70), fill=GOLD)
        center_lines(draw, text, font(FONT_BOLD, 58), 750, 555, 88)


def render_slide(text, slide_no, output, creative_type):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_brand(draw, slide_no)

    if creative_type == "empathy":
        render_empathy(draw, text, slide_no)
    elif creative_type == "checklist":
        render_checklist(draw, text, slide_no)
    elif creative_type == "diagnostic":
        render_diagnostic(draw, text, slide_no)
    else:
        render_empathy(draw, text, slide_no)

    draw.line((72, 1190, 1008, 1190), fill=LINE, width=2)
    draw.text((72, 1248), "占いは判断材料のひとつ。大きな仕事・金銭判断は現実の条件も確認してください。", font=font(FONT_REG, 20), fill=MUTED)
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, "PNG", optimize=True)


def main():
    posts = json.loads((ROOT / "posts.json").read_text(encoding="utf-8"))
    for post in posts:
        if len(post["slides"]) != 5:
            raise ValueError(f"{post['date']}: exactly five slides are required")
        creative_type = post.get("creative_type", "empathy")
        if creative_type not in {"empathy", "checklist", "diagnostic"}:
            raise ValueError(f"{post['date']}: invalid creative_type")
        day_dir = OUT / post["date"]
        for idx, text in enumerate(post["slides"], start=1):
            render_slide(text, idx, day_dir / f"{idx:02d}.png", creative_type)
        print(f"rendered {post['date']} type={creative_type}")


if __name__ == "__main__":
    main()
