"""Render approved-style glamorous ELEPHAN five-panel Instagram carousels.

Use ONLY the user-approved 2026-10-17-revised images as photographic sources.
The approved card images contain preprinted copy; take model-only crops so
yesterday's writing cannot leak into future posts. A new day's Japanese copy
comes from posts.json, never from the old images. Does not edit Oct 17 assets.
"""
from datetime import date
from pathlib import Path
import json
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "generated" / "2026-10-17-revised"
OUTPUT = ROOT / "generated" / "glam-v1"
W, H = 1080, 1350
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
WHITE = (255, 250, 253)
PINK = (255, 26, 154)
GOLD = (255, 213, 77)
DARK = (19, 3, 24)

def font(size, kind="bold"):
    return ImageFont.truetype({"bold": BOLD, "serif": SERIF, "reg": REG}[kind], size)

def lines_for(draw, text, size, width, kind="bold"):
    result = []
    ff = font(size, kind)
    for paragraph in text.replace("\r", "").split("\n"):
        if not paragraph:
            continue
        line = ""
        for char in paragraph:
            test = line + char
            if draw.textbbox((0, 0), test, font=ff)[2] <= width:
                line = test
            else:
                if line:
                    result.append(line)
                line = char
        if line:
            result.append(line)
    return result

def draw_copy(im, text, x, y, max_width, max_height, base_size=76, first_color=WHITE,
              last_color=PINK, kind="bold", center=False):
    draw = ImageDraw.Draw(im)
    for size in range(base_size, 28, -2):
        lines = lines_for(draw, text, size, max_width, kind)
        leading = int(size * 1.33)
        if len(lines) * leading <= max_height:
            break
    for k, line in enumerate(lines):
        xx = x
        if center:
            xx = x + (max_width - draw.textbbox((0,0), line, font=font(size,kind))[2]) // 2
        color = last_color if k == len(lines) - 1 else first_color
        # Bright pink glow behind the last/highlighted line, crisp white stroke.
        if k == len(lines)-1 and last_color == PINK:
            layer = Image.new("RGBA", (W,H), (0,0,0,0))
            ld = ImageDraw.Draw(layer)
            ld.text((xx,y), line, font=font(size,kind), fill=(255,10,157,205), stroke_width=5,stroke_fill=(255,10,157,195))
            im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(13)))
        draw.text((xx,y), line, font=font(size,kind), fill=color,
                  stroke_width=2, stroke_fill=(25,1,24))
        y += leading
    return y

def source_portraits():
    for i in [1,2,4]:
        if not (SOURCE / f"{i:02d}.jpg").exists():
            raise FileNotFoundError(f"Approved image not found: {i:02d}.jpg")
    # Actual clean model-only crops from the user-approved 10/17 photos.
    a = Image.open(SOURCE/"01.jpg").convert("RGB").crop((716,210,1055,850))
    b = Image.open(SOURCE/"02.jpg").convert("RGB").crop((634,175,1051,1085))
    c = Image.open(SOURCE/"04.jpg").convert("RGB").crop((39,445,518,852))
    return [a,b,c]

def background(portraits,seed):
    src=portraits[seed % len(portraits)]
    bg=ImageOps.fit(src,(W,H),method=Image.Resampling.LANCZOS)
    bg=bg.filter(ImageFilter.GaussianBlur(55))
    bg=ImageEnhance.Color(bg).enhance(1.65).convert("RGBA")
    bg.alpha_composite(Image.new("RGBA",(W,H),(34,2,39,174)))
    return bg

def portrait_on(im, image, *, right=True, top=164, width=640, height=1056):
    img=ImageOps.fit(image,(width,height),method=Image.Resampling.LANCZOS,centering=(.5,.42))
    img=ImageEnhance.Color(img).enhance(1.22).convert("RGBA")
    x = W-width+10 if right else -10
    mask=Image.new("L",(width,height),0)
    m=mask.load()
    for row in range(height):
        vy=min(1.,row/100.,(height-1-row)/135.)
        for col in range(width):
            vx=min(1.,col/95.,(width-1-col)/34.)
            m[col,row]=round(255*max(0.,vx)*max(0.,vy))
    im.paste(img,(x,top),mask)

def overlay(im, dark_strength=230, *, side="left"):
    grad=Image.new("RGBA",(W,1))
    pixels=grad.load()
    for x in range(W):
        t=x/W if side=="left" else (W-x)/W
        a=int(44 + dark_strength*(1-t)**2.0)
        pixels[x,0]=(7,1,18,min(245,a))
    im.alpha_composite(grad.resize((W,H)))

def neon_line(im,x,y,length,color=PINK):
    d=ImageDraw.Draw(im)
    pts=[(x+k*length/48,y+6*math.sin(k/5)) for k in range(49)]
    gl=Image.new("RGBA",(W,H))
    ImageDraw.Draw(gl).line(pts,fill=(*color,210),width=14,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(13)))
    d.line(pts,fill=color,width=7,joint="curve")

def label(im,n):
    d=ImageDraw.Draw(im)
    d.ellipse((46,43,107,104),outline=GOLD,width=4)
    d.arc((57,52,99,97),20,302,fill=GOLD,width=4)
    d.text((125,42),"ELEPHAN",font=font(34),fill=WHITE)
    d.text((126,87),"夜職の仕事運・金運",font=font(19,"reg"),fill=WHITE)
    d.text((911,35),f"{n:02d}/05",font=font(32,"serif"),fill=WHITE,stroke_width=2,stroke_fill=DARK)

def footer(im,n):
    d=ImageDraw.Draw(im)
    d.line((55,1256,1027,1256),fill=GOLD,width=2)
    d.text((57,1274),"ELEPHAN / NIGHT WORK",font=font(22,"reg"),fill=WHITE)
    if n!=5:
        d.text((922,1274),"SWIPE ›",font=font(23),fill=WHITE)

def badge(im, labeltext, color=PINK):
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((57,175,645,245),20,fill=(13,2,30,227),outline=color,width=4)
    d.text((79,189),labeltext,font=font(29),fill=WHITE)

def card(im,box,fill=(10,1,24,226),edge=PINK,roundness=25):
    d=ImageDraw.Draw(im)
    d.rounded_rectangle(box,roundness,fill=fill,outline=edge,width=4)

def render(post,n,portraits,seed):
    # Rotate the three approved glamorous models while retaining the brand treatment.
    model = portraits[(seed+n-1) % len(portraits)]
    im = background(portraits,seed+n)
    if n == 1:
        portrait_on(im,model,right=True,top=158,width=695,height=1090)
        overlay(im,233,side="left")
        badge(im,"NIGHT WORK / REAL TALK",GOLD)
        bottom=draw_copy(im,post["slides"][0],57,362,735,630,base_size=94,kind="serif")
        neon_line(im,55,min(1073,bottom+10),680)
        d=ImageDraw.Draw(im)
        card(im,(54,1116,1018,1224),fill=(35,2,39,220),edge=GOLD)
        d.text((87,1147),"指名・売上・人間関係を整理する。",font=font(29),fill=WHITE)
    elif n == 2:
        portrait_on(im,model,right=True,top=175,width=600,height=1060)
        overlay(im,238,side="left")
        badge(im,"CHECK 01 / まず整理",GOLD)
        card(im,(55,367,687,944),fill=(10,1,24,202),edge=PINK)
        bottom=draw_copy(im,post["slides"][1],91,467,544,416,base_size=66,last_color=PINK)
        neon_line(im,94,min(910,bottom+25),530)
        ImageDraw.Draw(im).text((80,1102),"焦らず、事実を分けて見る。",font=font(33),fill=GOLD)
    elif n == 3:
        portrait_on(im,model,right=False,top=188,width=660,height=1050)
        overlay(im,225,side="right")
        badge(im,"CHECK 02 / 比べる視点",GOLD)
        card(im,(395,350,1031,1006),edge=GOLD)
        bottom=draw_copy(im,post["slides"][2],437,468,550,442,base_size=78)
        neon_line(im,424,min(956,bottom+25),575)
        d=ImageDraw.Draw(im)
        d.text((441,1089),"数字と気持ち、どちらも大切。",font=font(26),fill=WHITE)
    elif n == 4:
        portrait_on(im,model,right=True,top=187,width=620,height=1020)
        overlay(im,231,side="left")
        badge(im,"REAL CHECK / 大切なサイン",GOLD)
        card(im,(54,375,697,946),fill=(10,1,24,198),edge=PINK)
        bottom=draw_copy(im,post["slides"][3],87,469,560,419,base_size=65)
        neon_line(im,86,min(916,bottom+25),549)
        ImageDraw.Draw(im).text((91,1101),"無理していないか、確認しよう。",font=font(29),fill=GOLD)
    else:
        portrait_on(im,model,right=True,top=160,width=620,height=1090)
        overlay(im,236,side="left")
        badge(im,"SAVE / 次にできること",GOLD)
        card(im,(50,359,690,965),fill=(10,1,24,201),edge=GOLD)
        bottom=draw_copy(im,post["slides"][4],87,451,555,462,base_size=60)
        neon_line(im,85,min(928,bottom+22),545)
        d=ImageDraw.Draw(im)
        d.rounded_rectangle((55,1075,1030,1205),26,fill=PINK)
        cta="個別鑑定はプロフィールのLINEへ" if "プロフィール" in post["slides"][4] or "LINE" in post["slides"][4] else "保存して、あとから見返す"
        d.text((94,1114),cta,font=font(32),fill=WHITE)
    label(im,n)
    footer(im,n)
    return im.convert("RGB")

def main():
    posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
    portraits=source_portraits()
    for post in posts:
        day=post["date"]
        if day < "2026-10-18":
            continue
        if len(post["slides"])!=5:
            raise ValueError("Expected exactly 5 slides for "+day)
        seed = date.fromisoformat(day).toordinal()
        folder=OUTPUT/day
        folder.mkdir(parents=True,exist_ok=True)
        for n in range(1,6):
            output=folder/f"{n:02d}.jpg"
            image=render(post,n,portraits,seed)
            if image.size!=(W,H): raise ValueError("Unexpected dimensions")
            image.save(output,format="JPEG",quality=90,optimize=True,subsampling=0)
            if output.stat().st_size<30000:raise ValueError(f"Suspiciously small {output}")
        print("ELEPHAN GLAM V1:",day,"JPEG 5/5",flush=True)

if __name__ == "__main__":
    main()
