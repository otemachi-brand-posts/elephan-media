"""Render ELEPHAN Instagram slides in a high-impact nightlife editorial system."""
import io, json, math, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"generated"
W,H=1080,1350

FONT_BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_SERIF="/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

WHITE=(255,255,255); BLACK=(7,8,14); PINK=(255,31,126)
YELLOW=(255,218,70); GOLD=(230,185,70); CYAN=(32,214,255)
PURPLE=(29,10,58); RED=(140,8,38); MUTED=(225,220,228)

PORTRAIT_URL="https://images.unsplash.com/photo-1773614784571-20d58c26597f?auto=format&fit=crop&w=1800&q=82"
GLASS_URL="https://images.unsplash.com/photo-1512834109963-ce6d308d7eea?auto=format&fit=crop&w=1800&q=82"
PURPLE_GLASS_URL="https://images.unsplash.com/photo-1737523644515-ec9a40bcd778?auto=format&fit=crop&w=1800&q=82"

def font(path,size):
    return ImageFont.truetype(path,size=size)

def load_remote(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=30) as resp:
        return Image.open(io.BytesIO(resp.read())).convert("RGB")

def cover_crop(im):
    scale=max(W/im.width,H/im.height)
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    x=max(0,(im.width-W)//2); y=max(0,(im.height-H)//2)
    return im.crop((x,y,x+W,y+H)).convert("RGBA")

def darken(im,amount=0.35):
    layer=Image.new("RGBA",im.size,(0,0,0,int(255*amount)))
    im.alpha_composite(layer)
    return im

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
                if cur: lines.append(cur)
                cur=ch
        if cur: lines.append(cur)
    return lines

def brand(img,n):
    d=ImageDraw.Draw(img)
    d.ellipse((42,40,88,86),outline=GOLD,width=3)
    d.arc((54,50,83,84),20,310,fill=GOLD,width=3)
    d.text((105,42),"ELEPHAN",font=font(FONT_BOLD,28),fill=WHITE)
    d.text((105,80),"夜職の仕事運・金運",font=font(FONT_REG,17),fill=WHITE)
    d.text((948,42),f"{n:02d}",font=font(FONT_SERIF,58),fill=WHITE)

def marker_circle(img,box):
    d=ImageDraw.Draw(img)
    for off in (0,7,-6):
        b=(box[0]+off,box[1],box[2]-off,box[3])
        d.arc(b,190,520,fill=PINK,width=8)

def headline(img,text,x,y,size=74,maxw=920,stroke=0,stroke_fill=BLACK,fill=WHITE,serif=False):
    d=ImageDraw.Draw(img)
    f=font(FONT_SERIF if serif else FONT_BOLD,size)
    yy=y
    for line in wrap(d,text,f,maxw):
        d.text((x,yy),line,font=f,fill=fill,stroke_width=stroke,stroke_fill=stroke_fill)
        yy += size+16
    return yy

def tape(img,xy,text,w=520):
    d=ImageDraw.Draw(img)
    x,y=xy
    d.polygon([(x,y+8),(x+w,y),(x+w-15,y+78),(x+12,y+85)],fill=YELLOW)
    d.text((x+24,y+18),text,font=font(FONT_BOLD,30),fill=BLACK)

def checkbox(d,x,y,text):
    d.rectangle((x,y,x+34,y+34),outline=PINK,width=3)
    d.line((x+6,y+18,x+14,y+28),fill=PINK,width=4)
    d.line((x+14,y+28,x+31,y+5),fill=PINK,width=4)
    d.text((x+54,y-3),text,font=font(FONT_BOLD,27),fill=WHITE)

def footer(img,text="数字だけじゃ分からない。店との相性は、心の余白も見る。"):
    d=ImageDraw.Draw(img)
    d.line((58,1240,650,1240),fill=GOLD,width=2)
    d.text((58,1260),text,font=font(FONT_REG,20),fill=WHITE)

def render_special_oct16(n,out,photos):
    portrait,glass,purple_glass=photos
    if n==1:
        img=darken(cover_crop(portrait),0.28)
        # warm magenta wash
        wash=Image.new("RGBA",(W,H),(100,0,55,65)); img.alpha_composite(wash)
        brand(img,1); d=ImageDraw.Draw(img)
        marker_circle(img,(35,155,600,390))
        d.text((74,210),"売上はある。",font=font(FONT_SERIF,70),fill=WHITE)
        d.text((62,425),"でも、",font=font(FONT_SERIF,66),fill=WHITE)
        d.text((62,510),"この店にいると",font=font(FONT_SERIF,74),fill=WHITE)
        d.text((55,660),"毎回",font=font(FONT_BOLD,130),fill=PINK,stroke_width=2,stroke_fill=PINK)
        d.text((120,840),"しんどい。",font=font(FONT_SERIF,118),fill=WHITE)
        d.text((60,1165),"数字だけじゃ分からない",font=font(FONT_BOLD,25),fill=WHITE)
        d.text((60,1205),"「合ってる店・合ってない店」のサイン",font=font(FONT_REG,22),fill=WHITE)
        d.text((865,1275),"SWIPE ›",font=font(FONT_BOLD,22),fill=WHITE)
    elif n==2:
        img=darken(cover_crop(glass),0.52); brand(img,2); d=ImageDraw.Draw(img)
        tape(img,(55,165),"こんな状態、ありませんか？",720)
        items=["出勤前から気が重い","売上はあるのに満たされない","お客さまに合わせすぎて疲れる","スタッフの顔色ばかり気になる","休みの日も仕事のことを考えてしまう"]
        yy=380
        for t in items:
            checkbox(d,82,yy,t); yy+=105
        d.line((70,930,1010,930),fill=WHITE,width=2)
        d.text((85,975),"ひとつでも当てはまるなら、",font=font(FONT_BOLD,30),fill=YELLOW)
        d.text((85,1028),"「頑張り方」ではなく",font=font(FONT_BOLD,30),fill=YELLOW)
        d.text((85,1081),"“店との相性”の問題かもしれません。",font=font(FONT_BOLD,30),fill=YELLOW)
        d.text((455,1245),"ELEPHAN",font=font(FONT_BOLD,22),fill=WHITE)
    elif n==3:
        img=darken(cover_crop(purple_glass),0.70); brand(img,3); d=ImageDraw.Draw(img)
        d.text((100,150),"稼げる × 心がラク",font=font(FONT_SERIF,54),fill=WHITE)
        d.text((275,215),"が最強です。",font=font(FONT_SERIF,52),fill=WHITE)
        # axes
        left,top,right,bottom=135,400,945,1040
        mx=(left+right)//2; my=(top+bottom)//2
        d.line((left,my,right,my),fill=PINK,width=4)
        d.line((mx,top,mx,bottom),fill=PINK,width=4)
        d.text((left,350),"稼げる",font=font(FONT_BOLD,25),fill=WHITE)
        d.text((right-80,350),"ラク",font=font(FONT_BOLD,25),fill=WHITE)
        d.text((42,my-15),"しんどい",font=font(FONT_BOLD,22),fill=WHITE)
        d.text((mx-40,bottom+22),"稼げない",font=font(FONT_BOLD,22),fill=WHITE)
        boxes=[
            (left,top,mx,my,"A","売上はあるが\n消耗する","今の状態かも？"),
            (mx,top,right,my,"B","売上もあり\n心もラク","理想の店"),
            (left,my,mx,bottom,"C","売上少なめ\n消耗する","今すぐ見直し"),
            (mx,my,right,bottom,"D","売上少なめ\n心はラク","一時的な避難先"),
        ]
        for x1,y1,x2,y2,k,t,s in boxes:
            d.rounded_rectangle((x1+8,y1+8,x2-8,y2-8),24,outline=WHITE,width=2)
            d.text((x1+35,y1+25),k,font=font(FONT_SERIF,44),fill=WHITE)
            d.multiline_text((x1+35,y1+95),t,font=font(FONT_BOLD,27),fill=WHITE,spacing=8)
            d.text((x1+35,y2-65),s,font=font(FONT_REG,18),fill=YELLOW)
    elif n==4:
        img=darken(cover_crop(portrait),0.58); brand(img,4); d=ImageDraw.Draw(img)
        d.text((68,155),"合ってない店の",font=font(FONT_SERIF,48),fill=WHITE)
        d.text((410,210),"サイン",font=font(FONT_SERIF,48),fill=WHITE)
        d.text((660,155),"3つ",font=font(FONT_BOLD,92),fill=PINK)
        rows=[
            ("1","感情がすり減る","接客中は笑っていても、終わるとどっと疲れる。"),
            ("2","条件だけで続けてしまう","時給やバックは良い。でも、それ以外に魅力を感じない。"),
            ("3","人間関係がストレス","スタッフ・お客さま・黒服など、特定の人の言動に常に気を使っている。"),
        ]
        yy=365
        for num,title,body in rows:
            d.rounded_rectangle((55,yy,1025,yy+235),24,fill=(5,6,12,205),outline=(255,255,255,80),width=2)
            d.text((85,yy+35),num,font=font(FONT_BOLD,48),fill=PINK)
            d.text((155,yy+38),title,font=font(FONT_BOLD,32),fill=YELLOW)
            d.multiline_text((155,yy+92),body,font=font(FONT_REG,23),fill=WHITE,spacing=6)
            yy+=260
    else:
        img=darken(cover_crop(glass),0.55); brand(img,5); d=ImageDraw.Draw(img)
        d.text((80,145),"次の一歩を考える",font=font(FONT_SERIF,50),fill=WHITE)
        d.text((155,205),"チェックリスト",font=font(FONT_SERIF,50),fill=WHITE)
        items=["月に数日は「感情」も記録してみる","売上だけでなく「心の余裕」も点数化する","怖い・嫌な人がいる場合は早めに相談する","今の店で変えられないことを明確にする","他の店や働き方の情報も集めておく"]
        yy=390
        for t in items:
            checkbox(d,80,yy,t); yy+=112
        d.rounded_rectangle((55,1025,1025,1195),24,fill=(70,0,35,175),outline=PINK,width=2)
        d.text((85,1050),"もっとラクに、もっと稼げる。",font=font(FONT_SERIF,38),fill=PINK)
        d.text((85,1105),"合う場所は必ずある。",font=font(FONT_SERIF,42),fill=WHITE)
        d.text((445,1250),"ELEPHAN",font=font(FONT_BOLD,22),fill=WHITE)
    out.parent.mkdir(parents=True,exist_ok=True)
    img.convert("RGB").save(out,"PNG",optimize=True)

def render_generic(text,n,out,photos):
    portrait,glass,purple_glass=photos
    base=[portrait,glass,purple_glass,portrait,glass][n-1]
    img=darken(cover_crop(base),0.52 if n>1 else 0.36)
    # color wash alternating
    wash_colors=[(80,0,55,45),(20,0,30,75),(0,10,60,80),(80,0,25,70),(30,0,55,65)]
    img.alpha_composite(Image.new("RGBA",(W,H),(*wash_colors[n-1],)))
    brand(img,n); d=ImageDraw.Draw(img)
    if n==1:
        marker_circle(img,(40,175,920,480))
        headline(img,text,55,245,76,950,fill=WHITE,serif=True)
        d.text((58,1125),"まず、今の状況を言葉にする。",font=font(FONT_BOLD,29),fill=YELLOW)
        footer(img)
    else:
        tape(img,(55,170),["POINT","CHECK","JUDGE","NEXT"][n-2],420)
        d.rounded_rectangle((55,345,1025,1040),30,fill=(5,6,12,205),outline=(255,255,255,90),width=2)
        headline(img,text,90,430,59,855,fill=WHITE,serif=(n in (2,5)))
        d.rounded_rectangle((55,1110,1025,1190),20,fill=(40,0,30,210))
        d.text((85,1131),"感情と数字を分けて見る。",font=font(FONT_BOLD,25),fill=YELLOW)
        footer(img)
    out.parent.mkdir(parents=True,exist_ok=True)
    img.convert("RGB").save(out,"PNG",optimize=True)

def main():
    posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
    photos=(load_remote(PORTRAIT_URL),load_remote(GLASS_URL),load_remote(PURPLE_GLASS_URL))
    for p in posts:
        if len(p["slides"])!=5:
            raise ValueError(f"{p['date']}: five slides required")
        for i,t in enumerate(p["slides"],1):
            out=OUT/p["date"]/f"{i:02d}.png"
            if p["date"]=="2026-10-16":
                render_special_oct16(i,out,photos)
            else:
                render_generic(t,i,out,photos)
        print(f"rendered {p['date']} nightlife_photo_v4")

if __name__=="__main__":
    main()
