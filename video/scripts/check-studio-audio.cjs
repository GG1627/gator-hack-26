const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/gael8/AppData/Local/npm-cache/_npx/31e32ef8478fbf80/node_modules/playwright');
const fs=require('node:fs');
const path=require('node:path');
(async()=>{
 const b=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'C:/Users/gael8/AppData/Local/ms-playwright/chromium-1247/chrome-win64/chrome.exe',args:['--autoplay-policy=no-user-gesture-required']});
 const p=await b.newPage({viewport:{width:1920,height:1080}});const errors=[],assets=[];
 p.on('pageerror',e=>errors.push(e.message));
 p.on('response',r=>{if(/\/audio\//.test(r.url()))assets.push({url:r.url().split('/audio/')[1].split('?')[0],status:r.status()});});
 await p.addInitScript(()=>{
  window.__audioMeters=[];
  const connect=AudioNode.prototype.connect;
  AudioNode.prototype.connect=function(destination,...args){
   if(destination instanceof AudioDestinationNode){const meter=this.context.createAnalyser();meter.fftSize=2048;window.__audioMeters.push(meter);connect.call(this,meter,...args);connect.call(meter,destination);return destination;}
   return connect.call(this,destination,...args);
  };
 });
 await p.goto('http://localhost:3001/Peekaboo-Submission');await p.waitForTimeout(2000);
 await p.getByRole('button',{name:'Play',exact:true}).click();
 let peak=0,rms=0;const samples=[];
 for(let i=0;i<24;i++){
  await p.waitForTimeout(700);
  const s=await p.evaluate(()=>window.__audioMeters.map(a=>{const d=new Float32Array(a.fftSize);a.getFloatTimeDomainData(d);return {state:a.context.state,peak:Math.max(...d.map(Math.abs)),rms:Math.sqrt(d.reduce((n,x)=>n+x*x,0)/d.length)};}));
  for(const x of s){peak=Math.max(peak,x.peak);rms=Math.max(rms,x.rms);}samples.push(s);
 }
 await p.getByRole('button',{name:'Pause',exact:true}).click();
 await p.screenshot({path:path.resolve(__dirname,'../.cache/voiced-studio.png')});
 const report={errors,assets,peak,rms,samples,check:'Browser audio signal sampling; not a final encoded loudness measurement'};
 fs.writeFileSync(path.resolve(__dirname,'../.cache/studio-audio-check.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({errors,audioAssets:assets.length,failedAssets:assets.filter(x=>x.status>=400),peak,rms}));
 await b.close();
 if(errors.length||assets.some(x=>x.status>=400)||peak===0)process.exitCode=1;
})();
