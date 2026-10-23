"""Render one 15-second vertical Instagram Reel from the previously approved
glamorous 5-page ELEPHAN magazine creative. No copyrighted music.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import subprocess, json

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"generated"/"2026-10-17-revised"
OUT=ROOT/"generated"/"reels"
FONT="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
DEST=OUT/"2026-10-23-elephan-test.mp4"

def render():
    OUT.mkdir(parents=True,exist_ok=True)
    frames=OUT/"frames-2026-10-23"
    frames.mkdir(parents=True,exist_ok=True)
    for n in range(1,6):
        src=SOURCE/f"{n:02d}.jpg"
        if not src.exists():raise RuntimeError("Missing approved image: "+str(src))
        im=Image.open(src).convert("RGB")
        bg=ImageOps.fit(im,(1080,1920)).filter(ImageFilter.GaussianBlur(40)).convert("RGBA")
        bg.alpha_composite(Image.new("RGBA",(1080,1920),(20,0,22,165)))
        foreground=ImageOps.fit(im,(1068,1335)).convert("RGBA")
        bg.paste(foreground,(6,283))
        d=ImageDraw.Draw(bg)
        d.rounded_rectangle((10,15,1070,204),20,fill=(18,0,28,218),outline=(255,34,164),width=5)
        d.text((65,54),"ELEPHAN  |  NIGHT WORK",font=ImageFont.truetype(FONT,48),fill=(255,255,255))
        d.text((73,130),"夜職の仕事運・金運  /  今夜のセルフチェック",
            font=ImageFont.truetype(FONT,27),fill=(255,195,219))
        d.rounded_rectangle((18,1710,1062,1875),22,fill=(30,2,28,218),outline=(255,34,164),width=5)
        copy="売上だけで、働く場所を決めない。" if n!=5 else "保存して見返す。個別鑑定はプロフィールへ"
        d.text((52,1755),copy,font=ImageFont.truetype(FONT,35 if n!=5 else 31),
               fill=(255,252,255))
        bg.convert("RGB").save(frames/f"slide{n:02d}.jpg",quality=91,optimize=True)
    command=[
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-framerate","1/3","-start_number","1",
        "-i",str(frames/"slide%02d.jpg"),
        "-vf","fps=24,format=yuv420p",
        "-c:v","libx264","-preset","veryfast","-crf","23",
        "-r","24","-pix_fmt","yuv420p","-movflags","+faststart",
        "-t","15",str(DEST)
    ]
    subprocess.run(command,check=True,timeout=300)
    cmd=["ffprobe","-v","error","-show_entries","stream=codec_name,width,height,r_frame_rate",
         "-show_entries","format=duration,size","-of","json",str(DEST)]
    probe=json.loads(subprocess.check_output(cmd,text=True))
    v=probe["streams"][0]
    if (v["width"],v["height"],v["codec_name"])!=(1080,1920,"h264"):
        raise RuntimeError("Invalid video format")
    duration=float(probe["format"]["duration"])
    if not (14.9<=duration<=15.2):raise RuntimeError("Wrong duration "+str(duration))
    if DEST.stat().st_size<200000:raise RuntimeError("Suspiciously small mp4")
    print(json.dumps({"file":str(DEST),"format":probe},ensure_ascii=False),flush=True)

if __name__=="__main__":
    render()
