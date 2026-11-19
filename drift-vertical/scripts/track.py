import sys, json, cv2
from ultralytics import YOLO
m = YOLO('yolov8n.pt')
src, out = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS); W=int(cap.get(3)); H=int(cap.get(4))
step = 0.1; nxt = 0.0; prev=None; rows=[]
i=0
while True:
    ok = cap.grab()
    if not ok: break
    t = i/fps; i+=1
    if t+1e-6 < nxt: continue
    nxt += step
    ok, fr = cap.retrieve()
    r = m.predict(fr, imgsz=640, conf=0.12, classes=[2,5,7], verbose=False)[0]
    best=None; bs=-1
    for b,c in zip(r.boxes.xyxy.tolist(), r.boxes.conf.tolist()):
        x1,y1,x2,y2=b; cx=(x1+x2)/2; cy=(y1+y2)/2; a=(x2-x1)*(y2-y1)/(W*H)
        s = c + 3*a**0.5
        if prev: s -= 1.5*abs(cx-prev[0])/W
        if s>bs: bs=s; best=[round(t,2),cx,cy,x2-x1,y2-y1,c]
    if best: prev=best[1:3]
    rows.append(best or [round(t,2)])
json.dump({"W":W,"H":H,"fps":fps,"rows":rows}, open(out,"w"))
det=sum(1 for r in rows if len(r)>1)
print(src.split('/')[-1], f"{det}/{len(rows)} detected")
