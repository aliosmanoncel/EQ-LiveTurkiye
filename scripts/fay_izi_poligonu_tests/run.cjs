// Fay İzinden Sismik Araştırma Poligonu (Fault-Trace-Based Zonation) — geometri regresyon testleri (2026-11-23)
// Kullanım: node scripts/fay_izi_poligonu_tests/run.cjs [--out sonuc.json]
// Kod index.html'den doğrudan çıkarılır (tek kaynak): geometri bloğu, alan (areaKm2) ve üyelik (pointInPolys) işlevleri.
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.resolve(__dirname, '..', '..'), HTML = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const between = (a, b) => { const i = HTML.indexOf(a), j = HTML.indexOf(b, i); if (i < 0 || j < 0) throw new Error('index.html içinde blok bulunamadı: ' + a); return HTML.slice(i, j); };
const fnSrc = name => { const i = HTML.indexOf('function ' + name + '('); if (i < 0) throw new Error('işlev yok: ' + name); let d = 0, k = HTML.indexOf('{', i);
  for (let j = k; j < HTML.length; j++) { if (HTML[j] === '{') d++; else if (HTML[j] === '}') { d--; if (!d) return HTML.slice(i, j + 1); } } };
const ctx = { console, Math, JSON, Set, Map, Uint8Array, Infinity, isFinite, Number };
ctx.geodesic = require(path.join(ROOT, 'vendor', 'geographiclib-geodesic-2.2.0.min.js'));
ctx.polygonClipping = require(path.join(ROOT, 'vendor', 'polygon-clipping-0.15.7.umd.min.js'));
vm.createContext(ctx);
vm.runInContext(between('const AREA_METHOD = ', '// Bölge Karşılaştırma, G–R Oran/Yoğunluk') + '\n' + fnSrc('pointInPolygon') + '\n' + fnSrc('pointInPolys') + '\n' +
  between('// ══ Fay Geometrisine Uyumlu Sismik Zonlama', '// ── Fay İzinden Araştırma Poligonu: iz çizimi') +
  '\nthis.K = { korZone, korWidth, korLengths, korMergeLines }; this.areaKm2 = areaKm2; this.pointInPolys = pointInPolys;', ctx);
const PC = ctx.polygonClipping, G = ctx.geodesic, K = ctx.K, s = { areaKm2: ctx.areaKm2 };
const DATA = path.join(ROOT, 'data', 'turkiye_diri_fay_mta2026.geojson');
const g=G.Geodesic.WGS84, A=r=>s.areaKm2({type:'MultiPolygon',polys:r.polys});
const out={}; const ok=(name,cond,info)=>{out[name]={gecti:!!cond,...info}; console.log((cond?'GEÇTİ ':'KALDI ')+name, JSON.stringify(info));};
const dense=(line,st=0.05)=>{const o=[];for(let i=0;i+1<line.length;i++){const l=g.InverseLine(line[i][0],line[i][1],line[i+1][0],line[i+1][1]);const n=Math.max(1,Math.ceil(l.s13/1000/st));for(let k=0;k<n;k++){const p=l.Position(l.s13*k/n);o.push([p.lat2,p.lon2]);}}o.push(line[line.length-1]);return o;};
// noktanın çizgiye en kısa jeodezik uzaklığı (km) ve en yakın noktanın uç olup olmadığı
const near=(pt,D)=>{let b=1e9,bi=-1;for(let i=0;i<D.length;i++){const d=g.Inverse(pt[0],pt[1],D[i][0],D[i][1]).s12/1000;if(d<b){b=d;bi=i;}}return {d:b,end:bi<20||bi>D.length-21,i:bi};   /* uçlara 1 km'den yakın en yakın noktalar (düz uç kenarı) hariç */};
const side=(pt,D,i)=>{const j=Math.min(i,D.length-2),a=D[j],b=D[j+1];return Math.sign((b[1]-a[1])*(pt[0]-a[0])-(b[0]-a[0])*(pt[1]-a[1]));}; // +1 sol(üst) lon-lat düzleminde
// 1) KAF
const f=JSON.parse(fs.readFileSync(DATA)).features.filter(x=>x.properties.fay_adi==='KUZEY ANADOLU FAY ZONU');
const kaf=f.flatMap(x=>(x.geometry.type==='MultiLineString'?x.geometry.coordinates:[x.geometry.coordinates]).map(l=>l.map(([lo,la])=>[la,lo])));
let t=Date.now(); const r1=K.korZone(kaf,{W:20,cap:'yuvarlak'},PC,g); const ms1=Date.now()-t, a1=A(r1);
ok('1_KAF_W20_yuvarlak', Math.abs(a1-52599.5)/52599.5<0.005, {A:+a1.toFixed(1),ref:52599.5,farkYuzde:+((a1-52599.5)/52599.5*100).toFixed(3),ms:ms1,parca:r1.polys.length,delik:r1.polys.reduce((t,p)=>t+p.length-1,0),Ltoplam:+r1.Lsum.toFixed(1),Lbirlesik:+r1.Luni.toFixed(1),zincir:r1.nChains,dallanma:r1.branchNodes,maxOlcek:+r1.maxScale.toFixed(5)});
t=Date.now(); const r1d=K.korZone(kaf,{W:20,cap:'duz'},PC,g); const a1d=A(r1d);
const r1a=K.korZone(kaf,{W:20,cap:'duz',p:0.5000001},PC,g); const a1a=A(r1a);
ok('1b_KAF_duz_uc_ve_asimetrik_yol_tutarliligi', a1d<a1 && Math.abs(a1a-a1d)/a1d<0.001, {A_duz_simetrik:+a1d.toFixed(1),A_duz_asimetrikYol:+a1a.toFixed(1),farkYuzde:+((a1a-a1d)/a1d*100).toFixed(3),uc_farki_km2:+(a1-a1d).toFixed(1),ms:Date.now()-t});
// 2) Düz çizgi simetrisi (meridyen, 100 km yaklaşık) W=20
const st=[[39.55,30.0],[40.45,30.0]]; const Dst=dense(st); const Lst=g.Inverse(...st[0],...st[1]).s12/1000;
for (const cap of ['duz','yuvarlak']) { const r=K.korZone([st],{W:20,cap},PC,g); const a=A(r); const ds={u:[],a:[]};
  for(const p of r.polys[0][0]){const n=near(p,Dst); if(n.end) continue; (side(p,Dst,n.i)>0?ds.u:ds.a).push(n.d);}
  const mm=v=>[+Math.min(...v).toFixed(4),+Math.max(...v).toFixed(4)]; const exp=cap==='duz'?Lst*20:Lst*20+Math.PI*100;
  ok('2_duz_cizgi_simetri_'+cap, Math.abs(Math.min(...ds.u)-10)<0.02&&Math.abs(Math.max(...ds.u)-10)<0.02&&Math.abs(Math.min(...ds.a)-10)<0.02&&Math.abs(Math.max(...ds.a)-10)<0.02&&Math.abs(a-exp)/exp<0.003, {L:+Lst.toFixed(3),A:+a.toFixed(2),beklenen:+exp.toFixed(2),ust_uzaklik:mm(ds.u),alt_uzaklik:mm(ds.a)}); }
// 2b) asimetrik p=0,75 → üst 15, alt 5; alan W·L değişmez (düz uç)
{ const r=K.korZone([st],{W:20,p:0.75},PC,g); const a=A(r); const ds={u:[],a:[]};
  for(const p of r.polys[0][0]){const n=near(p,Dst); if(n.end) continue; (side(p,Dst,n.i)>0?ds.u:ds.a).push(n.d);}
  const mm=v=>[+Math.min(...v).toFixed(4),+Math.max(...v).toFixed(4)];
  // meridyende S→N yönlendirme: üst = batı (sol). side>0 = lon-lat düzleminde sol = batı.
  ok('2b_asimetrik_p075', Math.abs(Math.max(...ds.u)-15)<0.03&&Math.abs(Math.min(...ds.u)-15)<0.03&&Math.abs(Math.max(...ds.a)-5)<0.03&&Math.abs(a-Lst*20)/(Lst*20)<0.003, {A:+a.toFixed(2),beklenen:+(Lst*20).toFixed(2),ust_bati_uzaklik:mm(ds.u),alt_dogu_uzaklik:mm(ds.a)}); }
// 3) Eğrisel fay: 60 km yarıçaplı 120° yay (merkez 39°K 35°D), W=20 düz uç → alan = W·L (yay ofseti), tüm sınır noktaları 10 km
{ const arc=[]; for(let k=0;k<=240;k++){const az=-60+120*k/240; const p=g.Direct(39,35,az,60000); arc.push([p.lat2,p.lon2]);} const D=dense(arc,0.05);
  let L=0; for(let i=0;i+1<arc.length;i++) L+=g.Inverse(...arc[i],...arc[i+1]).s12/1000;
  const r=K.korZone([arc],{W:20},PC,g); const a=A(r); const d=[]; for(const p of r.polys[0][0]){const n=near(p,D); if(!n.end) d.push(n.d);}
  ok('3_egrisel_geometri', Math.abs(Math.min(...d)-10)<0.05&&Math.abs(Math.max(...d)-10)<0.05&&Math.abs(a-L*20)/(L*20)<0.005&&r.polys.length===1&&r.polys[0].length===1, {L:+L.toFixed(3),A:+a.toFixed(2),beklenen_WL:+(L*20).toFixed(2),farkYuzde:+((a-L*20)/(L*20)*100).toFixed(3),sinir_uzaklik:[+Math.min(...d).toFixed(4),+Math.max(...d).toFixed(4)],n:d.length}); }
// 4) Paralel kollar: 5 km aralıklı iki paralel iz (D–B, 80 km), W=20 → tek parça, alan < iki ayrı alanın toplamı, ≈ (W+5)·L
{ const a0=[[40,30],[40,30.94]]; const p1=g.Direct(40,30,0,5000), p2=g.Direct(40,30.94,0,5000); const b0=[[p1.lat2,p1.lon2],[p2.lat2,p2.lon2]];
  const ra=K.korZone([a0],{W:20},PC,g), rb=K.korZone([b0],{W:20},PC,g), rab=K.korZone([a0,b0],{W:20},PC,g);
  const L=g.Inverse(...a0[0],...a0[1]).s12/1000, A_a=A(ra), A_b=A(rb), A_ab=A(rab), exp=L*25;
  ok('4_paralel_kollar_birlesimi', rab.polys.length===1&&A_ab<A_a+A_b&&Math.abs(A_ab-exp)/exp<0.01, {parca:rab.polys.length,A_birlesik:+A_ab.toFixed(1),A_ayri_toplam:+(A_a+A_b).toFixed(1),beklenen_yaklasik:+exp.toFixed(1),Ltoplam:+rab.Lsum.toFixed(2),Lbirlesik:+rab.Luni.toFixed(2)}); }
// 5) Kesişen parçalar: X (iki 100 km iz, 40°K 32°D'de kesişir), W=20 düz uç → tek parça, alan = 2·W·L − kesişim(≈W²/sin90=400)
{ const c=[40,32]; const e=(az)=>{const p=g.Direct(...c,az,50000);return [p.lat2,p.lon2];}; const l1=[e(225),c,e(45)], l2=[e(315),c,e(135)];
  const r=K.korZone([l1,l2],{W:20},PC,g); const a=A(r); const L1=2*50, exp=2*20*L1-400;
  const bad=r.polys.flat(2).some(q=>!isFinite(q[0])||!isFinite(q[1]));
  ok('5_kesisen_parcalar', r.polys.length===1&&!bad&&Math.abs(a-exp)/exp<0.01, {parca:r.polys.length,delik:r.polys[0].length-1,A:+a.toFixed(1),beklenen:exp,farkYuzde:+((a-exp)/exp*100).toFixed(3),zincir:r.nChains,dallanma:r.branchNodes,Ltoplam:+r.Lsum.toFixed(2),Lbirlesik:+r.Luni.toFixed(2)});
  // tekrar eden parça: aynı iz iki kez seçilirse L_birleşik değişmez, alan değişmez
  const rr=K.korZone([l1,l1.slice().reverse()],{W:20},PC,g), r0=K.korZone([l1],{W:20},PC,g);
  ok('5b_ayni_parca_iki_kez', Math.abs(rr.Luni-r0.Luni)<1e-9&&Math.abs(rr.Lsum-2*r0.Lsum)<1e-6&&Math.abs(A(rr)-A(r0))<0.01, {Ltoplam:+rr.Lsum.toFixed(3),Lbirlesik:+rr.Luni.toFixed(3),A_iki_kez:+A(rr).toFixed(3),A_tek:+A(r0).toFixed(3)}); }
// 6) Sabit ve orantılı W ayrı doğrulama
{ const w1=K.korWidth({mode:'sabit',W:20},123), w2=K.korWidth({mode:'oranli',k:0.2,Wmin:5,Wmax:50},100), w3=K.korWidth({mode:'oranli',k:0.2,Wmin:5,Wmax:50},10), w4=K.korWidth({mode:'oranli',k:0.2,Wmin:5,Wmax:50},1000);
  const L=g.Inverse(...st[0],...st[1]).s12/1000, wr=K.korWidth({mode:'oranli',k:0.2,Wmin:5,Wmax:50},L), r=K.korZone([st],{W:wr.W},PC,g), a=A(r);
  ok('6_sabit_ve_oranli_W', w1.W===20&&w1.raw===null&&w2.W===20&&!w2.clamped&&w3.W===5&&w3.clamped==='min'&&w4.W===50&&w4.clamped==='max'&&Math.abs(a-L*wr.W)/(L*wr.W)<0.003,
    {sabit:w1,oranli_L100:w2,oranli_L10:w3,oranli_L1000:w4,duz_cizgi:{L:+L.toFixed(3),W_kL:+wr.W.toFixed(3),A:+a.toFixed(2),beklenen:+(L*wr.W).toFixed(2)}}); }
// 7) Sorgu uyumu (çevrimdışı kısım): üyelik pointInPolys ile — dik 9 km içeride, 11 km dışarıda (W = 20 km); alan areaKm2 ile
{ const tr=[[40.60,29.00],[40.70,29.40],[40.72,29.80]]; const r=K.korZone([tr],{W:20},PC,g), PL=r.polys.map(rs=>rs.map(q=>q.map(([a,b])=>({lat:a,lng:b})))); let inn=0,outn=0,n=0;
  for (let i=0;i+1<tr.length;i++) for (const f of [0.25,0.5,0.75]) { const l=g.InverseLine(...tr[i],...tr[i+1]); const q=l.Position(l.s13*f); const az=q.azi2;
    for (const sd of [90,-90]) { const a=g.Direct(q.lat2,q.lon2,az+sd,9000), b=g.Direct(q.lat2,q.lon2,az+sd,11000); n++;
      if (ctx.pointInPolys(a.lat2,a.lon2,PL)) inn++; if (!ctx.pointInPolys(b.lat2,b.lon2,PL)) outn++; } }
  ok('7_sorgu_uyelik_cevrimdisi', inn===n&&outn===n, {n, ic_9km_icinde:inn, dis_11km_disinda:outn, A:+A(r).toFixed(2), not:'Canlı EMSC/USGS/AFAD ve VS30 uyumu tarayıcı testinde (PR raporu)'}); }
const oi = process.argv.indexOf('--out'); if (oi > 0) fs.writeFileSync(process.argv[oi + 1], JSON.stringify(out, null, 1));
const np=Object.values(out).filter(x=>x.gecti).length, nt=Object.keys(out).length; console.log('Toplam', np+'/'+nt); if (np!==nt) process.exit(1);
