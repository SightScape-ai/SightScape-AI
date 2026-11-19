const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const A = '/home/user/SightScape-AI/drift-vertical/assets/';
const logo = fs.readFileSync(A + 'logo.svg', 'utf8');
const css = `
@font-face{font-family:K;font-weight:600;src:url(file://${A}kufi-600.ttf)}
@font-face{font-family:K;font-weight:800;src:url(file://${A}kufi-800.ttf)}
html,body{margin:0;width:1080px;height:1920px;background:transparent;font-family:K;direction:rtl}
.wrap{position:absolute;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:18px}
.big{font-weight:800;color:#fff;font-size:128px;line-height:1.15;text-shadow:0 6px 30px rgba(0,0,0,.75),0 2px 4px rgba(0,0,0,.9);white-space:nowrap}
.mid{font-weight:800;color:#fff;font-size:84px;line-height:1.2;text-shadow:0 6px 24px rgba(0,0,0,.8),0 2px 4px rgba(0,0,0,.9);white-space:nowrap}
.tag{font-weight:800;color:#fff;background:#eb6f24;font-size:60px;padding:4px 40px 14px;border-radius:18px;white-space:nowrap;box-shadow:0 10px 30px rgba(0,0,0,.45)}
.navy{background:#1a1a2e;border:4px solid #3961a9}
.pill{background:#fff;border-radius:26px;padding:28px 46px;box-shadow:0 12px 40px rgba(0,0,0,.5)}
.pill svg{width:520px;height:auto;display:block}
.cta{font-weight:800;color:#fff;font-size:74px;line-height:1.35;text-align:center;text-shadow:0 6px 24px rgba(0,0,0,.85)}
.cta b{color:#eb6f24}
.grad{position:absolute;left:0;right:0;height:900px}
`;
const pages = {
  hook: `<div class="grad" style="top:0;background:linear-gradient(rgba(10,10,25,.75),transparent)"></div>
         <div class="wrap" style="top:250px"><div class="big">درفت حقيقي</div><div class="tag">في الرياض</div></div>`,
  seat1: `<div class="grad" style="bottom:0;background:linear-gradient(transparent,rgba(10,10,25,.75))"></div>
          <div class="wrap" style="bottom:330px"><div class="tag navy">المقعد ١</div><div class="mid">قيادة الدرفت مع مدرب</div></div>`,
  seat2: `<div class="grad" style="bottom:0;background:linear-gradient(transparent,rgba(10,10,25,.75))"></div>
          <div class="wrap" style="bottom:330px"><div class="tag navy">المقعد ٢</div><div class="mid">اركب جنب كابتن محترف</div></div>`,
  adr: `<div class="wrap" style="top:820px"><div class="big" style="font-size:112px">أدرينالين بلا حدود</div></div>`,
  end: `<div style="position:absolute;inset:0;background:rgba(10,10,25,.55)"></div>
        <div class="wrap" style="top:560px;gap:60px"><div class="cta">كومنت <b>«درفت»</b><br>ونرسلك التفاصيل على الخاص</div><div class="pill">${logo}</div></div>`,
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const [k, h] of Object.entries(pages)) {
    await p.setContent(`<html><head><style>${css}</style></head><body>${h}</body></html>`);
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: `/home/user/SightScape-AI/drift-vertical/overlays/${k}.png`, omitBackground: true });
  }
  await b.close(); console.log('done');
})();
