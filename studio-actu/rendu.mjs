// node rendu.mjs <spec.json> <out.mp4> <workers>
import { chromium } from 'playwright';
import { spawn } from 'child_process';
import fs from 'fs'; import path from 'path';
const [specPath, out, nw='3'] = process.argv.slice(2);
const spec = JSON.parse(fs.readFileSync(specPath,'utf8'));
const FPS = spec.fps||30, N = Math.round(spec.duree*FPS), W = +nw;
const dir = path.dirname(new URL(import.meta.url).pathname);
const exe = process.env.CHROME || ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].find(p=>fs.existsSync(p));
const html = fs.readFileSync(path.join(dir,'gabarit.html'),'utf8').replace('<script>',`<script>window.SPEC=${JSON.stringify(spec)};</script><script>`);
const page = path.join(dir, `_page_${path.basename(path.dirname(path.resolve(out)))}_${path.basename(out)}.html`); fs.writeFileSync(page, html);
const segs=[];
await Promise.all([...Array(W).keys()].map(async w=>{
  const a=Math.floor(N*w/W), b=Math.floor(N*(w+1)/W), seg=`${out}.part${w}.mp4`; segs[w]=seg;
  const br=await chromium.launch(exe?{executablePath:exe,args:['--allow-file-access-from-files']}:{args:['--allow-file-access-from-files']});
  const p=await br.newPage({viewport:{width:1080,height:1920}});const cdp=await p.context().newCDPSession(p);
  p.on('pageerror',e=>console.error('ERR',e.message));
  await p.goto('file://'+page); await p.evaluate(()=>document.fonts.ready);
  const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-vf','noise=alls=3:allf=t','-c:v','libx264','-preset','faster','-crf','18','-maxrate','7M','-bufsize','14M','-pix_fmt','yuv420p','-r',String(FPS),seg],{stdio:['pipe','inherit','inherit']});
  for(let f=a;f<b;f++){await p.evaluate(f=>window.seek(f),f);const buf=Buffer.from((await cdp.send('Page.captureScreenshot',{format:'jpeg',quality:92,optimizeForSpeed:true})).data,'base64');if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await br.close();
}));
fs.writeFileSync(out+'.list', segs.map(s=>`file '${path.resolve(s)}'`).join('\n'));
await new Promise(r=>spawn('ffmpeg',['-v','error','-y','-f','concat','-safe','0','-i',out+'.list','-c','copy',out],{stdio:'inherit'}).on('close',r));
segs.forEach(s=>fs.unlinkSync(s)); fs.unlinkSync(out+'.list'); if(!process.env.KX_GARDER) fs.unlinkSync(page);
