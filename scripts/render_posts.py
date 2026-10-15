"""Render ELEPHAN Instagram slides in a vivid premium-night visual system."""
import json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"generated"
W,H=1080,1350
FONT_BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

NAVY=(7,8,30); PURPLE=(35,13,65); PINK=(255,48,154); CYAN=(39,224,255)
GOLD=(239,190,76); IVORY=(255,247,235); MUTED=(206,196,218)

def font(path,size): return ImageFont.truetype(path,size=size)

def wrap(draw,text,fnt,maxw):
    out=[]
    for block in text.split("\n"):
        if not block: out.append(""); continue
        cur=""
        for ch in block:
            test=cur+ch
            if draw.textbbox((0,0),test,font=fnt)[2] <= maxw: cur=test
            else:
                if cur: out.append(cur)
                cur=ch
        if cur: out.append(cur)
    return out

def gradient():
    img=Image.new("RGB",(W,H))
    px=img.load()
    for y in range(H):
        t=y/(H-1)
        for x in range(W):
            sx=x/(W-1)
            r=int(NAVY[0]*(1-t)+PURPLE[0]*t + 18*math.sin(sx*math.pi)*t)
            g=int(NAVY[1]*(1-t)+PURPLE[1]*t)
            b=int(NAVY[2]*(1-t)+PURPLE[2]*t + 16*sx)
            px[x,y]=(max(0,min(r,255)),max(0,min(g,255)),max(0,min(b,255)))
    return img

def glow_text(base,pos,text,fnt,fill,glow):
    layer=Image.new("RGBA",base.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    d.text(pos,text,font=fnt,fill=(*glow,235),stroke_width=4,stroke_fill=(*glow,210))
    layer=layer.filter(ImageFilter.GaussianBlur(16))
    base.alpha_composite(layer)
    ImageDraw.Draw(base).text(pos,text,font=fnt,fill=fill,stroke_width=1,stroke_fill=(255,255,255,40))

def draw_lines(base,text,y,size=72,maxw=900,accent=False):
    d=ImageDraw.Draw(base); f=font(FONT_BOLD,size); lines=wrap(d,text,f,maxw)
    for i,line in enumerate(lines):
        box=d.textbbox((0,0),line,font=f); x=(W-(box[2]-box[0]))//2
        if accent and i==len(lines)-1:
            glow_text(base,(x,y+i*(size+22)),line,f,IVORY,PINK)
        else:
            d.text((x,y+i*(size+22)),line,font=f,fill=IVORY)
    return y+len(lines)*(size+22)

def elephant(draw,x,y,s=1.0):
    w=int(4*s)
    draw.ellipse((x,y,x+54*s,y+54*s),outline=GOLD,width=w)
    draw.arc((x+14*s,y+11*s,x+47*s,y+48*s),25,310,fill=GOLD,width=w)
    draw.ellipse((x+38*s,y+20*s,x+44*s,y+26*s),fill=GOLD)

def decorations(img,seed):
    rnd=random.Random(seed); d=ImageDraw.Draw(img)
    for _ in range(38):
        x=rnd.randint(30,W-30); y=rnd.randint(150,H-100); r=rnd.choice([2,3,4])
        c=rnd.choice([GOLD,PINK,CYAN,(180,120,255)])
        d.ellipse((x-r,y-r,x+r,y+r),fill=c)
    # neon arcs
    for box,c in [((690,-120,1190,390),PINK),((-160,820,360,1360),CYAN)]:
        layer=Image.new("RGBA",img.size,(0,0,0,0)); ld=ImageDraw.Draw(layer)
        ld.arc(box,25,235,fill=(*c,210),width=8)
        blur=layer.filter(ImageFilter.GaussianBlur(18)); img.alpha_composite(blur); img.alpha_composite(layer)

def brand(img,n):
    d=ImageDraw.Draw(img); elephant(d,62,54,0.9)
    d.text((124,52),"ELEPHAN",font=font(FONT_BOLD,31),fill=IVORY)
    d.text((124,92),"夜職の仕事運・金運",font=font(FONT_REG,20),fill=MUTED)
    d.text((950,62),f"{n}/5",font=font(FONT_REG,22),fill=MUTED)

def footer(img):
    d=ImageDraw.Draw(img)
    d.text((54,1288),"占いは判断材料のひとつ。大きな判断は現実の条件も確認してください。",font=font(FONT_REG,17),fill=(160,151,177))

def render(text,n,out):
    img=gradient().convert("RGBA"); decorations(img,hash(str(out))&0xffffffff); brand(img,n); d=ImageDraw.Draw(img)
    if n==1:
        d.rounded_rectangle((55,205,360,265),30,fill=(255,255,255,22),outline=(*GOLD,180),width=2)
        d.text((88,220),"NIGHT WORK / SELF CHECK",font=font(FONT_BOLD,20),fill=GOLD)
        draw_lines(img,text,350,78,900,True)
        # bold luminous bottom bar
        layer=Image.new("RGBA",img.size,(0,0,0,0)); ld=ImageDraw.Draw(layer)
        ld.rounded_rectangle((70,1040,1010,1158),40,fill=(255,45,146,72),outline=(*PINK,220),width=3)
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(10))); img.alpha_composite(layer)
        d=ImageDraw.Draw(img); d.text((132,1075),"止まって、分けて、次を決める。",font=font(FONT_BOLD,31),fill=IVORY)
    else:
        tag=["CHECK","REALITY","SIGN","NEXT"][n-2]
        glow_text(img,(68,218),tag,font(FONT_BOLD,34),GOLD,PINK if n%2==0 else CYAN)
        d=ImageDraw.Draw(img)
        d.rounded_rectangle((62,305,1018,1048),46,fill=(9,10,32,185),outline=(*GOLD,150),width=2)
        draw_lines(img,text,430,62,810,True)
        if n==5:
            d.rounded_rectangle((150,1090,930,1170),38,fill=(*GOLD,220))
            d.text((250,1112),"保存 / プロフィールから個別に",font=font(FONT_BOLD,27),fill=(20,12,33))
    footer(img)
    out.parent.mkdir(parents=True,exist_ok=True); img.convert("RGB").save(out,"PNG",optimize=True)

def main():
    posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
    for p in posts:
        if len(p["slides"])!=5: raise ValueError(f"{p['date']}: five slides required")
        for i,t in enumerate(p["slides"],1): render(t,i,OUT/p["date"]/f"{i:02d}.png")
        print(f"rendered {p['date']} flash_v1")
if __name__=="__main__": main()
