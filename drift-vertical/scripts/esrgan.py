import torch, torch.nn as nn, torch.nn.functional as F
class SRVGGNetCompact(nn.Module):
    def __init__(s, nf=64, nc=32, up=4):
        super().__init__(); s.up = up
        b = [nn.Conv2d(3, nf, 3, 1, 1), nn.PReLU(nf)]
        for _ in range(nc): b += [nn.Conv2d(nf, nf, 3, 1, 1), nn.PReLU(nf)]
        b += [nn.Conv2d(nf, 3 * up * up, 3, 1, 1)]
        s.body = nn.ModuleList(b); s.ps = nn.PixelShuffle(up)
    def forward(s, x):
        o = x
        for l in s.body: o = l(o)
        return s.ps(o) + F.interpolate(x, scale_factor=s.up, mode='nearest')
def load(path='/home/user/SightScape-AI/drift-vertical/models/realesr-general-x4v3.pth'):
    m = SRVGGNetCompact(); sd = torch.load(path, map_location='cpu')
    m.load_state_dict(sd.get('params_ema', sd.get('params', sd)), strict=True); return m.eval()
@torch.inference_mode()
def upscale(m, bgr):  # bgr uint8 HxWx3 numpy -> 4x bgr uint8
    import numpy as np
    x = torch.from_numpy(bgr[:, :, ::-1].copy()).permute(2, 0, 1).float().div(255).unsqueeze(0)
    y = m(x).clamp(0, 1)[0].permute(1, 2, 0).mul(255).round().byte().numpy()[:, :, ::-1]
    return np.ascontiguousarray(y)
