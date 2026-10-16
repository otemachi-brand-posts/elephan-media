"""Render ELEPHAN Instagram slides in a loud pop-night editorial system."""
import json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"generated"
W,H=1080,1350
FONT_BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

BLACK=(8,8,14)
NAVY=(12,16,42)
PINK=(255,45,135)
MAGENTA=(207,36,255)
CYAN=(30,225,255)
ORANGE=(255,125,44)
YELLOW=(255,222,77)
CREAM=(255,248,235)
WHITE=(255,255,255)
INK=(18,20,30)
GOLD=(245,190,58)
MUTED=(106,108,122)

def font(path,size):
    return ImageFont.truetype(path,size=size)

def wrap(draw,text,fnt,maxw):
    out=[]
    for block in text.split("\n"):
        if not block:
            out.append("")
            continue
        cur=""
        for ch in block:
            test=cur+ch
            if draw.textbbox((0,0),test,font=fnt)[2] <= maxw:
                cur=test
            else:
                if cur: out.append(cur)
                cur=ch
        if cur: out.append(cur)
    return out

def elephant(draw,x,y,s=1.0,color=WHITE):
    w=max(2,int(4*s))
    draw.ellipse((x,y,x+52*s,y+52*s),outline=color,width=w)
    draw.arc((x+14*s,y+12*s,x+47*s,y+48*s),25,310,fill=color,width=w)
    draw.ellipse((x+38*s,y+20*s,x+43*s,y+25*s),fill=color)

def gradient_bg(c1,c2):
    top=Image.new("RGB",(W,H),c1)
    bottom=Image.new("RGB",(W,H),c2)
    mask=Image.linear_gradient("L").resize((W,H))
    return Image.composite(bottom,top,mask).convert("RGBA")

def add_glow(img,box,color,blur=90,alpha=150):
    layer=Image.new("RGBA",img.size,(0,0,0,0))
    d=ImageDraw.Draw(layer)
    d.ellipse(box,fill=(*color,alpha))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))

def add_halftone(img,seed,area,color,spacing=28,r=3,alpha=120):
    rnd=random.Random(seed)
    layer=Image.new("RGBA",img.size,(0,0,0,0))
    d=ImageDraw.Draw(layer)
    x0,y0,x1,y1=area
    for y in range(y0,y1,spacing):
        for x in range(x0,x1,spacing):
            rr=r+rnd.choice([0,0,1])
            d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(*color,alpha))
    img.alpha_composite(layer)

def add_starburst(img,cx,cy,r1,r2,color,n=20):
    pts=[]
    for i in range(n*2):
        a=-math.pi/2 + i*math.pi/n
        r=r2 if i%2==0 else r1
        pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r))
    ImageDraw.Draw(img).polygon(pts,fill=color)

def add_tape(img,xy,text,fill,angle=0):
    w,h=410,72
    tape=Image.new("RGBA",(w,h),(0,0,0,0))
    d=ImageDraw.Draw(tape)
    d.rounded_rectangle((0,0,w,h),18,fill=fill)
    d.text((24,16),text,font=font(FONT_BOLD,27),fill=BLACK)
    tape=tape.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    img.alpha_composite(tape,xy)

def draw_outlined_lines(img,text,x,y,size,maxw,fill,stroke,stroke_width=6,line_gap=12):
    d=ImageDraw.Draw(img)
    f=font(FONT_BOLD,size)
    lines=wrap(d,text,f,maxw)
    yy=y
    for line in lines:
        d.text((x,yy),line,font=f,fill=fill,stroke_width=stroke_width,stroke_fill=stroke)
        yy += size+line_gap
    return yy

def brand(img,n,dark=True):
    d=ImageDraw.Draw(img)
    c=WHITE if dark else INK
    elephant(d,58,46,0.8,c)
    d.text((112,44),"ELEPHAN",font=font(FONT_BOLD,29),fill=c)
    d.text((112,83),"夜職の仕事運・金運",font=font(FONT_REG,18),fill=c if dark else MUTED)
    d.rounded_rectangle((932,46,1016,92),20,fill=(*BLACK,150) if dark else (255,255,255,210))
    d.text((952,55),f"{n}/5",font=font(FONT_BOLD,18),fill=WHITE if dark else INK)

def cover(text,out):
    img=gradient_bg((65,10,110),(10,10,28))
    add_glow(img,(620,-120,1200,520),PINK,100,180)
    add_glow(img,(-220,720,420,1380),CYAN,120,135)
    add_glow(img,(520,730,1180,1420),ORANGE,140,95)
    add_halftone(img,11,(700,110,1050,480),YELLOW,26,3,130)
    add_halftone(img,23,(40,930,410,1280),CYAN,30,3,95)
    brand(img,1,True)
    d=ImageDraw.Draw(img)

    add_starburst(img,870,265,85,138,(*YELLOW,240),18)
    d.text((796,218),"REAL",font=font(FONT_BOLD,34),fill=BLACK,stroke_width=1,stroke_fill=BLACK)

    add_tape(img,(60,190),"NIGHT WORK / SELF CHECK",YELLOW,-4)

    # oversized hook with hard shadow + white face
    shadow=Image.new("RGBA",img.size,(0,0,0,0))
    sd=ImageDraw.Draw(shadow)
    f=font(FONT_BOLD,86)
    lines=wrap(sd,text,f,900)
    yy=360
    for line in lines:
        sd.text((78,yy),line,font=f,fill=(*BLACK,180),stroke_width=10,stroke_fill=(*BLACK,180))
        yy+=102
    shadow=shadow.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(shadow)
    draw_outlined_lines(img,text,58,345,86,900,WHITE,PINK,7,16)

    # bottom punchline strip
    d=ImageDraw.Draw(img)
    d.rounded_rectangle((56,1080,1024,1218),30,fill=(*BLACK,210),outline=YELLOW,width=4)
    d.text((90,1108),"売上だけ見て「合ってる店」にしない。",font=font(FONT_BOLD,34),fill=YELLOW)
    d.text((90,1161),"数字と消耗、両方で見る。",font=font(FONT_REG,24),fill=WHITE)

    out.parent.mkdir(parents=True,exist_ok=True)
    img.convert("RGB").save(out,"PNG",optimize=True)

def interior(text,n,out):
    # alternate loud palettes so the carousel has rhythm
    palettes=[
        ((255,241,95),(255,87,146),INK,BLACK),
        ((32,229,255),(85,36,185),WHITE,BLACK),
        ((255,127,47),(255,55,145),WHITE,BLACK),
        ((235,229,255),(35,16,78),INK,BLACK)
    ]
    bg1,bg2,textc,outline=palettes[n-2]
    img=gradient_bg(bg1,bg2)
    brand(img,n,dark=(n in (3,4)))
    d=ImageDraw.Draw(img)

    # giant page number
    d.text((720,170),f"0{n}",font=font(FONT_BOLD,190),fill=(*WHITE,65) if n in (3,4) else (*BLACK,45))

    # diagonal accent bars
    for k,(yy,c) in enumerate([(230,YELLOW),(270,CYAN),(310,PINK)]):
        d.polygon([(0,yy+k*4),(W,yy-42+k*4),(W,yy+10+k*4),(0,yy+52+k*4)],fill=(*c,150))

    label=["POINT","CHECK","JUDGE","NEXT"][n-2]
    add_tape(img,(58,190),label,YELLOW,-5 if n%2==0 else 5)

    # central text card with sticker outline
    card_fill=(255,255,255,220) if n in (2,5) else (8,8,20,205)
    card_text=INK if n in (2,5) else WHITE
    d.rounded_rectangle((48,370,1032,1030),42,fill=card_fill,outline=BLACK if n in (2,5) else WHITE,width=5)
    draw_outlined_lines(img,text,82,430,66,860,card_text,PINK if n in (2,5) else BLACK,3 if n in (2,5) else 5,18)

    # pop badges
    if n==2:
        add_starburst(img,870,1035,56,98,(*CYAN,255),16)
        d.text((824,1003),"別",font=font(FONT_BOLD,44),fill=BLACK)
    elif n==3:
        add_starburst(img,875,1035,62,105,(*YELLOW,255),18)
        d.text((815,1004),"2軸",font=font(FONT_BOLD,32),fill=BLACK)
    elif n==4:
        add_starburst(img,870,1030,62,110,(*CYAN,255),18)
        d.text((817,1000),"調整",font=font(FONT_BOLD,31),fill=BLACK)
    else:
        add_starburst(img,870,1028,62,110,(*YELLOW,255),18)
        d.text((814,998),"保存",font=font(FONT_BOLD,31),fill=BLACK)

    # footer ribbon
    d.rounded_rectangle((58,1160,1020,1248),25,fill=(*BLACK,225))
    footer="必要ならプロフィールから個別に整理できます。" if n==5 else "感情と数字を分けて見る。"
    d.text((86,1183),footer,font=font(FONT_BOLD,25),fill=WHITE)
    d.text((62,1290),"占いは判断材料のひとつ。大きな判断は現実の条件も確認してください。",font=font(FONT_REG,15),fill=BLACK if n in (2,5) else WHITE)

    out.parent.mkdir(parents=True,exist_ok=True)
    img.convert("RGB").save(out,"PNG",optimize=True)

def render(text,n,out):
    if n==1: cover(text,out)
    else: interior(text,n,out)

def main():
    posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
    for p in posts:
        if len(p["slides"])!=5:
            raise ValueError(f"{p['date']}: five slides required")
        for i,t in enumerate(p["slides"],1):
            render(t,i,OUT/p["date"]/f"{i:02d}.png")
        print(f"rendered {p['date']} popnight_v3")

if __name__=="__main__":
    main()
