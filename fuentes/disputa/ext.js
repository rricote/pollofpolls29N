const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const out={};
for(const [name,f] of [['hoy','index.html'],['tend','tendencia.html']]){const p=await b.newPage();await p.goto('file:///mnt/user-data/outputs/'+f);await p.waitForTimeout(9000);
out[name]=await p.evaluate(()=>{ window.__P=D.parties;
 const N=5000, NJp=D.prov.length; const BL=['PP','VOX'].map(k=>KI[k]);
 const bh=D.prov.map(p=>new Uint32Array(p.seats+1)); let c=0; const orig=dhondt;
 dhondt=function(s,seats,o){orig(s,seats,o); if(c>=NJp){const j=(c-NJp)%NJp; let t=0;BL.forEach(k=>t+=o[k]); bh[j][t]++} c++;};
 const o=Object.assign({},st.o,{nsim:N}); const S=simulate(st.A.T,o,st.A.Tsep); dhondt=orig;
 const T=st.A.T;
 return {N:S.N,T:Object.fromEntries(KEYS.map((k,i)=>[k,T[i]])),
  groups:S.groups.map(g=>({id:g.id,label:g.label,mean:g.mean,p176:g.p176})),
  seatsNat:Object.fromEntries(KEYS.slice(0,16).map((k,i)=>[k,S.seats[i].mean])),
  prov:D.prov.map((p,j)=>({id:p.id,name:p.name,seats:p.seats,ccaa:p.ccaa,
   hist:Object.fromEntries(KEYS.slice(0,16).map((k,i)=>[k,Array.from(S.hist[j][i])]).filter(([k,h])=>h.slice(1).some(x=>x>0))),
   bh:Array.from(bh[j]), cent:S.cent[j].slice(0,16), sh:Array.from(S.shMean[j]).map(x=>+x.toFixed(4))}))}});
 }
fs.writeFileSync('disputa.json',JSON.stringify({parties:null,data:out}));
console.log(Object.keys(out), out.hoy.prov.length, out.hoy.groups.map(g=>g.id+':'+g.mean.toFixed(0)+'/'+g.p176.toFixed(2)).join(' '));
await b.close()})();
