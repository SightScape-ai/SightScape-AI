import sys, json, cv2
from ultralytics import YOLO
m = YOLO('yolov8n.pt')
src, out, a, b, cls = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), [int(c) for c in sys.argv[5].split(',')]
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS); W=int(cap.get(3)); H=int(cap.get(4))
cap.set(cv2.CAP_PROP_POS_MSEC, a*1000); rows=[]; nxt=a
while True:
    ok, fr = cap.read()
    if not ok: break
    t = cap.get(cv2.CAP_PROP_POS_MSEC)/1000
    if t > b: break
    if t < nxt: continue
    nxt += 0.1
    r = m.predict(fr, imgsz=640, conf=0.2, classes=cls, verbose=False)[0]
    bx = sorted(zip(r.boxes.xyxy.tolist(), r.boxes.conf.tolist()), key=lambda z:-(z[0][2]-z[0][0])*(z[0][3]-z[0][1]))
    if bx:
        x1,y1,x2,y2 = bx[0][0]; rows.append([round(t,2),(x1+x2)/2,(y1+y2)/2,x2-x1,y2-y1,bx[0][1]])
json.dump({"W":W,"H":H,"fps":fps,"rows":rows}, open(out,"w")); print(len(rows))
