"""Render ELEPHAN Instagram carousels in a loud luxury-night visual system."""
import json, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"generated"
W,H=1080,1350
FONT_BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

BLACK=(5,4,14); DEEP=(24,4,38); PINK=(255,36,150); PINK2=(255,86,190)
GOLD=(244,190,59); GOLD2=(255,224,135); WHITE=(255,249,244); MUTED=(213,193,214)
CYAN=(51,227,255)

def font(path,size): return ImageFont.truetype(path,size=size)

def wrap(draw,text,fnt,maxw):
    lines=[]
    for block in text.split("\n"):
        if not block: lines.append(""); continue
        cur=""
        for ch in block:
            test=cur+ch
            if draw.textbbox((0,0),test,font=fnt)[2] <= maxw: cur=test
            else:
                if cur: lines.append(cur)
                cur=ch
        if cur: lines.append(cur)
    return lines

def base(seed):
    img=Image.new("RGBA",(W,H),(*BLACK,255))
    bg=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(bg)
    # Large nightclub light washes.
    d.ellipse((500,-240,1300,550),fill=(*PINK,105))
    d.ellipse((-360,710,450,1500),fill=(*CYAN,55))
    d.ellipse((180,300,900,1120),fill=(110,25,170,40))
    bg=bg.filter(ImageFilter.GaussianBlur(145))
    img.alpha_composite(bg)

    rnd=random.Random(seed)
    # Glitter / bokeh.
    b=Image.new("RGBA",(W,H),(0,0,0,0)); bd=ImageDraw.Draw(b)
    for _ in range(62):
        x=rnd.randint(20,W-20); y=rnd.randint(120,H-30)
        r=rnd.randint(2,12)
        c=rnd.choice([GOLD,GOLD2,PINK,PINK2,CYAN,(165,100,255)])
        a=rnd.randint(85,220)
        bd.ellipse((x-r,y-r,x+r,y+r),fill=(*c,a))
        if r>8:
            bd.line((x-r*2,y,x+r*2,y),fill=(*c,170),width=2)
            bd.line((x,y-r*2,x,y+r*2),fill=(*c,170),width=2)
    img.alpha_composite(b.filter(ImageFilter.GaussianBlur(2)))
    return img

def glow_shape(img, box, color, radius=20, width=4):
    g=Image.new("RGBA",img.size,(0,0,0,0)); d=ImageDraw.Draw(g)
    d.rounded_rectangle(box,radius,outline=(*color,230),width=width)
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(15)))
    img.alpha_composite(g)

def draw_elephant(d,x,y):
    d.ellipse((x,y,x+45,y+45),outline=GOLD,width=3)
    d.arc((x+10,y+8,x+37,y+39),25,310,fill=GOLD,width=3)
    d.ellipse((x+31,y+16,x+37,y+22),fill=GOLD)

def brand(img,n):
    d=ImageDraw.Draw(img)
    draw_elephant(d,52,42)
    d.text((112,40),"ELEPHAN",font=font(FONT_BOLD,30),fill=WHITE)
    d.text((112,79),"夜職の仕事運・金運",font=font(FONT_REG,20),fill=MUTED)
    d.line((52,118,360,118),fill=GOLD,width=2)
    d.text((952,46),f"{n}/5",font=font(FONT_REG,21),fill=MUTED)

def glow_text(img,xy,text,fnt,fill,glow=PINK,stroke=4):
    x,y=xy
    layer=Image.new("RGBA",img.size,(0,0,0,0)); ld=ImageDraw.Draw(layer)
    ld.text((x,y),text,font=fnt,fill=(*glow,235),stroke_width=stroke+3,stroke_fill=(*glow,220))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(18)))
    ImageDraw.Draw(img).text((x,y),text,font=fnt,fill=fill,stroke_width=stroke,stroke_fill=(35,3,35))

def centered_lines(img,text,y,maxw=940,size=80,linegap=16):
    d=ImageDraw.Draw(img); f=font(FONT_BOLD,size)
    lines=wrap(d,text,f,maxw)
    for i,line in enumerate(lines):
        box=d.textbbox((0,0),line,font=f); x=(W-(box[2]-box[0]))//2
        fill=GOLD2 if i==0 else WHITE
        glow=PINK if i==len(lines)-1 else GOLD
        glow_text(img,(x,y+i*(size+linegap)),line,f,fill,glow,3)
    return y+len(lines)*(size+linegap)

def luxe_silhouette(img):
    # Abstract feminine profile / hair silhouette, kept decorative behind text.
    s=Image.new("RGBA",img.size,(0,0,0,0)); d=ImageDraw.Draw(s)
    d.ellipse((690,155,1035,545),fill=(10,4,20,150),outline=(*PINK,145),width=4)
    d.ellipse((770,205,955,420),fill=(44,12,46,105))
    d.arc((710,170,1025,555),205,60,fill=(*GOLD,165),width=5)
    d.arc((745,210,1005,525),210,35,fill=(*PINK2,165),width=4)
    d.polygon([(755,500),(1010,520),(1080,790),(720,760)],fill=(13,6,23,150))
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(1)))

def footer(img):
    d=ImageDraw.Draw(img)
    d.text((48,1294),"占いは判断材料のひとつ。大きな判断は現実の条件も確認してください。",font=font(FONT_REG,16),fill=(153,135,157))

def cover(img,text):
    luxe_silhouette(img)
    d=ImageDraw.Draw(img)
    d.text((54,185),"NIGHT WORK",font=font(FONT_BOLD,24),fill=GOLD)
    d.text((54,216),"REAL TALK",font=font(FONT_BOLD,18),fill=PINK2)
    centered_lines(img,text,335,950,84,17)
    # Hot lower strap.
    box=(58,1022,1022,1168)
    glow_shape(img,box,PINK,38,4)
    d.rounded_rectangle(box,38,fill=(35,5,31,225))
    d.text((110,1053),"売上だけじゃなく、消耗まで見る。",font=font(FONT_BOLD,34),fill=WHITE)
    d.text((110,1104),"保存して、しんどい日に見返す。",font=font(FONT_REG,26),fill=GOLD2)

def inner(img,text,n):
    d=ImageDraw.Draw(img)
    labels={2:"WHY",3:"CHECK",4:"SORT",5:"NEXT"}; d.text((54,182),labels[n],font=font(FONT_BOLD,26),fill=PINK2)
    # Large ornamental number.
    glow_text(img,(725,120),f"0{n-1}",font(FONT_BOLD,155),(*GOLD2,),PINK,2)
    # Main black glass panel with neon border.
    box=(54,310,1026,1040)
    g=Image.new("RGBA",img.size,(0,0,0,0)); gd=ImageDraw.Draw(g)
    gd.rounded_rectangle(box,40,fill=(7,4,15,215),outline=(*GOLD,220),width=3)
    img.alpha_composite(g)
    glow_shape(img,box,PINK if n in (3,5) else GOLD,40,3)

    f=font(FONT_BOLD,62)
    lines=wrap(d,text,f,820)
    total=len(lines)*84
    y=max(400,655-total//2)
    for i,line in enumerate(lines):
        b=d.textbbox((0,0),line,font=f); x=(W-(b[2]-b[0]))//2
        if i==0 or any(k in line for k in ["売上","消耗","移籍","自分","店","保存"]):
            glow_text(img,(x,y+i*84),line,f,GOLD2 if i%2==0 else WHITE,PINK,2)
        else:
            d.text((x,y+i*84),line,font=f,fill=WHITE,stroke_width=1,stroke_fill=(30,3,30))

    if n==5:
        box2=(140,1090,940,1182)
        glow_shape(img,box2,GOLD,34,3)
        d.rounded_rectangle(box2,34,fill=(25,5,29,245))
        d.text((205,1117),"保存  →  プロフィールから個別に",font=font(FONT_BOLD,27),fill=WHITE)

def render(text,n,out):
    seed=sum(str(out).encode("utf-8"))
    img=base(seed); brand(img,n)
    if n==1: cover(img,text)
    else: inner(img,text,n)
    footer(img)
    out.parent.mkdir(parents=True,exist_ok=True)
    img.convert("RGB").save(out,"PNG",optimize=True)

def main():
    posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
    for p in posts:
        if len(p["slides"])!=5: raise ValueError(f"{p['date']}: five slides required")
        for i,t in enumerate(p["slides"],1): render(t,i,OUT/p["date"]/f"{i:02d}.png")
        print(f"rendered {p['date']} loud_luxe_v2")
if __name__=="__main__": main()
