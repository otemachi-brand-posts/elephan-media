"""ELEPHAN 2026-10-17 classic design restored: neon handwriting + expressive
Japanese display lettering, nightclub bokeh, individualized layouts per slide.
Runs daily from posts.json. Adult glamorous fashion, fully dressed.
Fonts are OFL-licensed from google/fonts, downloaded by GitHub Actions.
"""
from datetime import date
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import math, random, json

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"generated"/"2026-10-17-revised"
DEST=ROOT/"generated"/"classic-v2"
W,H=1080,1350
HAND="/usr/local/share/fonts/elephan/ZenKurenaido-Regular.ttf"
DISPLAY="/usr/local/share/fonts/elephan/KaiseiDecol-Bold.ttf"
NOTO="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
NOTO_SERIF="/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
WHITE=(255,252,249)
HOT=(255,25,157)
PINK=(255,87,187)
GOLD=(250,198,95)
DARK=(20,2,20)

def font(size,kind="display"):
    path=HAND if kind=="hand" else DISPLAY if kind=="display" else NOTO
    if not Path(path).is_file():path=NOTO_SERIF if kind!="sans" else NOTO
    return ImageFont.truetype(path,size)

def lines_for(text,im,max_width,max_height,largest=110,smallest=49,kind="display"):
    drawing=ImageDraw.Draw(im)
    explicit=[z.strip() for z in str(text).split("\n") if z.strip()]
    if not explicit:return [],font(largest,kind),largest
    for size in range(largest,smallest-1,-2):
        f=font(size,kind)
        if all(drawing.textbbox((0,0),z,font=f)[2] <= max_width for z in explicit) and len(explicit)*int(size*1.35)<=max_height:
            return explicit,f,size
    # Only when authored hard breaks cannot fit: split at balanced Japanese chars.
    size=smallest;f=font(size,kind)
    result=[]
    for segment in explicit:
        chunk=""
        for ch in segment:
            if chunk and drawing.textbbox((0,0),chunk+ch,font=f)[2]>max_width:
                result.append(chunk);chunk=ch
            else:chunk+=ch
        if chunk:result.append(chunk)
    return result,f,size

def glow_text(im,xy,s,size,kind="hand",color=HOT,center=False,stroke=2,blur=14):
    x,y=xy; ff=font(size,kind)
    d=ImageDraw.Draw(im)
    textwidth=d.textbbox((0,0),s,font=ff)[2]
    if center:x-=textwidth//2
    halo=Image.new("RGBA",(W,H),(0,0,0,0));hd=ImageDraw.Draw(halo)
    hd.text((x,y),s,font=ff,fill=(*color,255),stroke_width=8,stroke_fill=(*color,240))
    im.alpha_composite(halo.filter(ImageFilter.GaussianBlur(blur)))
    d=ImageDraw.Draw(im)
    d.text((x+3,y+5),s,font=ff,fill=(13,2,15),stroke_width=6,stroke_fill=(13,2,15))
    d.text((x,y),s,font=ff,fill=color,stroke_width=stroke,stroke_fill=WHITE)
    return textwidth

def white_text(im,xy,s,size,kind="display",stroke=3):
    x,y=xy;ff=font(size,kind)
    d=ImageDraw.Draw(im)
    d.text((x+4,y+6),s,font=ff,fill=(4,1,8),stroke_width=stroke+4,stroke_fill=(4,1,8))
    d.text((x,y),s,font=ff,fill=WHITE,stroke_width=stroke,stroke_fill=(19,1,20))
    return d.textbbox((0,0),s,font=ff)[2]

def scribble(im,y,x=41,x2=685):
    layer=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    pts=[(x+round((x2-x)*k/48),y+round(6*math.sin(k*.38))) for k in range(49)]
    d.line(pts,fill=(*HOT,255),width=13)
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(11)))
    ImageDraw.Draw(im).line(pts,fill=PINK,width=5)

def photograph_sources():
    # Crop ONLY the original approved adult evening-wear photographs,
    # excluding the baked-in 1/5 and 2/5 counters in their upper-right corners.
    # avoiding baked-in old text, boxes and branding.
    raw=[Image.open(SOURCE/f"{n:02d}.jpg").convert("RGB") for n in range(1,6)]
    return [
        raw[0].crop((670,205,1075,1196)), # champagne dress; no old lettering
        raw[1].crop((638,205,1075,1055)), # black lace dress; no old lettering
        raw[3].crop((22,312,415,758))    # red cocktail dress; no old lettering
    ]

def backdrop(seed,photo):
    rng=random.Random(seed)
    # Nightclub: blurred champagne/pink lights rather than flat magenta.
    ambient=ImageOps.fit(photo,(W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(65))
    ambient=ImageEnhance.Color(ambient).enhance(1.4).convert("RGBA")
    ambient.alpha_composite(Image.new("RGBA",(W,H),(17,0,13,145)))
    light=Image.new("RGBA",(W,H),(0,0,0,0));ld=ImageDraw.Draw(light)
    ld.ellipse((-370,-160,540,940),fill=(163,3,86,160))
    ld.ellipse((770,-210,1440,790),fill=(215,42,117,100))
    for i in range(40):
        x=rng.randint(-60,W+60);y=rng.randint(70,H-20);r=rng.randrange(5,35)
        c=rng.choice([(250,187,93,135),(255,21,161,135),(255,210,211,110),(179,13,140,120)])
        ld.ellipse((x-r,y-r,x+r,y+r),fill=c)
    ambient.alpha_composite(light.filter(ImageFilter.GaussianBlur(26)))
    return ambient

def apply_model(im,source,x=340,y=155,w=755,h=1040):
    photo=ImageOps.fit(source,(w,h),Image.Resampling.LANCZOS,centering=(0.53,0.47)).convert("RGBA")
    photo=ImageEnhance.Color(photo).enhance(1.15)
    # Feather the left edge to restore the flowing photographic composition.
    mask=Image.new("L",(w,h),0);d=ImageDraw.Draw(mask)
    for i in range(w):
        alpha=round(255*min(1,max(0,(i-12)/200)))
        d.line((i,0,i,h),fill=alpha)
    mask=mask.filter(ImageFilter.GaussianBlur(19))
    im.paste(photo,(x,y),mask)
    shade=Image.new("RGBA",(W,H),(0,0,0,0));sd=ImageDraw.Draw(shade)
    for xx in range(0,660,4):
        alpha=int(175*(1-xx/670)**1.4)
        sd.rectangle((xx,120,xx+4,H-105),fill=(10,1,17,alpha))
    im.alpha_composite(shade)

def furniture(im,n):
    d=ImageDraw.Draw(im)
    d.rectangle((6,6,1074,1344),outline=HOT,width=7)
    d.rectangle((13,13,1067,147),fill=(14,0,16,230))
    d.rectangle((13,1250,1067,1330),fill=(14,0,16,210))
    white_text(im,(958,117),f"{n}/5",40,kind="display",stroke=1)
    white_text(im,(36,1200),"E L E P H A N",28,kind="display",stroke=1)
    white_text(im,(37,1239),"夜職の仕事運・金運",20,kind="sans",stroke=1)

def gold_sparkle(im,x,y):
    d=ImageDraw.Draw(im)
    d.line((x-12,y,x+12,y),fill=GOLD,width=3)
    d.line((x,y-12,x,y+12),fill=GOLD,width=3)

def headline(im,txt,y=300,x=40,maxw=735,maxh=600,start=105):
    lines,ff,size=lines_for(txt,im,maxw,maxh,start,46,"display")
    pos=y
    for i,s in enumerate(lines):
        if i%2:
            # Warm hand-lettered neon pink, close to the original October 17.
            glow_text(im,(x,pos),s,min(size+5,111),kind="hand",blur=16)
        else:
            white_text(im,(x,pos),s,size,"display",stroke=2)
        pos+=int(size*1.36)
    scribble(im,min(1130,pos+8),x,max(x+170,min(760,x+maxw)))
    return pos

def dark_panel(im,box,alpha=215):
    d=ImageDraw.Draw(im)
    d.rounded_rectangle(box,18,fill=(15,2,18,alpha),outline=(242,116,187,230),width=3)

def mini_sentences(text):
    # Do not introduce new claims; use original caption opening.
    text=str(text).replace("\n","").replace("。","。 ")
    words=[s.strip() for s in text.split("。") if s.strip()]
    return [s[:36] for s in words[:2]]

# Keep the portrait face in a separate right-hand photo column; text stays left.
def slide1(post,img,seed):
    im=backdrop(seed,img);apply_model(im,img,x=620,y=150,w=465,h=1060)
    glow_text(im,(50,190),"今夜のホンネ…",56,kind="hand")
    headline(im,post["slides"][0],y=286,maxw=545,maxh=580,start=88)
    white_text(im,(57,1101),"これ、私のことかも…？",35,"hand",1)
    furniture(im,1)
    gold_sparkle(im,730,275)
    return im.convert("RGB")

def slide2(post,img,seed):
    im=backdrop(seed,img);apply_model(im,img,x=650,y=190,w=435,h=1025)
    white_text(im,(38,192),"こんな状態",82)
    glow_text(im,(42,283),"当てはまる？",77,"hand")
    scribble(im,389,48,708)
    dark_panel(im,(33,456,780,970),225)
    d=ImageDraw.Draw(im)
    words=[q.strip() for q in post["slides"][1].split("\n") if q.strip()]
    for i,s in enumerate(words[:4]):
        yy=500+i*106
        d.rectangle((68,yy+14,111,yy+57),outline=HOT,width=5)
        d.line((75,yy+34,87,yy+49,116,yy+7),fill=PINK,width=6)
        size=58
        while ImageDraw.Draw(im).textbbox((0,0),s,font=font(size,"display"))[2]>600 and size>38:size-=2
        white_text(im,(140,yy),s,size,stroke=1)
    if len(words)<3:
        caption=mini_sentences(post.get("caption",""))
        for k,s in enumerate(caption[:3-len(words)]):
            yy=500+(len(words)+k)*106
            d.rectangle((68,yy+14,111,yy+57),outline=HOT,width=5)
            d.line((75,yy+34,87,yy+49,116,yy+7),fill=PINK,width=6)
            f=font(34,"sans")
            display=s
            while d.textbbox((0,0),display,font=f)[2]>590 and len(display)>4: display=display[:-1]
            white_text(im,(140,yy+7),display,34,"sans",stroke=1)
    glow_text(im,(160,1070),"無理してない？",60,"hand")
    furniture(im,2)
    gold_sparkle(im,770,180)
    return im.convert("RGB")

def slide3(post,img,seed):
    im=backdrop(seed,img)
    apply_model(im,img,x=620,y=175,w=465,h=1010)
    white_text(im,(72,181),"今、見るべきこと",73)
    headline(im,post["slides"][2],y=300,maxw=545,maxh=470,start=80)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((37,870,788,1079),22,fill=(15,1,19,220),outline=GOLD,width=3)
    white_text(im,(74,892),"気になるところを",42,"display",1)
    glow_text(im,(75,965),"ひとつ、整理しよう。",47,"hand",blur=11)
    furniture(im,3)
    gold_sparkle(im,838,960)
    return im.convert("RGB")

def slide4(post,img,seed):
    im=backdrop(seed,img)
    # Original Oct17 layout: a large visible fashion portrait and a concise
    # semi-transparent checklist area, not a blank giant black rectangle.
    apply_model(im,img,x=0,y=275,w=515,h=890)
    glow_text(im,(415,169),"見逃さないで…",61,"hand")
    dark_panel(im,(526,386,1038,876),200)
    txt=post["slides"][3]
    lines,_,size=lines_for(txt,im,435,365,70,41,"display")
    yy=458
    for k,line in enumerate(lines):
        if k%2==0:white_text(im,(547,yy),line,size,"display",1)
        else:glow_text(im,(547,yy),line,size,"hand",blur=9)
        yy+=int(size*1.43)
    scribble(im,min(842,yy+21),545,995)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((47,1058,1030,1164),22,fill=(18,0,22,208),outline=GOLD,width=3)
    glow_text(im,(66,1085),"今の状況、見直してみる？",37,"hand",blur=8)
    furniture(im,4)
    return im.convert("RGB")

def slide5(post,img,seed):
    im=backdrop(seed,img)
    apply_model(im,img,x=680,y=177,w=405,h=1005)
    white_text(im,(51,190),"これから、どうする？",57,"display",2)
    dark_panel(im,(42,356,754,913),194)
    headline(im,post["slides"][4],y=411,x=65,maxw=635,maxh=410,start=74)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((70,997,1010,1127),35,fill=(251,22,148,248),outline=GOLD,width=3)
    white_text(im,(139,1032),"保存して、あとで見返す",37,"sans",stroke=1)
    furniture(im,5)
    return im.convert("RGB")

def main():
    posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
    sources=photograph_sources()
    functions=[slide1,slide2,slide3,slide4,slide5]
    for p in posts:
        day=p["date"]
        if day<"2026-11-01":continue
        if len(p["slides"])!=5:raise ValueError("5 slides required "+day)
        o=DEST/day;o.mkdir(parents=True,exist_ok=True)
        for n,fun in enumerate(functions,1):
            img=sources[(date.fromisoformat(day).toordinal()+n)%len(sources)]
            result=fun(p,img,date.fromisoformat(day).toordinal()+n*137)
            path=o/f"{n:02d}.jpg"
            result.save(path,quality=92,optimize=True,subsampling=0)
            if path.stat().st_size<75000:raise RuntimeError("Render suspiciously small "+str(path))
        print("CLASSIC-V2",day,"5/5",flush=True)
if __name__=="__main__":main()
