set -e
P=../deck/png; mkdir -p seg; rm -f seg/*.mp4 lista.txt
for i in $(seq 1 70); do
  n=$(printf %02d $i)
  ffmpeg -loglevel error -y -loop 1 -framerate 5 -i $P/s-$n.png -i audio/$n.wav \
    -af "adelay=500|500,apad=pad_dur=1.0,aresample=44100" -ac 2 \
    -c:v libx264 -preset medium -tune stillimage -crf 23 -pix_fmt yuv420p -r 5 -g 50 \
    -c:a aac -b:a 128k -shortest seg/$n.mp4
  echo "file 'seg/$n.mp4'" >> lista.txt
  echo $i
done
ffmpeg -loglevel error -y -f concat -safe 0 -i lista.txt -c copy -movflags +faststart Video_Guia_MonteCarlo.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 Video_Guia_MonteCarlo.mp4
