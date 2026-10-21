"""ELEPHAN neon-magazine carousel. Approved vivid pink night-club direction.
The photographic subjects come from the user-approved Oct 17 revised media.
Change copy daily from posts.json; avoid baking old copy into future panels.
"""
from pathlib import Path
from datetime import date
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import json, math, random

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"generated"/"2026-10-17-revised"
DEST=ROOT/"generated"/"neon-v2"
W,H=1080,1350
BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SERIF="/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
REG="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
PINK=(255,19,154); LIGHT=(255,219,239); WHITE=(255,252,254); GOLD=(244,192,76)

def font(n,serif=False):
    return ImageFont.truetype(SERIF if serif else BOLD,n)

def wrap(draw,txt,ff,maxw):
    out=[]
    for block in txt.replace("\r","").split("\n"):
        if not block:continue
        line=""
        for ch in block:
            candidate=line+ch
            if draw.textbbox((0,0),candidate,font=ff)[2]<=maxw:
                line=candidate
            else:
                if line:out.append(line)
                line=ch
        if line:out.append(line)
    return out

def neon(im,pos,txt,size,fill=PINK,outer=19,stroke=4,serif=False):
    layer=Image.new("RGBA",(W,H),(0,0,0,0))
    ld=ImageDraw.Draw(layer)
    ld.text(pos,txt,font=font(size,serif),fill=(*fill,235),
            stroke_width=outer//3,stroke_fill=(*PINK,200))
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(outer)))
    ImageDraw.Draw(im).text(pos,txt,font=font(size,serif),fill=fill,
        stroke_width=stroke,stroke_fill=(65,2,35))

def handwritten_line(im,x,y,x2):
    ld=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(ld)
    pts=[(x+(x2-x)*k/35,y+6*math.sin(k*.51)) for k in range(36)]
    d.line(pts,fill=(*PINK,230),width=13)
    im.alpha_composite(ld.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(im).line(pts,fill=PINK,width=5)

def source_images():
    imgs=[]
    for n,crop in [(1,(714,222,1049,1116)),(2,(648,210,1049,1090))]:
        src=Image.open(SRC/f"{n:02d}.jpg").convert("RGB")
        # Crops deliberately exclude almost all of the old text.
        imgs.append(src.crop(crop))
    return imgs

def cover_photo(source):
    sw,sh=source.size; sc=max(680/sw,1230/sh)
    re=source.resize((round(sw*sc),round(sh*sc)),Image.Resampling.LANCZOS)
    x=(re.width-680)//2; y=max(0,(re.height-1230)//2)
    return re.crop((x,y,x+680,y+1230)).convert("RGBA")

def make_background(photo,seed):
    base=photo.resize((W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(55))
    base=ImageEnhance.Color(base).enhance(1.7).convert("RGBA")
    base.alpha_composite(Image.new("RGBA",(W,H),(42,1,26,118)))
    # Neon lighting and champagne highlights in the club background.
    effects=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(effects)
    rand=random.Random(seed)
    for _ in range(23):
        x=rand.randrange(0,W);y=rand.randrange(0,H)
        r=rand.randrange(15,85)
        col=(255,rand.choice([35,60,95,180]),rand.choice([130,200,245]),rand.randrange(60,145))
        d.ellipse((x-r,y-r,x+r,y+r),fill=col)
    for x in [80,255,785,985]:
        d.line((x,0,x+35,H),fill=(255,11,147,68),width=16)
    base.alpha_composite(effects.filter(ImageFilter.GaussianBlur(23)))
    return base

def apply_photo(im,src):
    p=cover_photo(src)
    # Smooth blended edge, full impact model on right and large readable headline on left.
    mask=Image.new("L",p.size)
    md=ImageDraw.Draw(mask)
    for x in range(p.width):
        amount=round(255*min(1,max(0,(x-12)/165)))
        md.line((x,0,x,p.height),fill=amount,width=1)
    # Soften photo's top and bottom edges.
    mask=mask.filter(ImageFilter.GaussianBlur(30))
    im.paste(p,(W-680,64),mask)
    shade=Image.new("RGBA",(W,H),(0,0,0,0));px=shade.load()
    for x in range(W):
        alpha=round(205*(1-x/W)**2.1)
        for y in range(H):
            px[x,y]=(14,1,20,alpha)
    im.alpha_composite(shade)

def branding(im,n):
    d=ImageDraw.Draw(im)
    d.ellipse((37,1231,97,1291),outline=GOLD,width=4)
    d.arc((50,1241,88,1283),20,300,fill=GOLD,width=4)
    d.text((120,1231),"E L E P H A N",font=font(30,True),fill=WHITE)
    d.text((125,1272),"夜職の仕事運・金運",font=ImageFont.truetype(REG,19),fill=WHITE)
    d.rounded_rectangle((931,27,1060,86),29,fill=(12,5,16,219),outline=(210,160,188),width=2)
    d.text((957,39),f"{n}/5",font=font(33,True),fill=WHITE)

def fit_lines(im,txt,*,x=51,y=145,width=690,maxh=800,base=101,small=46,highlight=True):
    d=ImageDraw.Draw(im)
    for size in range(base,small-1,-3):
        ff=font(size,True);ll=wrap(d,txt,ff,width)
        leading=int(size*1.27)
        if len(ll)*leading<=maxh:break
    yy=y
    for i,line in enumerate(ll):
        col=PINK if highlight and i==len(ll)-1 else WHITE
        neon(im,(x,yy),line,size,col,outer=18 if col==PINK else 5,stroke=3,serif=True)
        yy+=leading
    return yy

def micro(im,txt,y):
    d=ImageDraw.Draw(im)
    ff=font(29)
    li=wrap(d,txt,ff,660)
    for i,s in enumerate(li[:3]):
        neon(im,(66,y+i*46),s,29,LIGHT,outer=7,stroke=1)

def render(post,n,portrait,seed):
    im=make_background(portrait,seed+n*13)
    apply_photo(im,portrait)
    title=post["slides"][n-1]
    if n==1:
        end=fit_lines(im,title,x=41,y=180,width=717,maxh=750,base=101)
        handwritten_line(im,55,min(985,end+7),709)
        micro(im,"今の働き方、数字と気持ちで見直す。",y=1099)
    elif n==2:
        neon(im,(47,140),"まず整理したい",65,PINK,outer=22,serif=True)
        end=fit_lines(im,title,x=47,y=270,width=695,maxh=680,base=94)
        handwritten_line(im,61,min(1030,end+12),692)
        micro(im,"いつから変わった？",1083)
    elif n==3:
        neon(im,(47,140),"数字の裏を見る",66,PINK,outer=20,serif=True)
        end=fit_lines(im,title,x=47,y=295,width=695,maxh=690,base=98)
        handwritten_line(im,51,min(1040,end+10),665)
        micro(im,"状況をひとつずつ分けて確認。",1090)
    elif n==4:
        neon(im,(45,130),"見逃したくない",64,PINK,outer=22,serif=True)
        end=fit_lines(im,title,x=47,y=278,width=689,maxh=730,base=89)
        handwritten_line(im,55,min(1035,end+12),685)
        micro(im,"自分がどう感じたかも大切。",1085)
    else:
        neon(im,(48,145),"これからのために",67,PINK,outer=24,serif=True)
        end=fit_lines(im,title,x=51,y=307,width=687,maxh=740,base=81)
        handwritten_line(im,55,min(1032,end+12),673)
        d=ImageDraw.Draw(im)
        d.rounded_rectangle((52,1080,768,1185),20,fill=(255,12,149,218),outline=GOLD,width=3)
        cta="プロフィールのLINEへ" if "プロフィール" in title or "鑑定" in title else "保存して、あとで見返す"
        d.text((75,1110),cta,font=font(39),fill=WHITE)
    branding(im,n)
    return im.convert("RGB")

def main():
    posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
    models=source_images()
    for post in posts:
        day=post["date"]
        if day<"2026-10-21":continue
        if len(post["slides"])!=5:raise ValueError("Invalid five-slide data")
        dest=DEST/day
        dest.mkdir(parents=True,exist_ok=True)
        model=models[date.fromisoformat(day).toordinal()%len(models)]
        for n in range(1,6):
            im=render(post,n,model,date.fromisoformat(day).toordinal())
            out=dest/f"{n:02d}.jpg"
            im.save(out,format="JPEG",quality=91,optimize=True,subsampling=0)
            if out.stat().st_size<35000:raise RuntimeError("Invalid JPEG "+str(out))
        print("NEON-V2",day,"5/5",flush=True)

if __name__=="__main__":
    main()
