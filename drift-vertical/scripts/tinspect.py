import sys,json
T=json.load(open(sys.argv[1])); a,b=float(sys.argv[2]),float(sys.argv[3]); W=T["W"]
out=[]
for r in T["rows"]:
    if a<=r[0]<=b and abs(r[0]*2-round(r[0]*2))<0.06:
        out.append(f"{r[0]:.1f}:" + (f"x{r[1]/W:.2f} w{r[3]/W:.2f}" if len(r)>1 else "--"))
print(sys.argv[1].split('/')[-1], " ".join(out))
