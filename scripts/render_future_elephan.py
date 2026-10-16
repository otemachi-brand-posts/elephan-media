"""2026-10-18+ ELEPHAN editorial nightlife carousels.

Uses the approved Japanese-hostess visual assets already committed to generated/2026-10-17.
Deliberately does not alter Oct 17 reserved JPEGs.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import json, math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'generated'
W,H=1080,1350
B='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
R='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
F='/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
WHITE='#fff9fe'; YELLOW='#ffde3f'; PINK='#ff219b'; GOLD='#e8ba50'; NAVY='#0b0719'

def font(px,style='b'):return ImageFont.truetype({'b':B,'r':R,'f':F}[style],px)
def wrap(d,text,f,maxw):
    ls=[]
    for p in text.split('\n'):
        if not p: continue
        line=''
        for ch in p:
            if d.textbbox((0,0),line+ch,font=f)[2]<=maxw:line+=ch
            else:
                if line:ls.append(line)
                line=ch
        if line:ls.append(line)
    return ls

def centered_cover(src):
    crop=src.crop((max(0,src.width-550),30,src.width,800))
    scale=max(W/crop.width,H/crop.height)
    crop=crop.resize((int(crop.width*scale),int(crop.height*scale)),Image.Resampling.LANCZOS)
    x=(crop.width-W)//2;y=(crop.height-H)//2
    return crop.crop((x,y,x+W,y+H)).convert('RGBA')

def bg(photos,n):
    if n==1:
        img=centered_cover(photos[0]);img=ImageEnhance.Color(img).enhance(1.2)
    else:
        src=photos[[1,2,3,4][n-2]]
        img=src.filter(ImageFilter.GaussianBlur(27)).convert('RGBA')
    overlay=Image.new('RGBA',(W,H),(12,1,27,45 if n==1 else 52));img.alpha_composite(overlay)
    shade=Image.new('RGBA',(W,H));pixels=shade.load()
    for x in range(W):
        z=x/W
        alpha=int((230*(1-z)**2.0 + (25 if n==1 else 55)))
        for y in range(H): pixels[x,y]=(5,1,15,min(255,alpha))
    img.alpha_composite(shade)
    # Mask printed page numbers from source reference before adding current label.
    ImageDraw.Draw(img).rectangle((887,0,1079,139),fill=(13,3,29,250))
    return img

def label(d,n):
    d.ellipse((47,41,102,96),outline=GOLD,width=3)
    d.arc((60,50,95,91),30,322,fill=GOLD,width=3)
    d.text((121,43),'ELEPHAN',font=font(29),fill=WHITE)
    d.text((121,81),'夜職の仕事運・金運',font=font(17,'r'),fill=WHITE)
    d.text((938,34),str(n).zfill(2),font=font(58,'f'),fill=WHITE)

def underline(d,x,y,length):
    d.line([(x+k*length/32,y+5*math.sin(k/3)) for k in range(33)],fill=PINK,width=12,joint='curve')

def textbox(d,text,x,y,width,size,fill=WHITE,style='b',line_gap=17,max_lines=6,shadow=False):
    f=font(size,style);lines=wrap(d,text,f,width)
    if len(lines)>max_lines:
        size=max(25,size*max_lines//len(lines));f=font(size,style);lines=wrap(d,text,f,width)
    yy=y
    for line in lines:
        if shadow:d.text((x+3,yy+5),line,font=f,fill='#10001a',stroke_width=3,stroke_fill='#10001a')
        d.text((x,yy),line,font=f,fill=fill)
        yy+=size+line_gap
    return yy

def brand_bottom(d):
    d.line((58,1250,1020,1250),fill=GOLD,width=2)
    d.text((58,1269),'ELEPHAN  /  NIGHT WORK',font=font(17,'r'),fill=WHITE)
    d.text((900,1269),'SWIPE ›',font=font(17),fill=WHITE)

def panel(text,n,date,photos,out):
    img=bg(photos,n); d=ImageDraw.Draw(img)
    label(d,n)
    if n==1:
        d.rounded_rectangle((54,180,574,249),16,fill=YELLOW)
        d.text((80,196),'夜職の仕事運 / REAL CHECK',font=font(24),fill=NAVY)
        lines=text.split('\n')
        top=355
        for k,s in enumerate(lines):
            c=PINK if k==len(lines)-1 else WHITE
            top=textbox(d,s,55,top,950,84,c,'f' if k==0 else 'b',17,3,True)
            if k==0:underline(d,57,top+10,665)
        d.rounded_rectangle((55,1097,1030,1202),20,fill=(12,7,25,220),outline=PINK,width=3)
        d.text((82,1127),'数字だけじゃ見えない、仕事のヒント。',font=font(28),fill=YELLOW)
    elif n==2:
        d.rounded_rectangle((58,184,547,254),15,fill=YELLOW)
        d.text((85,202),'POINT 01 / まず気づく',font=font(27),fill=NAVY)
        top=textbox(d,text,60,365,943,90,WHITE,'f',23,5,True)
        underline(d,60,min(top+55,875),820)
        d.rounded_rectangle((61,1039,1016,1191),24,fill=(6,5,15,232),outline=GOLD,width=3)
        textbox(d,'思い込みと、現実に起きたことを分けてみる。',93,1082,870,30,YELLOW,'b',8,2)
    elif n==3:
        d.rounded_rectangle((55,180,555,255),14,fill=PINK)
        d.text((85,201),'POINT 02 / 何が変化した？',font=font(25),fill=WHITE)
        d.rounded_rectangle((53,360,1027,955),30,fill=(5,5,18,233),outline=YELLOW,width=5)
        top=textbox(d,text,91,505,865,81,WHITE,'f',19,5,True)
        underline(d,89,min(815,top+45),735)
        d.text((84,1084),'感情で決める前に、',font=font(37),fill=YELLOW)
        d.text((84,1141),'違いをひとつずつ確認。',font=font(35),fill=WHITE)
    elif n==4:
        d.rounded_rectangle((57,183,530,257),16,fill=YELLOW)
        d.text((82,202),'POINT 03 / ここも見る',font=font(26),fill=NAVY)
        d.rounded_rectangle((57,360,1023,990),27,fill=(5,3,14,210),outline=PINK,width=5)
        top=textbox(d,text,92,510,870,81,WHITE,'f',23,5,True)
        underline(d,91,min(top+55,883),755)
        d.text((73,1092),'環境が変わると、',font=font(41),fill=YELLOW)
        d.text((73,1155),'見える答えも変わる。',font=font(39),fill=WHITE)
    else:
        d.rounded_rectangle((57,181,567,255),15,fill=PINK)
        d.text((81,201),'SAVE / あとで確認',font=font(29),fill=WHITE)
        d.rounded_rectangle((51,320,1027,995),34,fill=(3,3,14,235),outline=YELLOW,width=4)
        top=textbox(d,text,92,456,854,66,WHITE,'f',24,6,True)
        underline(d,93,min(top+40,911),720)
        d.rounded_rectangle((53,1075,1028,1193),26,fill=PINK)
        d.text((105,1107),'保存して、次の出勤前に見返す。',font=font(34),fill=WHITE)
    brand_bottom(d)
    dest=out/date/f'{n:02d}.png';dest.parent.mkdir(parents=True,exist_ok=True)
    img.convert('RGB').save(dest,'PNG',optimize=True)

def main():
    p=json.loads((ROOT/'posts.json').read_text(encoding='utf-8'))
    album=ROOT/'generated'/'2026-10-17'
    photos=[Image.open(album/f'{k:02d}.jpg').convert('RGB') for k in range(1,6)]
    for post in p:
        if post['date']<'2026-10-18':continue
        for n,text in enumerate(post['slides'],1):panel(text,n,post['date'],photos,OUT)
        print('nightlife magazine updated',post['date'])
if __name__=='__main__':main()