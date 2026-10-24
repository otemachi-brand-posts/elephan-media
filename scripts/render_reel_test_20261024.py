"""Create Oct 24 2026 ELEPHAN Instagram Reel: three things to check before moving clubs.
15 seconds / 1080x1920 H264 MP4. Uses existing approved glamorous hostess portraits,
writes wholly new copy to each frame. No licensed background music.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import json, math, subprocess, random

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"generated"/"2026-10-17-revised"
OUT=ROOT/"generated"/"reels"
FOLDER=OUT/"frames-2026-10-24"
DEST=OUT/"2026-10-24-elephan-reel.mp4"
FW,FH=1080,1920
FONT="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SERIF="/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
PINK=(255,14,160);WHITE=(255,255,255);GOLD=(255,207,105)
FRAMES=[
 ("移籍したい。","でも、次の店でも\n同じだったら？","移籍前に見たい3つの条件"),
 ("CHECK 01","お客さんの層","自分の接客と\n合う雰囲気？"),
 ("CHECK 02","スタッフとの関係","困った時に\n相談しやすい？"),
 ("CHECK 03","出勤のしやすさ","無理せず続く\n曜日と時間帯？"),
 ("移籍前に保存","時給だけで\n決めないで。","個別鑑定は\nプロフィールのLINEへ")
]
def font(sz,serif=False):
    return ImageFont.truetype(SERIF if serif else FONT,sz)
def model():
    # Clean-text crop from the final approved visual, no old headline residue.
    im=Image.open(SOURCE/"04.jpg").convert("RGB")
    return im.crop((39,445,518,852))
def draw_label(im,text,y,sz,maxwidth=920,color=WHITE,highlight=False):
    dr=ImageDraw.Draw(im)
    ft=font(sz,serif=True)
    lines=[]
    for row in text.split("\n"):
        if dr.textbbox((0,0),row,font=ft)[2]<=maxwidth:lines.append(row)
        else:
            tmp=""
            for ch in row:
                trial=tmp+ch
                if dr.textbbox((0,0),trial,font=ft)[2]>maxwidth and tmp:
                    lines.append(tmp);tmp=ch
                else:tmp=trial
            if tmp:lines.append(tmp)
    for row in lines:
        sh=Image.new("RGBA",(FW,FH),(0,0,0,0))
        sd=ImageDraw.Draw(sh)
        if highlight:
            sd.text((53,y),row,font=ft,fill=(*PINK,210),stroke_width=11,stroke_fill=(*PINK,185))
            im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(17)))
        dr.text((53,y),row,font=ft,fill=PINK if highlight else color,stroke_width=3,
                stroke_fill=(31,2,25))
        y+=int(sz*1.39)
    return y
def make_slide(i,portrait):
    im=Image.new("RGBA",(FW,FH),(13,2,21,255))
    # Approved photo against a glowing magenta nightclub backdrop.
    bg=ImageOps.fit(portrait,(FW,FH),Image.Resampling.LANCZOS)
    bg=ImageEnhance.Color(bg).enhance(1.7)
    bg=bg.filter(ImageFilter.GaussianBlur(62)).convert("RGBA")
    bg.alpha_composite(Image.new("RGBA",(FW,FH),(33,0,35,120)))
    im.alpha_composite(bg)
    sparkle=Image.new("RGBA",(FW,FH),(0,0,0,0));d=ImageDraw.Draw(sparkle)
    rng=random.Random(20261024+i)
    for _ in range(24):
        x=rng.randrange(FW);y=rng.randrange(FH);r=rng.randrange(10,42)
        d.ellipse((x-r,y-r,x+r,y+r),fill=(255,rng.randrange(70,160),172,rng.randrange(40,105)))
    im.alpha_composite(sparkle.filter(ImageFilter.GaussianBlur(21)))
    # Large colorful portrait, but leave contrast for vivid giant headline.
    photo=ImageOps.fit(portrait,(796,1370),Image.Resampling.LANCZOS,centering=(0.55,0.5))
    photo=ImageEnhance.Color(photo).enhance(1.23).convert("RGBA")
    mask=Image.new("L",photo.size,0);px=mask.load()
    for x in range(photo.width):
        factor=max(0,min(1,(x-6)/230))
        for y in range(photo.height):
            vy=min(1,(y+2)/70,(photo.height-y+2)/90)
            px[x,y]=int(255*factor*max(0,vy))
    mask=mask.filter(ImageFilter.GaussianBlur(22))
    im.paste(photo,(FW-796,212),mask)
    dark=Image.new("RGBA",(FW,FH),(0,0,0,0));dp=dark.load()
    for x in range(FW):
        a=int(184*(1-x/FW)**1.9)
        for y in range(FH):dp[x,y]=(16,0,22,a)
    im.alpha_composite(dark)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((42,34,1038,156),30,fill=(16,2,28,207),outline=PINK,width=5)
    d.text((74,59),"ELEPHAN  |  夜職の仕事運・金運",font=font(38),fill=WHITE)
    d.rounded_rectangle((896,179,1038,261),32,fill=(25,0,29,230),outline=GOLD,width=3)
    d.text((926,193),f"{i+1}/5",font=font(42,True),fill=WHITE)
    first,second,third=FRAMES[i]
    if i==0:
        y=draw_label(im,first,367,111,highlight=True)
        y=draw_label(im,second,y+30,90)
        draw_label(im,third,1258,54,highlight=True)
    elif i==4:
        y=draw_label(im,first,373,98,highlight=True)
        y=draw_label(im,second,y+34,88)
        draw_label(im,third,1242,54,highlight=True)
    else:
        y=draw_label(im,first,350,69,highlight=True)
        y=draw_label(im,second,y+35,102)
        draw_label(im,third,1215,63,highlight=True)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((34,1664,1046,1851),28,fill=(32,1,33,220),outline=PINK,width=5)
    foot="稼げるかだけでなく、続けられるかも見る。" if i<4 else "あとで見返して、条件を整理しよう。"
    d.text((66,1717),foot,font=font(34),fill=WHITE)
    d.text((67,1791),"ELEPHAN  NIGHT WORK",font=font(23),fill=GOLD)
    return im.convert("RGB")
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    FOLDER.mkdir(parents=True,exist_ok=True)
    pic=model()
    for i in range(5):
        output=FOLDER/f"slide{i+1:02d}.jpg"
        make_slide(i,pic).save(output,quality=89,optimize=True)
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-framerate","1/3","-start_number","1","-i",str(FOLDER/"slide%02d.jpg"),
        "-vf","fps=24,format=yuv420p","-c:v","libx264","-crf","23",
        "-preset","veryfast","-movflags","+faststart","-t","15",str(DEST)]
    subprocess.run(cmd,check=True,timeout=300)
    p=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
        "stream=codec_name,width,height","-show_entries","format=duration,size",
        "-of","json",str(DEST)],text=True))
    video=p["streams"][0]
    assert (video["codec_name"],video["width"],video["height"])==("h264",1080,1920)
    assert 14.9<=float(p["format"]["duration"])<=15.2
    assert DEST.stat().st_size>200000
    print(json.dumps({"video":str(DEST),"meta":p},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
