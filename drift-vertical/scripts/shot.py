# Render one vertical 1080x1920 shot that keeps the car centred.
# usage: shot.py src.mp4 track.json start dur out.mp4 [fill]
# fill = target fraction of crop width the car should occupy (default 0.75)
import sys, json, subprocess, numpy as np, cv2
src, tj, start, dur, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
fill = float(sys.argv[6]) if len(sys.argv) > 6 else 0.55
MODE = sys.argv[7] if len(sys.argv) > 7 else ""
AI = MODE in ("ai", "ai2")
if AI:
    sys.path.insert(0, __import__("os").path.dirname(__file__)); import esrgan; SR = esrgan.load()
if MODE == "ai2":
    SRP = esrgan.load_plus()
T = json.load(open(tj)); W, H = T["W"], T["H"]
rows = [r for r in T["rows"] if len(r) > 1]
ts = np.array([r[0] for r in rows]); cx = np.array([r[1] for r in rows]); cy = np.array([r[2] for r in rows]); bw = np.array([r[3] for r in rows]); bh = np.array([r[4] for r in rows])
OUTFPS = 30; n = int(round(dur * OUTFPS))
tt = start + np.arange(n) / OUTFPS
# pad the window so smoothing has context
pad = 1.5
grid = np.arange(start - pad, start + dur + pad, 1 / OUTFPS)
def interp(v): return np.interp(grid, ts, v)
gx, gy, gw = interp(cx), interp(cy), interp(bw)
maxh = H; minh = 0.6 * H
gh = np.clip(gw / fill * 16 / 9, minh, maxh)
def smooth(v, sec):
    k = max(1, int(sec * OUTFPS)) | 1
    w = np.hanning(k + 2)[1:-1]; w /= w.sum()
    vp = np.pad(v, k // 2, mode="edge")
    return np.convolve(vp, w, mode="valid")
sx, sy, sh = smooth(gx, 0.6), smooth(gy, 0.8), smooth(gh, 1.4)
def at(v): return np.interp(tt, grid, v)
X, Y, CH = at(sx), at(sy), at(sh)
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1080x1920", "-r", str(OUTFPS), "-i", "-",
                       "-vf", ("noise=alls=2:allf=t" if MODE == "ai2" else "noise=alls=4:allf=t" if AI else "unsharp=5:5:0.6"), "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-g", "15", out], stdin=subprocess.PIPE)
frame = None; srct = start
ok, frame = cap.read(); srct = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
for i in range(n):
    want = tt[i]
    while srct < want - 0.5 / fps:
        ok, f2 = cap.read()
        if not ok: break
        frame = f2; srct = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
    ch = CH[i]; cw = ch * 9 / 16
    if cw > W: cw = W; ch = cw * 16 / 9
    x0 = np.clip(X[i] - cw / 2, 0, W - cw); y0 = np.clip(Y[i] - ch * 0.5, 0, H - ch)
    # sub-pixel crop via affine warp (no jitter from integer rounding)
    s = 1080 / cw
    M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    img = cv2.warpAffine(frame, M, (1080, 1920), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    if AI:
        s4 = s / 4
        M4 = np.float32([[s4, 0, -x0 * s4], [0, s4, -y0 * s4]])
        small = cv2.warpAffine(frame, M4, (270, 480), flags=cv2.INTER_AREA if s4 < 1 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        if MODE == "ai2":
            img = esrgan.upscale(SR, small)
            # car patch in small-frame coords, from the raw detection at this time
            t = tt[i]; bx, by = np.interp(t, ts, cx), np.interp(t, ts, cy)
            hw, hh = np.interp(t, ts, bw) * 0.62, np.interp(t, ts, bh) * 0.70
            px0 = int(max(0, (bx - hw - x0) * s4)); px1 = int(min(270, (bx + hw - x0) * s4))
            py0 = int(max(0, (by - hh - y0) * s4)); py1 = int(min(480, (by + hh - y0) * s4))
            if px1 - px0 > 16 and py1 - py0 > 16:
                up = esrgan.upscale(SRP, np.ascontiguousarray(small[py0:py1, px0:px1]))
                up = cv2.addWeighted(up, 1.35, cv2.GaussianBlur(up, (0, 0), 2.2), -0.35, 0)
                ph, pw = up.shape[:2]; f = max(8, min(ph, pw) // 6)
                m = np.zeros((ph, pw), np.float32); m[f:-f, f:-f] = 1
                m = cv2.GaussianBlur(m, (0, 0), f / 2)[..., None]
                reg = img[py0*4:py1*4, px0*4:px1*4].astype(np.float32)
                img[py0*4:py1*4, px0*4:px1*4] = (up * m + reg * (1 - m)).astype(np.uint8)
        else:
            img = cv2.addWeighted(esrgan.upscale(SR, small), 0.75, img, 0.25, 0)
    ff.stdin.write(img.tobytes())
ff.stdin.close(); ff.wait()
print(out, "ok")
