const $=s=>document.querySelector(s), nf=(x,d=0)=>x.toLocaleString('es-ES',{minimumFractionDigits:d,maximumFractionDigits:d}), pc=x=>nf(x*100,0)+' %';
const PN={}; DS.parties.forEach(p=>PN[p.k]=p.name);
const st={esc:'hoy',thr:.75,all:false,sel:null,tab:'prov',par:'PP'};
const BLK=['PP','VOX'];
function cls(P){ // clasifica los escaños de una provincia
  const N=P.N, M=P.seats, ps=.95, pp=st.thr, out={sure:[],prob:[],cand:[],M};
  const cnt={}; let A=0;
  for(const k in P.hist){const h=P.hist[k]; let tail=0; const ge=[]; for(let s=h.length-1;s>=1;s--){tail+=h[s]; ge[s]=tail/N}
    let j=0; while(j+1<h.length && ge[j+1]>=pp) j++; cnt[k]=j;
    for(let s=1;s<=j;s++){ (ge[s]>=ps?out.sure:out.prob).push({k,n:s,p:ge[s]}); A++ }
    for(let s=j+1;s<h.length;s++) if(ge[s]>=.04) out.cand.push({k,n:s,p:ge[s]}) }
  out.A=A; out.E=Math.max(0,M-A); out.cnt=cnt; out.cand.sort((a,b)=>b.p-a.p);
  // bloque PP+Vox
  const bh=P.bh; let tail=0, bg=[]; for(let s=bh.length-1;s>=1;s--){tail+=bh[s]; bg[s]=tail/N}
  let bs=0; while(bs+1<bh.length && bg[bs+1]>=pp) bs++;
  let nb=0; for(const k in cnt) if(!BLK.includes(k)) nb+=cnt[k];
  out.bs=bs; out.nb=nb; out.chg=Math.max(0,Math.min(out.E, M-bs-nb)); out.duel=out.E-out.chg;
  out.bnext=bs+1<=M?bg[bs+1]||0:0; out.bmean=bh.reduce((a,x,i)=>a+x*i,0)/N;
  return out;
}
function draw(){
  const D0=DS.data[st.esc]; const rows=D0.prov.map(P=>({P:{...P,N:D0.N},c:cls({...P,N:D0.N})}));
  const tot=rows.reduce((a,r)=>{a.sure+=r.c.sure.length;a.prob+=r.c.prob.length;a.E+=r.c.E;a.chg+=r.c.chg;a.duel+=r.c.duel;a.bs+=r.c.bs;a.np+=r.c.E>0?1:0;a.nchg+=r.c.chg>0?1:0;return a},{sure:0,prob:0,E:0,chg:0,duel:0,bs:0,np:0,nchg:0});
  const g=D0.groups.find(x=>x.id==='pp_vox');
  $('#headline').textContent=`${tot.E} escaños siguen en juego en ${tot.np} provincias`;
  $('#sub').innerHTML=`${st.esc==='hoy'?'Con la media de encuestas de hoy':'Si la tendencia sigue hasta el 29-N'}, <b>${tot.sure+tot.prob}</b> de los 350 escaños salen casi seguros (<b>${tot.sure}</b>) o probables (<b>${tot.prob}</b>) en nuestras ${nf(D0.N)} simulaciones. De los <b>${tot.E}</b> restantes, <b>${tot.chg}</b> pueden cambiar de bloque (PP+Vox frente al resto) y <b>${tot.duel}</b> se juegan dentro de un mismo bloque. PP y Vox suman <b>${tot.bs}</b> escaños seguros o probables, ${tot.bs>=176?`<b>${tot.bs-176} más</b> que`:`<b>${176-tot.bs} menos</b> que`} la mayoría de 176, y llegan a ella en <b>${pc(g.p176)}</b> de las simulaciones. No es una predicción.`;
  // barra
  const W=[['sure',tot.sure,'Seguros (≥95 %)'],['prob',tot.prob,`Probables (≥${pc(st.thr)})`],['dis',tot.E,'En juego']];
  $('#bar').innerHTML=`<div class="sbar" role="img" aria-label="Seguros ${tot.sure}, probables ${tot.prob}, en juego ${tot.E}">`+W.map(([c,v])=>`<span class="s-${c}" style="flex:${v}">${v}</span>`).join('')+`</div>`;
  $('#legend').innerHTML=W.map(([c,v,l])=>`<span><i class="sw s-${c}"></i>${l}</span>`).join('');
  const lead=`<div><b>${tot.chg}</b><span>escaños pueden cambiar de bloque, en ${tot.nchg} provincias</span></div><div><b>${tot.duel}</b><span>se juegan dentro del mismo bloque (PP-Vox, PSOE-FA, nacionalistas…)</span></div><div><b>${tot.bs+tot.chg}</b><span>escaños que PP y Vox tendrían como máximo con todo lo disputado a su favor</span></div><div><b>${tot.bs>=176?'+'+(tot.bs-176):176-tot.bs}</b><span>${tot.bs>=176?'de margen sobre 176 contando solo escaños seguros o probables de PP y Vox':'escaños disputados que necesitan ganar PP y Vox para llegar a 176'}</span></div>`;
  $('#kpis').innerHTML=lead;
  // mapa
  const col=n=>n===0?['var(--track)',1]:n===1?['#f4b183',1]:n===2?['#e8793a',1]:['#b8430e',1];
  const byId={}; rows.forEach(r=>byId[r.P.id]=r);
  let h='',sq='',tx='';
  Object.keys(MAP.paths).forEach(id=>{const r=byId[id];if(!r)return;const [c]=col(r.c.E);h+=`<path data-id="${id}" tabindex="0" role="button" aria-label="${r.P.name}: ${r.c.E} escaños en juego" class="${id===st.sel?'sel':''}" d="${MAP.paths[id]}" style="fill:${c}"><title>${r.P.name}: ${r.c.E} de ${r.P.seats} en juego</title></path>`});
  Object.keys(MAP.sq).forEach(id=>{const r=byId[id];if(!r)return;const [c]=col(r.c.E),[x,y,s]=MAP.sq[id];sq+=`<rect data-id="${id}" tabindex="0" role="button" aria-label="${r.P.name}: ${r.c.E} escaños en juego" class="sqr${id===st.sel?' sel':''}" x="${x}" y="${y}" width="${s}" height="${s}" rx="4" style="fill:${c}"><title>${r.P.name}: ${r.c.E} de ${r.P.seats} en juego</title></rect><text x="${x+s/2}" y="${y+s/2}" class="ml">${r.c.E||''}</text>`});
  Object.keys(MAP.lab).forEach(id=>{const r=byId[id];if(!r||!r.c.E)return;tx+=`<text class="ml" x="${MAP.lab[id][0]}" y="${MAP.lab[id][1]}">${r.c.E}</text>`});
  const b=MAP.box;
  $('#map').innerHTML=`<svg class="mapsvg" viewBox="0 0 ${MAP.w} ${MAP.h}" role="group" aria-label="Escaños en juego por provincia">${h}${tx}${sq}<rect class="bx" x="${b[0]}" y="${b[1]}" width="${b[2]-b[0]}" height="${b[3]-b[1]}" rx="6"/><text class="bt" x="${b[0]+8}" y="${b[1]+16}">Canarias</text></svg>`;
  $('#maplg').innerHTML=[0,1,2,3].map(n=>`<span><i class="sw" style="background:${col(n)[0]}"></i>${n===3?'3 o más':n+(n===1?' escaño':' escaños')}</span>`).join('');
  $('#mapnote').textContent='Número de escaños que no son seguros ni probables. Pulsa una provincia para ver el detalle.';
  document.querySelectorAll('#map [data-id]').forEach(e=>{const f=()=>{st.sel=e.dataset.id;draw();const t=document.getElementById('r-'+st.sel);if(t){t.open=true;t.scrollIntoView({block:'nearest',behavior:'smooth'})}};e.onclick=f;e.onkeydown=ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();f()}}});
  // lista
  let L=rows.slice().sort((a,b)=>b.c.E-a.c.E||b.c.chg-a.c.chg||a.P.name.localeCompare(b.P.name,'es'));
  if(!st.all) L=L.filter(r=>r.c.E>0);
  $('#lh').textContent=st.all?'Las 52 provincias':`${L.length} provincias con escaños en juego`;
  const chip=(x,t)=>`<span class="chp ${t}" style="--c:var(--c-${x.k},var(--c-OTROS))" title="${PN[x.k]||x.k}${x.n>1?' · escaño n.º '+x.n:''}">${PN[x.k]||x.k}${t==='dis'?' '+pc(x.p):''}</span>`;
  $('#list').innerHTML=L.map(r=>{const c=r.c,P=r.P;
    const seats=[...c.sure.map(x=>chip(x,'sure')),...c.prob.map(x=>chip(x,'prob'))].join('');
    const dis=c.E?`<div class="dis"><b>${c.E} en juego</b> · candidatos: ${c.cand.slice(0,c.E+3).map(x=>chip(x,'dis')).join('')}</div>`:'';
    const blk=c.E?`<div class="blk">${c.chg?`<b>${c.chg}</b> ${c.chg===1?'puede':'pueden'} cambiar de bloque (PP+Vox ${c.bs} seguros o probables; ${pc(c.bnext)} de que tengan al menos ${c.bs+1}).`:'Todo se juega dentro de un mismo bloque.'}</div>`:'';
    return `<details class="pv${P.id===st.sel?' on':''}" id="r-${P.id}" ${P.id===st.sel?'open':''}><summary><span class="pn">${P.name}</span><span class="ps">${P.seats} esc.</span><span class="pd">${c.E?`<b>${c.E}</b> en juego`:'<span class="muted">cerrada</span>'}</span></summary><div class="in"><div class="sr"><span class="lb">Seguros y probables</span><span>${seats||'—'}</span></div>${dis}${blk}</div></details>`}).join('');

  // vista de partidos
  const PA={};
  rows.forEach(r=>{const c=r.c,nm=r.P.name;
    const add=(k,t,x)=>{(PA[k]=PA[k]||{sure:0,prob:[],cand:[],mean:0}); if(t==='sure')PA[k].sure++; else PA[k][t].push({...x,prov:nm,id:r.P.id})};
    c.sure.forEach(x=>add(x.k,'sure',x)); c.prob.forEach(x=>add(x.k,'prob',x)); c.cand.forEach(x=>{if(x.p>=.1)add(x.k,'cand',x)});
    r.P.cent.forEach((v,i)=>{});
  });
  const nat=D0.seatsNat;
  const order=Object.keys(PA).sort((a,b)=>(nat[b]||0)-(nat[a]||0));
  $('#ptab').innerHTML=`<thead><tr><th>Partido</th><th>Media</th><th>Seguros</th><th>Probables (pueden perderse)</th><th>Candidatos (pueden ganarse)</th></tr></thead><tbody>`+order.map(k=>{const a=PA[k];return `<tr data-k="${k}" class="${k===st.par?'on':''}" tabindex="0"><td><i class="sw" style="background:var(--c-${k},var(--c-OTROS))"></i>${PN[k]||k}</td><td>${nf(nat[k]||0,0)}</td><td>${a.sure}</td><td>${a.prob.length}</td><td>${a.cand.length}</td></tr>`}).join('')+`</tbody>`;
  document.querySelectorAll('#ptab tbody tr').forEach(e=>{const f=()=>{st.par=e.dataset.k;draw()};e.onclick=f;e.onkeydown=ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();f()}}});
  const A=PA[st.par]||{sure:0,prob:[],cand:[]};
  const line=(x,t)=>`<div class="pl"><span class="pn2">${x.prov}${x.n>1?` <small>(${x.n}.º escaño)</small>`:''}</span><span class="pb"><i style="width:${Math.round(x.p*100)}%;background:var(--c-${st.par},var(--c-OTROS))"></i></span><span class="pp">${pc(x.p)}</span></div>`;
  $('#pdet').innerHTML=`<h3><i class="sw" style="background:var(--c-${st.par},var(--c-OTROS))"></i>${PN[st.par]||st.par}: ${nf(nat[st.par]||0,0)} escaños de media</h3><div class="pcols"><div><h4>Puede perder (${A.prob.length})</h4><p class="muted">Escaños probables que no llegan al 95 %.</p>${A.prob.sort((a,b)=>a.p-b.p).map(x=>line(x)).join('')||'<p class="muted">Ninguno.</p>'}</div><div><h4>Puede ganar (${A.cand.length})</h4><p class="muted">Escaños que hoy no son suyos ni probables pero tiene al menos un 10 % de conseguir.</p>${A.cand.sort((a,b)=>b.p-a.p).map(x=>line(x)).join('')||'<p class="muted">Ninguno.</p>'}</div></div><p class="muted">Además tiene ${A.sure} escaños seguros (≥95 %).</p>`;
}
document.querySelectorAll('input[name=esc]').forEach(r=>r.onchange=()=>{st.esc=r.value;draw()});
document.querySelectorAll('input[name=lst]').forEach(r=>r.onchange=()=>{st.all=r.value==='1';draw()});
$('#thr').onchange=e=>{st.thr=+e.target.value;draw()};
function setTab(t){st.tab=t;$('#p-prov').hidden=t!=='prov';$('#p-par').hidden=t!=='par';['prov','par'].forEach(x=>{const b=$('#tab-'+x);b.setAttribute('aria-selected',x===t);b.tabIndex=x===t?0:-1})}
$('#tab-prov').onclick=()=>setTab('prov');$('#tab-par').onclick=()=>setTab('par');
draw();
