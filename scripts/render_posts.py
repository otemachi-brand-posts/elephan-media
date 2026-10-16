"""Render ELEPHAN Instagram slides in a bold nightlife-magazine system.

Creative target: full-bleed nightlife photography, oversized Japanese copy,
hot-pink hand-drawn accents, gold/yellow labels, and dense editorial layouts.
The 2026-10-16 carousel intentionally mirrors the approved five-panel structure:
hook -> checklist -> 2x2 matrix -> three signs -> next-step checklist.
"""
import io, json, math, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"generated"
W,H=1080,1350

FONT_BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_SERIF="/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

WHITE=(255,255,255); BLACK=(6,7,12); PINK=(255,28,126)
PINK2=(255,75,167); YELLOW=(255,216,75); GOLD=(235,190,72)
CYAN=(39,214,255); MUTED=(220,216,225)

# Licensed/public Unsplash photography, fixed URLs for stable rendering.
PORTRAIT_URL="https://images.unsplash.com/photo-1773614784571-20d58c26597f?auto=format&fit=crop&w=1800&q=88"
GLASS_URL="https://images.unsplash.com/photo-1512834109963-ce6d308d7eea?auto=format&fit=crop&w=1800&q=88"
PURPLE_GLASS_URL="https://images.unsplash.com/photo-1737523644515-ec9a40bcd778?auto=format&fit=crop&w=1800&q=88"

def font(path,size):
    return ImageFont.truetype(path,size=size)

def load_remote(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=30) as resp:
        return Image.open(io.BytesIO(resp.read())).convert("RGB")

def cover_crop(im, focus_x=0.5, focus_y=0.5):
    scale=max(W/im.width,H/im.height)
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    max_x=max(0,im.width-W); max_y=max(0,im.height-H)
    x=int(max_x*min(1,max(0,focus_x))); y=int(max_y*min(1,max(0,focus_y)))
    return im.crop((x,y,x+W,y+H)).convert("RGBA")

def tint(img, rgba):
    img.alpha_composite(Image.new("RGBA",img.size,rgba))
    return img

def darken(img,alpha):
    return tint(img,(0,0,0,alpha))

def wrap(draw,text,fnt,maxw):
    out=[]
    for block in text.split("\n"):
        if not block:
            out.append("")
            continue
        cur=""
        for ch in block:
            if draw.textbbox((0,0),cur+ch,font=fnt)[2] <= maxw:
                cur+=ch
            else:
                if cur: out.append(cur)
                cur=ch
        if cur: out.append(cur)
    return out

def brand(img,n):
    d=ImageDraw.Draw(img)
    d.ellipse((38,35,88,85),outline=GOLD,width=3)
    d.arc((51,47,83,83),25,310,fill=GOLD,width=3)
    d.text((104,36),"ELEPHAN",font=font(FONT_BOLD,28),fill=WHITE)
    d.text((104,75),"夜職の仕事運・金運",font=font(FONT_REG,17),fill=WHITE)
    d.line((260,62,510,62),fill=GOLD,width=2)
    d.text((944,26),f"{n:02d}",font=font(FONT_SERIF,58),fill=WHITE)

def hand_circle(d,box):
    # Irregular pink hand-drawn circle
    x1,y1,x2,y2=box
    pts=[]
    cx=(x1+x2)/2; cy=(y1+y2)/2; rx=(x2-x1)/2; ry=(y2-y1)/2
    for i in range(80):
        a=2*math.pi*i/80
        wob=1+0.035*math.sin(i*1.7)+0.02*math.cos(i*2.4)
        pts.append((cx+rx*wob*math.cos(a),cy+ry*wob*math.sin(a)))
    d.line(pts+[pts[0]],fill=PINK,width=9,joint="curve")

def brush_word(d,xy,text,size,fill=PINK,angle=-6):
    f=font(FONT_BOLD,size)
    bbox=d.textbbox((0,0),text,font=f,stroke_width=2)
    w=bbox[2]-bbox[0]+60; h=bbox[3]-bbox[1]+60
    layer=Image.new("RGBA",(w,h),(0,0,0,0)); ld=ImageDraw.Draw(layer)
    # shadow/rough offset for pseudo-brush depth
    ld.text((30,30),text,font=f,fill=fill,stroke_width=2,stroke_fill=fill)
    layer=layer.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    return layer

def checkbox(d,x,y,text):
    d.rectangle((x,y,x+34,y+34),outline=PINK,width=3)
    d.line((x+6,y+18,x+14,y+28),fill=PINK,width=4)
    d.line((x+14,y+28,x+31,y+5),fill=PINK,width=4)
    d.text((x+54,y-4),text,font=font(FONT_BOLD,27),fill=WHITE)

def yellow_tape(img,x,y,text,w):
    d=ImageDraw.Draw(img)
    d.polygon([(x,y+12),(x+w,y),(x+w-18,y+90),(x+10,y+84)],fill=YELLOW)
    d.text((x+28,y+18),text,font=font(FONT_BOLD,32),fill=BLACK)

def glow_line(img,xy1,xy2,color=PINK,width=5):
    layer=Image.new("RGBA",img.size,(0,0,0,0))
    ld=ImageDraw.Draw(layer)
    ld.line((xy1,xy2),fill=(*color,180),width=width*3)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(img).line((xy1,xy2),fill=color,width=width)

def oct16_panel(n,out,photos):
    portrait,glass,purple=photos
    if n==1:
        # Closer to approved right-side reference: more nightlife scene visible,
        # richer bokeh, dramatic diagonal body crop, big handwritten-style accents.
        img=cover_crop(portrait,0.50,0.42)
        img=darken(img,55)
        tint(img,(90,0,45,50))
        brand(img,1)
        d=ImageDraw.Draw(img)
        hand_circle(d,(28,125,610,365))
        d.text((70,175),"売上はある。",font=font(FONT_SERIF,70),fill=WHITE)

        d.text((54,390),"でも、",font=font(FONT_SERIF,64),fill=WHITE)
        d.text((54,478),"この店にいると",font=font(FONT_SERIF,72),fill=WHITE)

        bw=brush_word(d,(0,0),"毎回",142,PINK,-7)
        img.alpha_composite(bw,(36,620))
        d=ImageDraw.Draw(img)
        d.text((86,835),"しんどい。",font=font(FONT_SERIF,118),fill=WHITE,stroke_width=1,stroke_fill=WHITE)

        d.line((44,1130,690,1130),fill=GOLD,width=2)
        d.text((46,1160),"数字だけじゃ分からない",font=font(FONT_BOLD,25),fill=WHITE)
        d.text((46,1205),"「合ってる店・合ってない店」のサイン",font=font(FONT_REG,22),fill=WHITE)
        d.text((865,1275),"SWIPE 〉",font=font(FONT_BOLD,22),fill=WHITE)

    elif n==2:
        img=cover_crop(glass,0.50,0.47)
        img=darken(img,120)
        tint(img,(55,0,10,25))
        brand(img,2)
        yellow_tape(img,58,145,"こんな状態、ありませんか？",755)
        d=ImageDraw.Draw(img)

        items=["出勤前から気が重い","売上はあるのに満たされない","お客さまに合わせすぎて疲れる","スタッフの顔色ばかり気になる","休みの日も仕事のことを考えてしまう"]
        yy=350
        for t in items:
            checkbox(d,82,yy,t); yy+=102
        d.line((70,920,1010,920),fill=WHITE,width=2)
        d.text((90,966),"ひとつでも当てはまるなら、",font=font(FONT_BOLD,28),fill=YELLOW)
        d.text((90,1015),"「頑張り方」ではなく",font=font(FONT_BOLD,28),fill=YELLOW)
        d.text((90,1064),"“店との相性”の問題かもしれません。",font=font(FONT_BOLD,28),fill=YELLOW)
        d.text((455,1248),"ELEPHAN",font=font(FONT_BOLD,21),fill=WHITE)

    elif n==3:
        img=cover_crop(purple,0.50,0.52)
        img=darken(img,165)
        brand(img,3)
        d=ImageDraw.Draw(img)
        d.text((150,120),"稼げる",font=font(FONT_SERIF,49),fill=WHITE)
        d.text((350,120),"×",font=font(FONT_BOLD,55),fill=PINK)
        d.text((415,120),"心がラク",font=font(FONT_SERIF,49),fill=WHITE)
        d.text((285,190),"が最強です。",font=font(FONT_SERIF,47),fill=WHITE)

        left,top,right,bottom=120,390,960,1055
        mx=(left+right)//2; my=(top+bottom)//2
        # 2x2 premium cards
        labels=[
            (left,top,mx,my,"A","売上はあるが\n消耗する","今の状態かも？"),
            (mx,top,right,my,"B","売上もあり\n心もラク","理想の店"),
            (left,my,mx,bottom,"C","売上も少なく\n消耗する","今すぐ見直し"),
            (mx,my,right,bottom,"D","売上は少ないが\n心はラク","一時的な避難先"),
        ]
        for x1,y1,x2,y2,k,txt,note in labels:
            d.rounded_rectangle((x1+9,y1+9,x2-9,y2-9),24,fill=(3,8,17,190),outline=PINK,width=3)
            d.text((x1+32,y1+24),k,font=font(FONT_SERIF,48),fill=WHITE)
            d.multiline_text((x1+32,y1+100),txt,font=font(FONT_BOLD,26),fill=WHITE,spacing=9)
            d.text((x1+32,y2-64),note,font=font(FONT_REG,18),fill=YELLOW)

        # axis stickers around cards
        d.rounded_rectangle((120,335,265,378),16,fill=PINK); d.text((150,342),"稼げる",font=font(FONT_BOLD,20),fill=WHITE)
        d.rounded_rectangle((815,335,960,378),16,fill=PINK); d.text((853,342),"ラク",font=font(FONT_BOLD,20),fill=WHITE)
        d.rounded_rectangle((17,687,118,733),16,fill=PINK); d.text((29,695),"しんどい",font=font(FONT_BOLD,18),fill=WHITE)
        d.rounded_rectangle((445,1067,635,1112),16,fill=PINK); d.text((480,1075),"稼げない",font=font(FONT_BOLD,18),fill=WHITE)
        d.text((458,1247),"ELEPHAN",font=font(FONT_BOLD,21),fill=WHITE)

    elif n==4:
        # Dense magazine list with photos embedded in rows, closer to approved reference.
        img=cover_crop(purple,0.50,0.56)
        img=darken(img,175)
        brand(img,4)
        d=ImageDraw.Draw(img)
        d.text((80,125),"合ってない店の",font=font(FONT_SERIF,47),fill=WHITE)
        d.text((395,180),"サイン",font=font(FONT_SERIF,44),fill=WHITE)
        bw=brush_word(d,(0,0),"3",102,PINK,-8); img.alpha_composite(bw,(670,120))
        d=ImageDraw.Draw(img)
        d.text((780,175),"つ",font=font(FONT_SERIF,44),fill=WHITE)

        rows=[
            ("1","感情がすり減る","接客中は笑っていても、\n終わるとどっと疲れる。",portrait),
            ("2","条件だけで続けてしまう","時給やバックは良い。\nでも、それ以外に魅力を感じない。",glass),
            ("3","人間関係がストレス","スタッフ・お客さま・黒服など、\n特定の人の言動に常に気を使っている。",portrait),
        ]
        yy=330
        for num,title,body,pic in rows:
            d.rounded_rectangle((55,yy,1025,yy+250),24,fill=(3,7,15,220),outline=(255,255,255,90),width=2)
            # photo strip at right
            thumb=cover_crop(pic,0.5,0.5).resize((260,250),Image.Resampling.LANCZOS)
            thumb=ImageEnhance.Brightness(thumb).enhance(0.65)
            mask=Image.new("L",(260,250),255)
            img.alpha_composite(thumb,(765,yy))
            d=ImageDraw.Draw(img)
            d.text((85,yy+38),num,font=font(FONT_BOLD,45),fill=PINK)
            d.text((150,yy+38),title,font=font(FONT_BOLD,31),fill=YELLOW)
            d.multiline_text((150,yy+97),body,font=font(FONT_REG,21),fill=WHITE,spacing=8)
            yy+=270
        d.text((455,1248),"ELEPHAN",font=font(FONT_BOLD,21),fill=WHITE)

    else:
        img=cover_crop(glass,0.50,0.55)
        img=darken(img,135)
        tint(img,(60,0,35,38))
        brand(img,5)
        d=ImageDraw.Draw(img)
        d.text((82,120),"次の一歩を考える",font=font(FONT_SERIF,48),fill=WHITE)
        d.text((150,182),"チェックリスト",font=font(FONT_SERIF,48),fill=WHITE)
        d.line((155,244,610,244),fill=PINK,width=7)

        items=["月に数日は「感情」も記録してみる","売上だけでなく「心の余裕」も点数化する","怖い・嫌な人がいる場合は早めに相談する","今の店で変えられないことを明確にする","他の店や働き方の情報も集めておく"]
        yy=360
        for t in items:
            checkbox(d,80,yy,t); yy+=102

        # Bottom magenta editorial strip
        d.rounded_rectangle((45,930,1035,1192),28,fill=(75,0,40,205),outline=PINK,width=2)
        d.text((80,965),"もっとラクに、もっと稼げる。",font=font(FONT_SERIF,38),fill=PINK2)
        d.text((80,1022),"合う場所は必ずある。",font=font(FONT_SERIF,42),fill=WHITE)
        bw=brush_word(d,(0,0),"もっと",66,PINK,-7); img.alpha_composite(bw,(700,1040))
        d=ImageDraw.Draw(img)
        d.text((455,1248),"ELEPHAN",font=font(FONT_BOLD,21),fill=WHITE)

    out.parent.mkdir(parents=True,exist_ok=True)
    img.convert("RGB").save(out,"PNG",optimize=True)

def generic_panel(text,n,out,photos):
    portrait,glass,purple=photos
    base=[portrait,glass,purple,portrait,glass][n-1]
    img=cover_crop(base,0.5,0.5)
    img=darken(img,110 if n==1 else 145)
    tint(img,(70,0,35,35))
    brand(img,n)
    d=ImageDraw.Draw(img)

    if n==1:
        hand_circle(d,(32,135,800,440))
        # bigger hook
        f=font(FONT_SERIF,68)
        yy=190
        for line in wrap(d,text,f,900):
            d.text((55,yy),line,font=f,fill=WHITE)
            yy+=86
        bw=brush_word(d,(0,0),"CHECK",72,PINK,-7); img.alpha_composite(bw,(710,620))
        d=ImageDraw.Draw(img)
        d.line((50,1128,690,1128),fill=GOLD,width=2)
        d.text((50,1160),"まず今の状況を言葉にする。",font=font(FONT_BOLD,27),fill=WHITE)
    else:
        yellow_tape(img,58,145,["POINT","CHECK","JUDGE","NEXT"][n-2],420)
        d=ImageDraw.Draw(img)
        d.rounded_rectangle((55,330,1025,1050),32,fill=(3,7,15,215),outline=(255,255,255,90),width=2)
        f=font(FONT_SERIF if n in (2,5) else FONT_BOLD,56)
        yy=405
        for line in wrap(d,text,f,850):
            d.text((90,yy),line,font=f,fill=WHITE)
            yy+=72
        d.rounded_rectangle((58,1120,1022,1195),20,fill=(60,0,35,215))
        d.text((85,1141),"感情と数字を分けて見る。",font=font(FONT_BOLD,24),fill=YELLOW)
    d.text((455,1250),"ELEPHAN",font=font(FONT_BOLD,20),fill=WHITE)

    out.parent.mkdir(parents=True,exist_ok=True)
    img.convert("RGB").save(out,"PNG",optimize=True)

def main():
    posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
    photos=(load_remote(PORTRAIT_URL),load_remote(GLASS_URL),load_remote(PURPLE_GLASS_URL))
    for p in posts:
        if p["date"] < "2026-10-16":
            continue
        if len(p["slides"])!=5:
            raise ValueError(f"{p['date']}: five slides required")
        for i,t in enumerate(p["slides"],1):
            out=OUT/p["date"]/f"{i:02d}.png"
            if p["date"]=="2026-10-16":
                oct16_panel(i,out,photos)
            else:
                generic_panel(t,i,out,photos)
        print(f"rendered {p['date']} approved_reference_v5")

if __name__=="__main__":
    main()
