#!/bin/sh
# Short (~14 s) cut assembled from already-rendered AI shots.
set -e; cd "$(dirname "$0")"; SH=${1:-shots_ai2}; OUT=${2:-output/sightscape-drift-vertical-short.mp4}
mkdir -p cut; : > concat.txt; : > aconcat.txt
grep -v '^#' shots_short.txt | while read n src st off du; do
  ffmpeg -nostdin -v error -y -ss $off -t $du -i $SH/$n.mp4 -an -c:v libx264 -preset slow -crf 16 -r 30 cut/$n.mp4
  ffmpeg -nostdin -v error -y -ss $(echo "$st+$off"|bc) -t $du -i source/$src.mp4 -vn -af "aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.03,afade=t=out:st=$(echo "$du-0.04"|bc):d=0.04" -c:a pcm_s16le cut/$n.wav
  echo "file 'cut/$n.mp4'" >> concat.txt; echo "file 'cut/$n.wav'" >> aconcat.txt
done
ffmpeg -nostdin -v error -y -f concat -safe 0 -i concat.txt -c copy vid.mp4
ffmpeg -nostdin -v error -y -f concat -safe 0 -i aconcat.txt -c copy aud.wav
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 vid.mp4)
ov(){ echo "[$1]format=rgba,fade=t=in:st=$2:d=0.2:alpha=1,fade=t=out:st=$3:d=0.2:alpha=1[o$1]"; }
ffmpeg -nostdin -v error -y -i vid.mp4 \
 -loop 1 -t $D -i overlays/hook.png -loop 1 -t $D -i overlays/line1.png -loop 1 -t $D -i overlays/line2.png \
 -loop 1 -t $D -i overlays/adr.png -loop 1 -t $D -i overlays/end.png -i aud.wav -t $D -i source/5b7307c7.mp4 -filter_complex "\
[0]eq=contrast=1.05:saturation=1.12[g];\
$(ov 1 0.0 1.8);$(ov 2 3.5 6.5);$(ov 3 6.7 9.7);$(ov 4 9.9 11.2);[5]format=rgba,fade=t=in:st=11.6:d=0.35:alpha=1[o5];\
[g][o1]overlay=shortest=1[v1];[v1][o2]overlay[v2];[v2][o3]overlay[v3];[v3][o4]overlay[v4];[v4][o5]overlay,format=yuv420p[v];\
[7:a]aresample=48000,volume=0.35,afade=t=in:d=0.2,afade=t=out:st=$(echo "$D-0.6"|bc):d=0.6[bed];[6:a]afade=t=out:st=$(echo "$D-0.4"|bc):d=0.4[main];\
[main][bed]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
 -map "[v]" -map "[a]" -t $D -c:v libx264 -preset slow -crf 19 -r 30 -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "$OUT $D s"
