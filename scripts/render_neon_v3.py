"""ELEPHAN: Oct-17-winning editorial look, amplified for vertical carousels.
Adult women in glamorous, low-cut party dresses; no nudity. Matching bold
Japanese display font, white text, neon-pink outlines and handwritten strokes.
All five slides vary by day using posts.json. No text baked in source portraits.
"""
from pathlib import Path
from datetime import date
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import json, math, random

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"generated"/"2026-10-17-revised"
DEST=ROOT/"generated"/"neon-v3"
W,H=1080,1350
BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
REG="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
PINK=(255,8,150)
WHITE=(255,250,253)
GOLD=(255,208,83)
DEEP=(23,1,17)

def font(size,regular=False):
    return ImageFont.truetype(REG if regular else BOLD,size)

def normalize(text):
    return str(text).replace("\r","").strip()

def wrap(text,draw,ff,maxw):
    result=[]
    for item in normalize(text).split("\n"):
        if not item:continue
        line=""
        for c in item:
            cand=line+c
            if draw.textbbox((0,0),cand,font=ff)[2]<=maxw:
                line=cand
            else:
                if line:result.append(line)
                line=c
        if line:result.append(line)
    return result

def headline(im,text,x,y,maxwidth=700,maxheight=725,start=107,minimum=52):
    d=ImageDraw.Draw(im)
    for sz in range(start,minimum-1,-2):
        lines=wrap(text,d,font(sz),maxwidth)
        leading=int(sz*1.22)
        if len(lines)*leading<=maxheight:
            break
    # Pink neon shadow, bold white letters, hot-pink edge -- based on the
    # highest-viewed Oct 17 approved slide rather than weak thin serif.
    for i,line in enumerate(lines):
        yy=y+i*leading
        accent=(i==len(lines)-1)
        glow=Image.new("RGBA",(W,H),(0,0,0,0))
        gd=ImageDraw.Draw(glow)
        gd.text((x,yy),line,font=font(sz),fill=(*PINK,255),
                stroke_width=12,stroke_fill=(*PINK,240))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
        d=ImageDraw.Draw(im)
        # dark extrusion provides strong contrast on photo background
        for ex,ey in [(5,7),(4,5)]:
            d.text((x+ex,yy+ey),line,font=font(sz),
                   fill=(25,0,24),stroke_width=10,stroke_fill=(25,0,24))
        d.text((x,yy),line,font=font(sz),
               fill=PINK if accent else WHITE,
               stroke_width=5,stroke_fill=WHITE if accent else PINK)
        if accent:
            brush(im,x,yy+sz+12,min(710,x+maxwidth-20))
    return y+len(lines)*leading

def brush(im,x,y,x2):
    strokes=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(strokes)
    points=[(round(x+(x2-x)*j/45),round(y+6*math.sin(j*.34))) for j in range(46)]
    d.line(points,fill=(*PINK,240),width=15)
    im.alpha_composite(strokes.filter(ImageFilter.GaussianBlur(13)))
    ImageDraw.Draw(im).line(points,fill=(255,55,183),width=7)

def portraits():
    # Cropped away text from the approved original images; retain adult
    # hostess faces and festive dresses rather than reusing old headlines.
    a=Image.open(SRC/"01.jpg").convert("RGB").crop((710,157,1054,1216))
    b=Image.open(SRC/"02.jpg").convert("RGB").crop((649,150,1050,1045))
    return [a,b]

def background(seed):
    rng=random.Random(seed)
    base=Image.new("RGB",(W,H),(28,1,24)).convert("RGBA")
    wash=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(wash)
    d.ellipse((-400,-300,800,1000),fill=(123,0,69,215))
    d.ellipse((550,-300,1550,690),fill=(149,24,103,185))
    d.ellipse((-250,700,900,1750),fill=(95,5,53,150))
    for i in range(55):
        x=rng.randrange(-80,W+80);y=rng.randrange(-50,H+50);r=rng.randrange(6,52)
        c=rng.choice([(255,16,147,150),(255,183,77,155),
                      (255,54,182,180),(245,224,245,100)])
        d.ellipse((x-r,y-r,x+r,y+r),fill=c)
    base.alpha_composite(wash.filter(ImageFilter.GaussianBlur(30)))
    d=ImageDraw.Draw(base)
    # Editorial hot pink frame associated with the winning image
    d.rectangle((8,8,W-9,H-9),outline=(255,16,155),width=11)
    return base

def apply_portrait(im,img,*,slide):
    # Big photo on right, preserving face and shoulders/décolletage in frame.
    width,height=715,1130
    photo=ImageOps.fit(img,(width,height),Image.Resampling.LANCZOS,centering=(0.5,.46))
    photo=ImageEnhance.Contrast(photo).enhance(1.08)
    photo=ImageEnhance.Color(photo).enhance(1.25).convert("RGBA")
    mask=Image.new("L",(width,height))
    # horizontal fade keeping the model clear on the right
    grad=Image.linear_gradient("L").rotate(90,expand=True)
    grad=grad.resize((width,height))
    mask=grad.point(lambda x: min(255,int(x*1.65)))
    # lower corners fade subtly into nightclub color
    upper=Image.linear_gradient("L").resize((width,height))
    alpha=Image.new("L",(width,height),255)
    # mask only the left edge; dark overlay will support text readability
    mask=mask.filter(ImageFilter.GaussianBlur(27))
    im.paste(photo,(W-width-12,95),mask)
    # strong left-to-right fade; text floats above portrait
    dark=Image.new("RGBA",(W,H),(0,0,0,0))
    dd=ImageDraw.Draw(dark)
    for x in range(0,750,5):
        opacity=int(225*(1-x/780)**1.65)
        dd.rectangle((x,70,x+5,H-45),fill=(18,1,18,opacity))
    im.alpha_composite(dark)
    # brighten glitter lower frame
    d=ImageDraw.Draw(im)
    for x,y,r in [(995,160,6),(750,1080,10),(930,1165,8),(660,138,6)]:
        d.line((x-r,y,x+r,y),fill=GOLD,width=3)
        d.line((x,y-r,x,y+r),fill=GOLD,width=3)

def badge(im,n):
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((919,47,1053,116),34,fill=(23,0,25,229),outline=GOLD,width=3)
    d.text((943,59),f"{n}/5",font=font(35),fill=WHITE)
    d.text((51,42),"E L E P H A N",font=font(30),fill=GOLD)
    d.text((52,88),"夜職の仕事運・金運",font=font(24),fill=WHITE)

def capsule(im,text):
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((48,1110,793,1202),20,fill=(250,3,134,243),outline=GOLD,width=3)
    ff=font(33)
    usable=650
    while d.textbbox((0,0),text,font=ff)[2]>usable:
        ff=font(ff.size-1)
    d.text((81,1132),text,font=ff,fill=WHITE,stroke_width=1,stroke_fill=(82,0,48))

def card(im,txt,y):
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((43,y,766,y+78),15,fill=(10,0,21,215),outline=(255,92,175),width=2)
    d.text((73,y+17),txt,font=font(27),fill=WHITE)

def render(item,n,images):
    day=item["date"]
    stamp=date.fromisoformat(day).toordinal()
    base=background(stamp*17+n*159)
    # alternate adult glamour photography; every frame visibly includes model
    woman=images[(stamp+n)%len(images)]
    apply_portrait(base,woman,slide=n)
    badge(base,n)
    if n==1:
        end=headline(base,item["slides"][0],50,185,maxwidth=736,maxheight=770,start=111,minimum=63)
        # Distinct hero text + bright accent with no cramped paragraph
        card(base,"その悩み、ひとりで抱えないで。",1000)
    elif n<5:
        d=ImageDraw.Draw(base)
        d.text((57,162),f"CHECK 0{n-1}",font=font(47),fill=GOLD,
               stroke_width=2,stroke_fill=(42,1,22))
        headline(base,item["slides"][n-1],50,282,maxwidth=719,maxheight=700,start=106,minimum=60)
        card(base,"こんな時、あなたならどうする？",1000)
    else:
        d=ImageDraw.Draw(base)
        d.text((55,156),"LAST CHECK",font=font(48),fill=GOLD,
               stroke_width=2,stroke_fill=(35,0,15))
        headline(base,item["slides"][4],48,291,maxwidth=722,maxheight=660,start=93,minimum=56)
        capsule(base,"保存して、出勤前に見返す")
    d=ImageDraw.Draw(base)
    d.text((55,1261),"NIGHT WORK  /  ELEPHAN",font=font(24),fill=WHITE)
    return base.convert("RGB")

def main():
    posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
    photos=portraits()
    for item in posts:
        day=item["date"]
        if day<"2026-10-25":continue
        if len(item["slides"])!=5:raise ValueError("Need 5 unique slides "+day)
        output=DEST/day;output.mkdir(parents=True,exist_ok=True)
        for n in range(1,6):
            result=render(item,n,photos)
            path=output/f"{n:02d}.jpg"
            result.save(path,quality=92,optimize=True,subsampling=0)
            if path.stat().st_size<55000:raise RuntimeError("Invalid render "+str(path))
        print(f"NEON-V3 {day} verified 5/5",flush=True)
if __name__=="__main__":main()
