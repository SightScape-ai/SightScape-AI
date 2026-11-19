#!/bin/sh
# Assemble the final reel from rendered shots (shots_ai/) + overlays + clip audio.
set -e; cd "$(dirname "$0")"; SH=${1:-shots_ai}; OUT=${2:-output/sightscape-drift-vertical.mp4}
mkdir -p aud; : > concat.txt; : > aconcat.txt
while read n src st du fill; do
  ffmpeg -nostdin -v error -y -ss $st -t $du -i source/$src.mp4 -vn -af "aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.03,afade=t=out:st=$(echo "$du-0.04"|bc):d=0.04" -c:a pcm_s16le aud/$n.wav
  echo "file '$SH/$n.mp4'" >> concat.txt; echo "file 'aud/$n.wav'" >> aconcat.txt
done < shots.txt
ffmpeg -nostdin -v error -y -f concat -safe 0 -i concat.txt -c copy vid.mp4
ffmpeg -nostdin -v error -y -f concat -safe 0 -i aconcat.txt -c copy aud.wav
ov(){ echo "[$1]format=rgba,fade=t=in:st=$2:d=0.25:alpha=1,fade=t=out:st=$3:d=0.25:alpha=1[o$1]"; }
ffmpeg -nostdin -v error -y -i vid.mp4 \
 -loop 1 -t 27.3 -i overlays/hook.png -loop 1 -t 27.3 -i overlays/line1.png -loop 1 -t 27.3 -i overlays/line2.png \
 -loop 1 -t 27.3 -i overlays/adr.png -loop 1 -t 27.3 -i overlays/end.png -i aud.wav -t 27.3 -i source/5b7307c7.mp4 -filter_complex "\
[0]eq=contrast=1.05:saturation=1.12[g];\
$(ov 1 0.0 2.2);$(ov 2 8.6 12.7);$(ov 3 13.1 17.2);$(ov 4 17.6 21.0);[5]format=rgba,fade=t=in:st=23.9:d=0.4:alpha=1[o5];\
[g][o1]overlay=shortest=1[v1];[v1][o2]overlay[v2];[v2][o3]overlay[v3];[v3][o4]overlay[v4];[v4][o5]overlay,format=yuv420p[v];\
[7:a]aresample=48000,volume=0.35,afade=t=in:d=0.3,afade=t=out:st=26.6:d=0.7[bed];[6:a]afade=t=out:st=26.8:d=0.5[main];\
[main][bed]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
 -map "[v]" -map "[a]" -t 27.3 -c:v libx264 -preset slow -crf 19 -r 30 -c:a aac -b:a 192k -movflags +faststart "$OUT"
