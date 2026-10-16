"""Render ELEPHAN Instagram slides in a restrained editorial visual system."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"generated"
W,H=1080,1350
FONT_BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

NAVY=(13,18,38)
NAVY_2=(22,25,52)
IVORY=(249,246,239)
INK=(24,27,38)
GOLD=(196,157,76)
GOLD_SOFT=(224,211,174)
PLUM=(72,48,74)
MUTED=(120,122,132)
PALE=(236,232,223)

def font(path,size):
    return ImageFont.truetype(path,size=size)

def wrap(draw,text,fnt,maxw):
    lines=[]
    for block in text.split("\n"):
        if block=="":
            lines.append("")
            continue
        cur=""
        for ch in block:
            test=cur+ch
            if draw.textbbox((0,0),test,font=fnt)[2] <= maxw:
                cur=test
            else:
                if cur:
                    lines.append(cur)
                cur=ch
        if cur:
            lines.append(cur)
    return lines

def elephant(draw,x,y,s=1.0,color=GOLD):
    w=max(2,int(3*s))
    draw.ellipse((x,y,x+52*s,y+52*s),outline=color,width=w)
    draw.arc((x+14*s,y+12*s,x+47*s,y+48*s),25,310,fill=color,width=w)
    draw.ellipse((x+38*s,y+20*s,x+43*s,y+25*s),fill=color)

def dark_bg():
    top=Image.new("RGB",(W,H),NAVY)
    bottom=Image.new("RGB",(W,H),NAVY_2)
    mask=Image.linear_gradient("L").resize((W,H))
    img=Image.composite(bottom,top,mask).convert("RGBA")

    # One restrained soft light only; no neon arcs, stars, or particles.
    glow=Image.new("RGBA",(W,H),(0,0,0,0))
    gd=ImageDraw.Draw(glow)
    gd.ellipse((650,-260,1260,360),fill=(*PLUM,80))
    glow=glow.filter(ImageFilter.GaussianBlur(120))
    img.alpha_composite(glow)
    return img

def light_bg():
    return Image.new("RGBA",(W,H),(*IVORY,255))

def brand_dark(img,n):
    d=ImageDraw.Draw(img)
    elephant(d,64,58,0.75,GOLD)
    d.text((112,56),"ELEPHAN",font=font(FONT_BOLD,27),fill=IVORY)
    d.text((112,92),"夜の仕事を整理する",font=font(FONT_REG,18),fill=(188,190,200))
    d.text((950,64),f"{n}/5",font=font(FONT_REG,19),fill=(170,173,184))
    d.line((62,138,1018,138),fill=(*GOLD_SOFT,95),width=1)

def brand_light(img,n):
    d=ImageDraw.Draw(img)
    elephant(d,64,58,0.75,GOLD)
    d.text((112,56),"ELEPHAN",font=font(FONT_BOLD,27),fill=INK)
    d.text((112,92),"夜の仕事を整理する",font=font(FONT_REG,18),fill=MUTED)
    d.text((950,64),f"{n}/5",font=font(FONT_REG,19),fill=MUTED)
    d.line((62,138,1018,138),fill=GOLD_SOFT,width=1)

def draw_left_text(img,text,x,y,size,maxw,fill,line_gap=18):
    d=ImageDraw.Draw(img)
    f=font(FONT_BOLD,size)
    lines=wrap(d,text,f,maxw)
    cur_y=y
    for line in lines:
        d.text((x,cur_y),line,font=f,fill=fill)
        cur_y += size + line_gap
    return cur_y

def cover(text,out):
    img=dark_bg()
    brand_dark(img,1)
    d=ImageDraw.Draw(img)

    # Quiet category label: the hook itself does the stopping.
    d.text((66,235),"店との相性 / SELF CHECK",font=font(FONT_BOLD,21),fill=GOLD)

    y=330
    y=draw_left_text(img,text,66,y,80,900,IVORY,22)

    # Thin editorial accent, not a CTA button.
    accent_y=min(1050,y+70)
    d.line((66,accent_y,300,accent_y),fill=GOLD,width=4)
    d.text((66,accent_y+34),"売上だけで決めない。",font=font(FONT_BOLD,29),fill=GOLD_SOFT)
    d.text((66,accent_y+82),"2枚目から、判断軸を分けて見ます。",font=font(FONT_REG,22),fill=(202,203,211))

    out.parent.mkdir(parents=True,exist_ok=True)
    img.convert("RGB").save(out,"PNG",optimize=True)

def interior(text,n,out):
    img=light_bg()
    brand_light(img,n)
    d=ImageDraw.Draw(img)

    # Large pale page number gives visual rhythm without looking like a template card.
    d.text((690,205),f"0{n}",font=font(FONT_BOLD,150),fill=PALE)

    label=["POINT","CHECK","JUDGE","NEXT"][n-2]
    d.text((66,238),label,font=font(FONT_BOLD,20),fill=GOLD)
    d.line((66,280,210,280),fill=GOLD,width=3)

    y=370
    y=draw_left_text(img,text,66,y,64,870,INK,22)

    if n<5:
        d.text((66,1170),"感情と数字を分けて見る。",font=font(FONT_REG,22),fill=MUTED)
    else:
        d.line((66,1136,1014,1136),fill=GOLD_SOFT,width=1)
        d.text((66,1172),"必要ならプロフィールから個別に整理できます。",font=font(FONT_BOLD,24),fill=INK)
        d.text((66,1222),"占いは判断材料のひとつ。大きな判断は現実の条件も確認してください。",font=font(FONT_REG,16),fill=MUTED)

    out.parent.mkdir(parents=True,exist_ok=True)
    img.convert("RGB").save(out,"PNG",optimize=True)

def render(text,n,out):
    if n==1:
        cover(text,out)
    else:
        interior(text,n,out)

def main():
    posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
    for p in posts:
        if len(p["slides"])!=5:
            raise ValueError(f"{p['date']}: five slides required")
        for i,t in enumerate(p["slides"],1):
            render(t,i,OUT/p["date"]/f"{i:02d}.png")
        print(f"rendered {p['date']} editorial_v2")

if __name__=="__main__":
    main()
