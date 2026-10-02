"""Render ELEPHAN Instagram carousel slides as 1080x1350 PNGs."""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated"
W, H = 1080, 1350
BG = "#0B1020"
GOLD = "#D6B36A"
IVORY = "#F6F0E5"
LAVENDER = "#8E7BAE"
MUTED = "#B8B2C2"

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
            if draw.textbbox((0,0), test, font=fnt)[2] <= max_width:
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


def render_slide(text, slide_no, output):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_brand(draw, slide_no)

    # Quiet celestial accents
    draw.arc((640, -120, 1170, 410), 105, 245, fill=GOLD, width=7)
    draw.ellipse((894, 255, 909, 270), fill=GOLD)
    draw.ellipse((824, 188, 832, 196), fill=LAVENDER)
    draw.line((86, 1190, 995, 1190), fill="#2A3042", width=2)

    title_font = font(FONT_BOLD, 72 if slide_no == 1 else 64)
    lines = wrap(draw, text, title_font, 870)
    line_h = 100 if slide_no == 1 else 92
    total_h = len(lines) * line_h
    y = max(350, (H - total_h) // 2 - 20)

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0,0), line, font=title_font)
        x = (W - (bbox[2]-bbox[0])) // 2
        draw.text((x, y + i*line_h), line, font=title_font, fill=IVORY)

    if slide_no == 5:
        draw.rounded_rectangle((245, 1010, 835, 1122), radius=56, outline=GOLD, width=3)
        cta = "プロフィールのLINEへ"
        cta_font = font(FONT_BOLD, 38)
        bbox = draw.textbbox((0,0), cta, font=cta_font)
        draw.text(((W-(bbox[2]-bbox[0]))/2, 1041), cta, font=cta_font, fill=GOLD)

    draw.text((72, 1250), "占いは判断材料のひとつ。大きな仕事・金銭判断は現実の条件も確認してください。", font=font(FONT_REG, 20), fill=MUTED)
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, "PNG", optimize=True)


def main():
    posts = json.loads((ROOT / "posts.json").read_text(encoding="utf-8"))
    for post in posts:
        if len(post["slides"]) != 5:
            raise ValueError(f"{post['date']}: exactly five slides are required")
        day_dir = OUT / post["date"]
        for idx, text in enumerate(post["slides"], start=1):
            render_slide(text, idx, day_dir / f"{idx:02d}.png")
        print(f"rendered {post['date']}")


if __name__ == "__main__":
    main()
