"""ELEPHAN Instagram: neon nightlife magazine visual system v6.

Photographs are freely usable Unsplash images. Each slide is 1080x1350.
Keep tomorrow and subsequent covers consistently in this editorial style.
"""
import io, json, math, random, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"generated"
W,H=1080,1350
BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
REG="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SERIF="/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
PINK=(255,24,148); HOT=(255,59,174); YELLOW=(255,226,67); WHITE=(255,255,255)
GOLD=(236,185,62); DARK=(9,6,23)
PHOTOS=[
 "https://images.unsplash.com/photo-1751076547698-b45b3b7d2695?auto=format&fit=crop&w=1800&q=88",
 "https://images.unsplash.com/photo-1600047987918-ae9beb3fd06e?auto=format&fit=crop&w=1800&q=88",
 "https://images.unsplash.com/photo-1512834109963-ce6d308d7eea?auto=format&fit=crop&w=1800&q=85",
 "https://images.unsplash.com/photo-1737523644515-ec9a40bcd778?auto=format&fit=crop&w=1800&q=85",
]

def f(size,serif=False):
 return ImageFont.truetype(SERIF if serif else BOLD,size)

def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 ELEPHAN"})
 with urllib.request.urlopen(req,timeout=35) as response:
  return Image.open(io.BytesIO(response.read())).convert("RGB")

def fit(im,focus=0.5):
 scale=max(W/im.width,H/im.height)
 im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
 x=int(max(0,im.width-W)*focus); y=int(max(0,im.height-H)*0.44)
 return im.crop((x,y,x+W,y+H)).convert("RGBA")

def bg(photo,shade=85):
 im=fit(photo)
 dark=Image.new("RGBA",(W,H),(9,2,22,shade))
 im.alpha_composite(dark)
 # Add magenta on the left and a warm gold glow on the lower right.
 layer=Image.new("RGBA",(W,H),(0,0,0,0))
 ld=ImageDraw.Draw(layer)
 ld.ellipse((-420,-100,680,1050),fill=(158,0,77,102))
 ld.ellipse((720,600,1500,1520),fill=(223,95,3,77))
 im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(140)))
 return im

def outline_text(draw,xy,text,size,fill=WHITE,stroke=(34,4,35),weight=4,serif=False):
 draw.text(xy,text,font=f(size,serif),fill=fill,stroke_width=weight,stroke_fill=stroke)

def label(im,index):
 d=ImageDraw.Draw(im)
 d.ellipse((44,42,99,97),outline=GOLD,width=4)
 d.arc((57,52,91,91),22,308,fill=GOLD,width=4)
 outline_text(d,(115,36),"ELEPHAN",29,WHITE,weight=0)
 d.text((115,78),"夜職の仕事運・金運",font=ImageFont.truetype(REG,17),fill=WHITE)
 d.line((314,64,758,64),fill=GOLD,width=2)
 outline_text(d,(930,25),f"{index:02d}",59,WHITE,weight=0,serif=True)

def ring(im,coords):
 d=ImageDraw.Draw(im)
 x1,y1,x2,y2=coords
 pts=[]
 for i in range(130):
  a=2*math.pi*i/130
  wob=1+0.016*math.sin(i*1.6)+0.021*math.cos(i*1.95)
  pts.append(((x1+x2)/2+(x2-x1)/2*wob*math.cos(a),(y1+y2)/2+(y2-y1)/2*wob*math.sin(a)))
 d.line(pts+[pts[0]],fill=PINK,width=12,joint="curve")
 d.arc((x1+5,y1+10,x2+5,y2+12),20,150,fill=HOT,width=4)

def under(im,x1,y1,x2,y2):
 d=ImageDraw.Draw(im)
 d.line((x1,y1,x2,y2),fill=PINK,width=11)
 d.line((x1+15,y1+9,x2+37,y2+6),fill=HOT,width=5)

def star(im,x,y,r=10):
 d=ImageDraw.Draw(im)
 d.line((x-r*2,y,x+r*2,y),fill=YELLOW,width=3)
 d.line((x,y-r*2,x,y+r*2),fill=YELLOW,width=3)

def footer(im,caption="数字だけでは分からない、店との相性。"):
 d=ImageDraw.Draw(im)
 d.line((48,1225,715,1225),fill=GOLD,width=2)
 d.text((52,1245),caption,font=ImageFont.truetype(REG,21),fill=WHITE)
 d.text((925,1254),"SWIPE ›",font=f(20),fill=WHITE)

def checkpoint(d,y,text,highlight=False):
 d.rectangle((64,y,104,y+41),outline=PINK,width=4)
 d.line((70,y+19,80,y+32,103,y+1),fill=PINK,width=6)
 d.text((130,y-4),text,font=f(31),fill=YELLOW if highlight else WHITE)

def wrapped(text,size,maxw):
 scratch=ImageDraw.Draw(Image.new("RGB",(1,1)))
 out=[]
 for block in text.split("\n"):
  row=""
  for ch in block:
   if scratch.textbbox((0,0),row+ch,font=f(size,True))[2] <= maxw:
    row+=ch
   else:
    if row: out.append(row)
    row=ch
  if row: out.append(row)
 return out

def save(im,out):
 out.parent.mkdir(parents=True,exist_ok=True)
 im.convert("RGB").save(out,"PNG",optimize=True)

def special_1017(n,photos,out):
 jp,jp2,bar,purple=photos
 if n==1:
  im=bg(jp,62)
  label(im,1); d=ImageDraw.Draw(im)
  outline_text(d,(55,160),"売上があっても、",57,WHITE,weight=3,serif=True)
  under(im,50,251,610,220)
  outline_text(d,(52,320),"この店、",112,WHITE,weight=6,serif=True)
  outline_text(d,(52,490),"合ってない",114,PINK,stroke=WHITE,weight=3)
  outline_text(d,(70,653),"かも。",138,WHITE,weight=7,serif=True)
  ring(im,(42,450,980,870))
  outline_text(d,(60,1050),"出勤前から気が重いなら。",32,YELLOW,weight=3)
  d.text((60,1108),"売上だけで、働く場所を決めなくていい。",font=f(23),fill=WHITE)
  footer(im)
 elif n==2:
  im=bg(bar,135); label(im,2);d=ImageDraw.Draw(im)
  d.polygon([(43,183),(1015,156),(992,272),(55,298)],fill=YELLOW)
  d.text((80,190),"こんな状態、続いていませんか？",font=f(43),fill=DARK)
  for y,s in zip([386,503,620,737,854],[
    "出勤前から気が重い","客層に無理して合わせる",
    "スタッフの顔色を見る","帰宅後の消耗が強い",
    "休みの日も気が休まらない"
  ]): checkpoint(d,y,s,y in (503,737))
  d.line((62,990,1015,990),fill=PINK,width=5)
  outline_text(d,(74,1030),"頑張り方だけの問題？",43,YELLOW,weight=3,serif=True)
  d.text((76,1106),"環境の条件を、一度分けて見てみよう。",font=f(26),fill=WHITE)
 elif n==3:
  im=bg(purple,175);label(im,3);d=ImageDraw.Draw(im)
  outline_text(d,(85,140),"売上 × 心の余裕",65,WHITE,weight=3,serif=True)
  under(im,78,242,812,237)
  data=[
   ("A","売上はある","でも、消耗する",PINK),
   ("B","売上もある","心もラク",YELLOW),
   ("C","売上が少ない","しかも疲れる",WHITE),
   ("D","売上は少ない","でも、心はラク",WHITE),
  ]
  for idx,(letter,t1,t2,col) in enumerate(data):
   x=65+(idx%2)*493;y=348+(idx//2)*352
   d.rounded_rectangle((x,y,x+458,y+319),24,fill=(14,6,33,235),outline=col,width=5)
   outline_text(d,(x+25,y+17),letter,56,col,weight=0,serif=True)
   outline_text(d,(x+28,y+103),t1,31,WHITE,weight=0)
   outline_text(d,(x+28,y+173),t2,34,col,weight=0)
  d.text((102,1100),"「数字はいい」だけでは、",font=f(31),fill=YELLOW)
  d.text((102,1148),"長く続けられるとは限らない。",font=f(31),fill=WHITE)
 elif n==4:
  im=bg(jp2,153);label(im,4);d=ImageDraw.Draw(im)
  outline_text(d,(68,145),"合ってない店の",56,WHITE,weight=4,serif=True)
  outline_text(d,(490,225),"サイン",63,WHITE,weight=4,serif=True)
  outline_text(d,(786,152),"3",105,PINK,weight=2)
  rows=[
   ("01","出勤前から気が重い","前の日から気持ちが沈んでいない？"),
   ("02","人に合わせすぎる","客層・スタッフに無理をしていない？"),
   ("03","終わるとぐったり","売上と疲労の釣り合いはどう？"),
  ]
  for k,(num,title,detail) in enumerate(rows):
   y=380+k*240
   d.rounded_rectangle((43,y,1038,y+220),19,fill=(12,3,28,235),outline=PINK if k==1 else GOLD,width=3)
   outline_text(d,(64,y+23),num,53,PINK,weight=0)
   outline_text(d,(180,y+32),title,38,YELLOW,weight=0)
   d.text((182,y+110),detail,font=f(24),fill=WHITE)
  d.text((90,1180),"数字の裏にある「消耗」も見落とさない。",font=f(25),fill=WHITE)
 elif n==5:
  im=bg(bar,130);label(im,5);d=ImageDraw.Draw(im)
  outline_text(d,(78,157),"この店、合ってる？",61,WHITE,weight=3,serif=True)
  under(im,72,255,879,254)
  outline_text(d,(105,297),"見直しチェック",52,YELLOW,weight=3,serif=True)
  for y,s in zip([470,575,680,785,890],[
    "売上と疲労、両方を記録する",
    "無理に合わせていることを書き出す",
    "改善できる条件を店と相談する",
    "他の店・働き方も比較してみる",
    "安全や健康を優先して判断する"
  ]): checkpoint(d,y,s)
  d.rounded_rectangle((50,1070,1028,1215),30,fill=(107,2,64,238),outline=PINK,width=4)
  outline_text(d,(85,1080),"場所が合えば、働き方は変わる。",35,WHITE,weight=2)
  d.text((85,1150),"保存して、必要な日に見直して。",font=f(24),fill=YELLOW)
 save(im,out)

def generic(post,n,photos,out):
 jp,jp2,bar,purple=photos
 im=bg([jp,bar,purple,jp2,bar][n-1],90 if n==1 else 155)
 label(im,n);d=ImageDraw.Draw(im)
 text=post["slides"][n-1]
 if n==1:
  outline_text(d,(64,155),"NIGHT WORK  /  REAL TALK",28,YELLOW,weight=2)
  under(im,56,226,860,205)
  lines=wrapped(text,76,930)
  y=335
  for idx,line in enumerate(lines[:7]):
   outline_text(d,(59,y),line,76,PINK if idx==len(lines)-1 else WHITE,weight=4,serif=True)
   y+=115
  ring(im,(35,300,1005,min(1090,y+105)))
  footer(im,"夜職の悩みを、数字と気持ちで整理する。")
 else:
  kicker=["","CHECK","POINT","REAL TALK","NEXT"][n-1]
  d.polygon([(48,168),(933,140),(913,253),(58,278)],fill=YELLOW)
  d.text((93,169),kicker,font=f(52),fill=DARK)
  d.rounded_rectangle((40,355,1038,1090),32,fill=(12,2,28,225),outline=PINK,width=5)
  lines=wrapped(text,58,858)
  y=428
  for idx,line in enumerate(lines[:8]):
   outline_text(d,(84,y),line,58,YELLOW if idx==0 else WHITE,weight=2,serif=True)
   y+=83
  under(im,85,1052,744,1020)
  d.text((80,1174),"数字だけでは分からないこともある。",font=f(24),fill=WHITE)
 save(im,out)

def main():
 posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
 photos=[fetch(url) for url in PHOTOS]
 for post in posts:
  if post["date"] < "2026-10-17": continue
  if len(post["slides"])!=5: raise ValueError("Expected five slides")
  for n in range(1,6):
   out=OUT/post["date"]/f"{n:02d}.png"
   if post["date"]=="2026-10-17": special_1017(n,photos,out)
   else: generic(post,n,photos,out)
  print("Rendered",post["date"],"nightlife_magazine_v6",flush=True)

if __name__=="__main__":
 main()
