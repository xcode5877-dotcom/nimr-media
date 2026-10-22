// Generic kinetic reel engine — NMD / Nimr Masalha style
(function(){
const C = window.CFG;
const st = document.getElementById('stage');
const $ = id => document.getElementById(id);
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const p=(t,a,b)=>clamp((t-a)/(b-a));
const eo=x=>1-Math.pow(1-x,3);
const eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const back=x=>{const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2)};
function rise(el,t,a,d=0.45,dist=80){const k=eo(p(t,a,a+d));el.style.opacity=k;el.style.transform=`translateY(${(1-k)*dist}px)`;}
function pop(el,t,a,d=0.4,from=1.5){const x=p(t,a,a+d);const k=back(x);el.style.opacity=clamp(x*3);el.style.transform=`scale(${from+(1-from)*k})`;}
const NAVYBG='radial-gradient(ellipse 900px 1200px at 50% 40%,#1D3A66 0%,#13294B 50%,#0B1A33 100%)';
let t0=0; const scenes=[];
C.scenes.forEach((s,i)=>{
  const id='sc'+i; const d=s.dur; const a=t0; t0+=d;
  let html='';
  if(s.type==='hook'){
    html=`<div class="scene" id="${id}" style="background:${NAVYBG}">
      <div class="abs" id="${id}g1" style="top:-300px;left:140px;width:4px;height:1500px;transform:rotate(28deg);background:linear-gradient(180deg,rgba(240,210,140,0),#F0D28C 50%,rgba(240,210,140,0));box-shadow:0 0 26px 5px rgba(240,200,120,.45)"></div>
      <div class="abs" id="${id}g2" style="top:900px;right:70px;width:3px;height:1200px;transform:rotate(28deg);background:linear-gradient(180deg,rgba(240,210,140,0),#E8C77E 50%,rgba(240,210,140,0));box-shadow:0 0 20px 4px rgba(240,200,120,.35)"></div>
      <div class="abs" aria-hidden="true" id="${id}bg" style="top:260px;left:0;right:0;text-align:center;font-family:Alex;font-weight:900;font-size:900px;line-height:1;color:rgba(230,199,127,.07)">${s.bg||'؟'}</div>
      <div class="zone" style="top:${s.top||820}px">${s.lines.map((l,j)=>`<span class="line h" id="${id}l${j}" style="font-size:${l.size}px;line-height:1.2;margin-top:${j?24:0}px;color:${l.color||'#fff'}">${l.t}</span>`).join('')}</div></div>`;
  } else if(s.type==='point'){
    html=`<div class="scene" id="${id}" style="background:#F4EEE4">
      <div class="zone" style="top:600px">
        <span class="line h" id="${id}n" style="font-size:${s.label?84:230}px;line-height:1;color:#C9A24E;font-weight:900">${s.label||s.n}</span>
        <span class="line h" id="${id}t" style="margin-top:44px;font-size:90px;line-height:1.2;color:#13294B">${s.title}</span>
        <span class="line" id="${id}u" style="margin:36px auto 0;width:140px;height:7px;background:#C9A24E;border-radius:4px"></span>
        <span class="line" id="${id}b" style="margin-top:34px;font-size:50px;line-height:1.5;font-weight:500;color:#3A4A66">${s.body}</span>
      </div></div>`;
  } else if(s.type==='cta'){
    html=`<div class="scene" id="${id}" style="background:radial-gradient(ellipse 1000px 1300px at 50% 30%,#1D3A66 0%,#13294B 48%,#0B1A33 100%)">
      <div class="abs" id="${id}logo" style="top:270px;left:375px;width:330px;height:112px;overflow:hidden"><img src="nm_mark.png" style="width:330px;height:112px;object-fit:contain"></div>
      <div class="abs" id="${id}halo" style="top:330px;left:190px;width:700px;height:700px;border-radius:50%;background:radial-gradient(circle,rgba(230,199,127,.35) 0%,rgba(230,199,127,0) 62%)"></div>
      <div class="abs" id="${id}arc" style="top:400px;left:265px;width:550px;height:550px;border-radius:50%;border:4px solid rgba(230,199,127,.75)"></div>
      <div class="abs" id="${id}ph" style="top:390px;left:240px;width:600px;height:640px;-webkit-mask-image:radial-gradient(ellipse 50% 52% at 50% 44%,#000 62%,rgba(0,0,0,0) 100%)"><img src="lawyer.jpg" style="width:600px;height:640px;object-fit:cover;object-position:50% 0%"></div>
      <div class="zone" style="top:1010px"><span class="line h" id="${id}a" style="font-size:74px;color:#E6C77F">المحامي نمر مصالحة</span>
        <span class="line" id="${id}b" style="margin-top:6px;font-size:38px;font-weight:500;color:#fff">${s.sub||'مكتب محاماة · <span class="he">משרד עורכי דין</span>'}</span></div>
      <div class="abs" id="${id}c" style="top:1185px;left:90px;right:120px;display:flex;flex-direction:column;align-items:center;gap:22px">
        <div style="font-size:44px;font-weight:600;color:#fff">${s.q}</div>
        <div style="display:flex;align-items:center;gap:22px;padding:24px 54px;border-radius:999px;background:linear-gradient(180deg,#F0D697,#C9A24E 60%,#A8823A)">
          <svg width="58" height="58" viewBox="0 0 24 24" fill="none" stroke="#0B1A33" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8.5 8.5 0 0 1-12.6 7.4L3 21l1.6-5.2A8.5 8.5 0 1 1 21 12z"/></svg>
          <span class="h" style="font-size:70px;color:#0B1A33;direction:ltr">054-334-5123</span></div></div>
      <div class="zone" id="${id}d" style="top:1440px;font-size:23px;line-height:1.6;color:#AEB8CA">${C.disc}</div></div>`;
  }
  st.insertAdjacentHTML('beforeend',html);
  scenes.push({id,a,b:t0,s});
});
st.insertAdjacentHTML('beforeend','<div class="wipe" id="wipe" style="display:none"><div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,0) 0%,rgba(0,0,0,0) 42%,#A8823A 45%,#F6E3A8 50%,#A8823A 55%,rgba(0,0,0,0) 58%,rgba(0,0,0,0) 100%)"></div></div>');
const D=t0, W=0.5;
function render(t){
  scenes.forEach((S,i)=>{const el=$(S.id);
    el.style.display=(t>=S.a-(i?W/2:0)&&t<S.b+W/2)?'block':'none'; el.style.zIndex=i;
    if(i>0){const k=eio(p(t,S.a-W/2,S.a+W/2)); el.style.clipPath=k>=1?'none':`polygon(${100-k*130}% 0,100% 0,100% 100%,${100-k*130+30}% 100%)`;}
    const s=S.s, a=S.a, id=S.id;
    if(s.type==='hook'){ const kg=eo(p(t,a,a+0.8)); $(id+'g1').style.clipPath=`inset(0 0 ${100-kg*100}% 0)`; $(id+'g2').style.clipPath=`inset(${100-kg*100}% 0 0 0)`; $(id+'bg').style.transform=`scale(${1.25-0.25*eo(p(t,a,a+2.5))})`; s.lines.forEach((l,j)=>{ const el2=$(id+'l'+j); if(j===0||l.pop) pop(el2,t,a+0.05+j*0.3,0.4,l.pop||1.3); else rise(el2,t,a+0.1+j*0.35,0.4,60);}); }
    if(s.type==='point'){ pop($(id+'n'),t,a+0.2,0.45,0.5); rise($(id+'t'),t,a+0.45); const ku=eo(p(t,a+0.8,1.2+a)); $(id+'u').style.width=(140*ku)+'px'; rise($(id+'b'),t,a+0.95,0.45,40);}
    if(s.type==='cta'){ const kl=eio(p(t,a+0.2,a+0.8)); $(id+'logo').style.clipPath=`inset(0 0 0 ${100-kl*100}%)`;
      const kp=eo(p(t,a+0.2,a+1.1)); $(id+'ph').style.opacity=kp; $(id+'ph').style.transform=`translateY(${(1-kp)*120}px) scale(${1.08-0.08*kp})`;
      $(id+'halo').style.opacity=eo(p(t,a+0.3,a+1.3)); const ka=eo(p(t,a+0.6,a+1.4)); $(id+'arc').style.opacity=ka; $(id+'arc').style.clipPath=`inset(0 0 ${100-ka*55}% 0)`;
      rise($(id+'a'),t,a+1.1,0.45,50); rise($(id+'b'),t,a+1.35,0.45,40); pop($(id+'c'),t,a+1.8,0.5,0.8); rise($(id+'d'),t,a+2.3,0.4,20);}
  });
  const w=$('wipe'); let on=false;
  for(let i=1;i<scenes.length;i++){const a=scenes[i].a-W/2,b=scenes[i].a+W/2; if(t>=a&&t<=b){on=true;const k=eio(p(t,a,b));w.style.display='block';w.style.zIndex=50;w.style.transform=`translateX(${1080-k*2700}px) skewX(-16deg)`;}}
  if(!on) w.style.display='none';
}
// sound cue list, mirrors the animation timings above
const CUES=[];
scenes.forEach((S,i)=>{const s=S.s,a=S.a;
  if(i>0) CUES.push({t:a,k:'wipe'});
  if(s.type==='hook'){ CUES.push({t:a,k:'shimmer'}); s.lines.forEach((l,j)=>{ if(j===0||l.pop) CUES.push({t:a+0.05+j*0.3+0.12,k:(l.pop&&l.pop>=1.6)?'impact':'pop'}); else CUES.push({t:a+0.1+j*0.35,k:'swoosh'});}); }
  if(s.type==='point'){ CUES.push({t:a+0.32,k:'thud'}); CUES.push({t:a+0.45,k:'swoosh'}); CUES.push({t:a+0.8,k:'zip'}); CUES.push({t:a+0.95,k:'tick'}); }
  if(s.type==='cta'){ CUES.push({t:a+0.2,k:'shimmer'}); CUES.push({t:a+0.6,k:'riser'}); CUES.push({t:a+1.1,k:'swoosh'}); CUES.push({t:a+1.95,k:'pop'}); CUES.push({t:a+1.95,k:'chime'}); }
});
window.render=render; window.DURATION=D; window.CUES=CUES; window.BOUNDS=scenes.slice(1).map(s=>s.a);
if(!location.search.includes('capture')){const s0=performance.now();(function loop(){const t=((performance.now()-s0)/1000)%(D+1);render(Math.min(t,D));requestAnimationFrame(loop)})();} else render(0);
})();
