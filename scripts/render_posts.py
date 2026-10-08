"""Render ELEPHAN Instagram carousel slides as editorial 1080x1350 PNGs."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"generated"
W,H=1080,1350

NAVY="#0B1020"
NAVY2="#151D35"
IVORY="#F4EFE5"
GOLD="#C9A55D"
LAV="#9A8AB8"
MUTED="#777184"
INK="#121728"
SOFT="#E8E1D7"

FONT_BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

def font(path,size):
    return ImageFont.truetype(path,size=size)

def wrap(draw,text,fnt,max_width):
    lines=[]
    for block in text.split("\n"):
        if block=="":
            lines.append("")
            continue
        cur=""
        for ch in block:
            test=cur+ch
            if draw.textbbox((0,0),test,font=fnt)[2] <= max_width:
                cur=test
            else:
                if cur: lines.append(cur)
                cur=ch
        if cur: lines.append(cur)
    return lines

def draw_text_block(draw,text,fnt,x,y,max_width,line_h,fill,align="left"):
    lines=wrap(draw,text,fnt,max_width)
    for i,line in enumerate(lines):
        if align=="center":
            box=draw.textbbox((0,0),line,font=fnt)
            xx=x+(max_width-(box[2]-box[0]))/2
        else:
            xx=x
        draw.text((xx,y+i*line_h),line,font=fnt,fill=fill)
    return y+len(lines)*line_h

def elephant_mark(draw,x,y,scale=1.0,color=GOLD):
    r=int(24*scale)
    draw.ellipse((x,y,x+r*2,y+r*2),outline=color,width=max(2,int(3*scale)))
    draw.arc((x+r*0.55,y+r*0.35,x+r*1.55,y+r*1.55),35,310,fill=color,width=max(2,int(3*scale)))
    draw.ellipse((x+r*1.42,y+r*0.75,x+r*1.58,y+r*0.91),fill=color)

def brand(draw,dark=True,slide_no=1):
    fg=IVORY if dark else INK
    elephant_mark(draw,64,58,1.0,GOLD)
    draw.text((124,55),"ELEPHAN",font=font(FONT_BOLD,30),fill=fg)
    draw.text((124,93),"夜職の仕事運・金運",font=font(FONT_REG,20),fill=LAV if dark else MUTED)
    draw.text((946,64),f"{slide_no}/5",font=font(FONT_REG,22),fill=LAV if dark else MUTED)

def celestial(draw,dark=True):
    c=GOLD if dark else LAV
    draw.arc((780,-100,1160,300),105,245,fill=c,width=5)
    draw.ellipse((896,205,908,217),fill=c)
    draw.ellipse((838,160,845,167),fill=LAV if dark else GOLD)

def footer(draw,dark=True):
    fg="#9D98A9" if dark else "#777184"
    draw.text((64,1268),"占いは判断材料のひとつ。大きな判断は現実の条件も確認してください。",font=font(FONT_REG,18),fill=fg)

def cover(draw,text,creative_type):
    # Editorial cover: no card-in-card. Huge hook with a single strong graphic device.
    dark=creative_type!="checklist"
    bg=NAVY if dark else IVORY
    fg=IVORY if dark else INK
    brand(draw,dark,1)
    celestial(draw,dark)
    label={"diagnostic":"SELF CHECK","checklist":"WORK NOTE","empathy":"TONIGHT"}[creative_type]
    draw.text((66,250),label,font=font(FONT_BOLD,24),fill=GOLD if dark else LAV)

    if creative_type=="diagnostic":
        # big question mark as visual anchor
        draw.text((720,330),"? ",font=font(FONT_BOLD,250),fill=NAVY2)
        y=390
        y=draw_text_block(draw,text,font(FONT_BOLD,78),72,y,720,104,fg)
        draw.line((72,1035,560,1035),fill=GOLD,width=4)
        draw.text((72,1070),"答えを急がず、まず分けて見る。",font=font(FONT_REG,28),fill=LAV)
    elif creative_type=="checklist":
        draw.text((72,360),"01",font=font(FONT_BOLD,160),fill=SOFT)
        y=430
        y=draw_text_block(draw,text,font(FONT_BOLD,76),290,y,700,102,fg)
        draw.rounded_rectangle((72,1030,435,1108),radius=38,fill=INK)
        draw.text((110,1050),"保存して見返す",font=font(FONT_BOLD,28),fill=IVORY)
    else:
        draw.line((72,350,72,970),fill=GOLD,width=5)
        y=410
        y=draw_text_block(draw,text,font(FONT_BOLD,80),112,y,820,110,fg)
        draw.text((112,1015),"一晩の数字と、自分の価値は別。",font=font(FONT_REG,28),fill=LAV)
    footer(draw,dark)

def insight_slide(draw,text,slide_no,creative_type):
    # Alternating light/dark spreads; this is intentionally not a repeated template.
    dark = slide_no in (2,4)
    bg=NAVY if dark else IVORY
    fg=IVORY if dark else INK
    brand(draw,dark,slide_no)

    if slide_no==2:
        draw.text((68,245),"まず、ここを見る",font=font(FONT_BOLD,25),fill=GOLD)
        draw_text_block(draw,text,font(FONT_BOLD,64),72,360,860,90,fg)
        draw.line((72,1025,1008,1025),fill=GOLD if dark else LAV,width=3)
        draw.text((72,1060),"感情と事実を分ける。",font=font(FONT_REG,30),fill=LAV if dark else MUTED)

    elif slide_no==3:
        draw.text((68,235),"CHECK",font=font(FONT_BOLD,24),fill=LAV)
        parts=[p for p in text.split("\n") if p.strip()]
        y=330
        for i,p in enumerate(parts[:4],1):
            draw.text((72,y),f"{i:02}",font=font(FONT_BOLD,52),fill=GOLD)
            draw.line((155,y+35,220,y+35),fill=GOLD,width=3)
            draw_text_block(draw,p,font(FONT_BOLD,44),255,y+2,720,60,fg)
            y+=165

    elif slide_no==4:
        draw.text((68,240),"HOW TO READ IT",font=font(FONT_BOLD,24),fill=GOLD)
        draw.rounded_rectangle((64,320,1016,1000),radius=38,outline=NAVY2 if dark else SOFT,width=2)
        draw_text_block(draw,text,font(FONT_BOLD,58),110,455,820,82,fg,align="center")
        draw.text((110,915),"→ 次に動かす場所を一つだけ決める",font=font(FONT_REG,28),fill=LAV if dark else MUTED)

    else:
        # CTA / summary slide: lighter commercial touch, not banner-like.
        draw.text((68,240),"NEXT STEP",font=font(FONT_BOLD,24),fill=LAV)
        draw_text_block(draw,text,font(FONT_BOLD,58),72,360,880,82,fg)
        draw.rounded_rectangle((72,925,1008,1088),radius=40,fill=NAVY2 if not dark else IVORY)
        cta_fill=IVORY if not dark else INK
        draw.text((118,970),"必要な方だけ、プロフィールから個別に。",font=font(FONT_BOLD,30),fill=cta_fill)

    footer(draw,dark)

def render_slide(text,slide_no,output,creative_type):
    dark = True if slide_no==1 and creative_type!="checklist" else slide_no in (2,4)
    bg=NAVY if dark else IVORY
    img=Image.new("RGB",(W,H),bg)
    draw=ImageDraw.Draw(img)
    if slide_no==1:
        cover(draw,text,creative_type)
    else:
        insight_slide(draw,text,slide_no,creative_type)
    output.parent.mkdir(parents=True,exist_ok=True)
    img.save(output,"PNG",optimize=True)

def main():
    posts=json.loads((ROOT/"posts.json").read_text(encoding="utf-8"))
    for post in posts:
        if len(post["slides"])!=5:
            raise ValueError(f"{post['date']}: exactly five slides are required")
        creative_type=post.get("creative_type","empathy")
        if creative_type not in {"empathy","checklist","diagnostic"}:
            raise ValueError(f"{post['date']}: invalid creative_type")
        day=OUT/post["date"]
        for i,text in enumerate(post["slides"],1):
            render_slide(text,i,day/f"{i:02d}.png",creative_type)
        print(f"rendered {post['date']} editorial_v2 type={creative_type}")

if __name__=="__main__":
    main()
