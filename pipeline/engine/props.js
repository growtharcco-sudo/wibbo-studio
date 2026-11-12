// Props, icons and text blocks. Drawn exactly as in the first two Wibbo episodes.
// Every icon is centred on (0,0) and fits inside about 240 x 240, so it sits in a thought bubble or callout.
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const ease=x=>{x=cl(x);return x*x*(3-2*x)};
const eob=x=>{x=cl(x);const c=1.9;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
const lerp=(a,b,u)=>a+(b-a)*u, seg=(t,a,b)=>cl((t-a)/(b-a));
const sin=Math.sin,cos=Math.cos,PI=Math.PI;
const NAVY='#1d2b53', YEL='#ffd23f', TEAL='#2ec4b6', PINK='#ff7b9c', ORANGE='#ff8a3d', RED='#e63946', BLUE='#4d96ff', GREEN='#3fa34d';

function duck(p){ // local origin = body centre
  const fl=p.flap||0, bl=p.blink?0.12:1;
  return `<g>
   <ellipse cx="-118" cy="55" rx="34" ry="62" fill="#ffc21a" transform="rotate(${20+fl},-100,20)"/><ellipse cx="118" cy="55" rx="34" ry="62" fill="#ffc21a" transform="rotate(${-20-fl},100,20)"/>
   <ellipse cx="0" cy="70" rx="125" ry="108" fill="#ffd93b"/>
   <path d="M-12 -168 Q-30 -210 -2 -200 Q0 -232 22 -200 Q46 -206 26 -166Z" fill="#ffc21a"/>
   <circle cx="0" cy="-80" r="92" fill="#ffd93b"/>
   <ellipse cx="-34" cy="-98" rx="14" ry="${18*bl}" fill="#1d2b53"/><ellipse cx="34" cy="-98" rx="14" ry="${18*bl}" fill="#1d2b53"/>
   ${p.blink?'':'<circle cx="-38" cy="-104" r="5" fill="#fff"/><circle cx="30" cy="-104" r="5" fill="#fff"/>'}
   <ellipse cx="0" cy="-54" rx="44" ry="${22+10*(p.open||0)}" fill="#ff8a3d"/><path d="M-40 -54 Q0 -40 40 -54" fill="none" stroke="#d96a1f" stroke-width="5" stroke-linecap="round"/>
   <circle cx="-64" cy="-58" r="14" fill="#ff9aa8" opacity=".6"/><circle cx="64" cy="-58" r="14" fill="#ff9aa8" opacity=".6"/>
  </g>`;
}
function foot(w){return `<g transform="rotate(${w})"><rect x="-10" y="-8" width="20" height="80" rx="10" fill="#ff8a3d"/><path d="M0 60 L-46 104 Q-22 96 -14 112 Q0 98 14 112 Q22 96 46 104 Z" fill="#ff8a3d" stroke="#ff8a3d" stroke-width="10" stroke-linejoin="round"/></g>`}
function tuft(){return `<path d="M-30 6 Q-56 -70 -12 -44 Q-4 -104 22 -44 Q62 -66 34 6Z" fill="#ffd93b" stroke="#ffc21a" stroke-width="6" stroke-linejoin="round"/>`}
function star(x,y,r,rot,col='#fff'){return `<g transform="translate(${x},${y}) rotate(${rot})"><path d="M0 ${-r} L${r*0.22} ${-r*0.22} L${r} 0 L${r*0.22} ${r*0.22} L0 ${r} L${-r*0.22} ${r*0.22} L${-r} 0 L${-r*0.22} ${-r*0.22}Z" fill="${col}"/></g>`}

// ---- toothbrush kit (episode 2) ----
function brush(x,y,rot,blob){ // origin = bristle head centre, handle extends along +x
  return `<g transform="translate(${x},${y}) rotate(${rot})">
   <rect x="30" y="-14" width="250" height="28" rx="14" fill="#4d96ff"/><rect x="40" y="-14" width="230" height="9" rx="4.5" fill="#fff" opacity=".35"/>
   <rect x="-48" y="-18" width="86" height="36" rx="14" fill="#4d96ff"/>
   <g>${[-36,-22,-8,6,20].map(bx=>`<rect x="${bx}" y="-52" width="11" height="36" rx="4" fill="#fff"/><rect x="${bx}" y="-52" width="11" height="12" rx="4" fill="#9be7ff"/>`).join('')}</g>
   ${blob||''}</g>`;
}
function paste(r){ // soft-serve pile above the bristles; r = size
  if(r<=1) return '';
  if(r<22) return `<g transform="translate(-6,-60)"><circle r="${r}" fill="#e9fff6"/><circle r="${r*0.62}" cx="${-r*0.2}" cy="${-r*0.2}" fill="#7fe0c4"/></g>`;
  let g=`<g transform="translate(-6,-50)">`;
  for(const [k,dy] of [[1,0],[0.78,-0.55],[0.56,-1.0],[0.34,-1.36]]){g+=`<ellipse cx="0" cy="${dy*r}" rx="${r*k}" ry="${r*k*0.55}" fill="#e9fff6"/><path d="M${-r*k*0.9} ${dy*r} Q0 ${dy*r+r*k*0.35} ${r*k*0.9} ${dy*r}" fill="none" stroke="#7fe0c4" stroke-width="${Math.max(6,r*k*0.18)}" stroke-linecap="round"/>`;}
  g+=`<path d="M-6 ${-1.36*r-r*0.3} q10 ${-r*0.25} 22 ${-r*0.05}" fill="none" stroke="#e9fff6" stroke-width="${r*0.14}" stroke-linecap="round"/>`;
  return g+`</g>`;
}
function tube(x,y,rot,sq){return `<g transform="translate(${x},${y}) rotate(${rot})"><path d="M-70 -34 L60 -24 Q74 0 60 24 L-70 34 Z" fill="#fff" transform="scale(1,${1-0.35*sq})"/><rect x="-74" y="-36" width="14" height="72" rx="4" fill="#e63946"/><rect x="60" y="-14" width="28" height="28" rx="6" fill="#4d96ff"/><path d="M-40 -10 L30 -8" stroke="#4d96ff" stroke-width="10" stroke-linecap="round"/><path d="M-40 10 L20 9" stroke="#e63946" stroke-width="8" stroke-linecap="round"/></g>`}

// ---- the mystery egg (episode 1) ----
const EGG="M0 -280 C 150 -280 220 -60 220 60 C 220 205 122 280 0 280 C -122 280 -220 205 -220 60 C -220 -60 -150 -280 0 -280Z";
const ZIG=[[-260,-20],[-170,-70],[-110,-5],[-50,-65],[10,-5],[70,-65],[130,-5],[190,-60],[260,-20]];
function eggBody(){
  return `<path d="${EGG}" fill="#fff4dc"/>
   <g clip-path="url(#eggc)"><ellipse cx="-90" cy="-120" rx="48" ry="40" fill="#2ec4b6"/><ellipse cx="110" cy="-30" rx="40" ry="34" fill="#ff7b9c"/><ellipse cx="-120" cy="90" rx="36" ry="30" fill="#ffd23f"/>
   <ellipse cx="60" cy="170" rx="50" ry="40" fill="#2ec4b6"/><ellipse cx="40" cy="-210" rx="30" ry="26" fill="#ffd23f"/><ellipse cx="180" cy="110" rx="34" ry="30" fill="#ff7b9c"/>
   <path d="M-220 60 C-220 205 -122 280 0 280 C60 280 110 262 150 228 C60 250 -120 220 -160 20Z" fill="#f1dcb4" opacity=".55"/></g>
   <ellipse cx="-80" cy="-170" rx="34" ry="60" fill="#fff" opacity=".7" transform="rotate(24,-80,-170)"/>`;
}
const EGG_DEFS=`<clipPath id="eggc"><path d="${EGG}"/></clipPath>
   <clipPath id="topc"><path d="M-300 -400 L300 -400 L${ZIG.slice().reverse().map(q=>q.join(' ')).join(' L')} Z"/></clipPath>
   <clipPath id="botc"><path d="M-300 400 L300 400 L${ZIG.slice().reverse().map(q=>q.join(' ')).join(' L')} Z"/></clipPath>`;

// ---- icon library (thought bubbles, callouts, things Wibbo holds) ----
const ICONS={
 carrot:()=>`<g><path d="M-8 -70 Q-40 -120 -24 -70Z M0 -72 Q0 -135 14 -72Z M10 -70 Q48 -116 26 -66Z" fill="#3fa34d" stroke="#3fa34d" stroke-width="10" stroke-linejoin="round"/><path d="M-42 -66 L42 -66 Q36 20 0 96 Q-36 20 -42 -66Z" fill="#ff8a3d" stroke="#ff8a3d" stroke-width="12" stroke-linejoin="round"/><path d="M-20 -30 L6 -30 M-6 6 L20 6 M-12 40 L8 40" stroke="#d96a1f" stroke-width="7" stroke-linecap="round"/></g>`,
 bus:()=>`<g><rect x="-110" y="-62" width="220" height="112" rx="26" fill="#ffd23f"/><rect x="-92" y="-44" width="52" height="42" rx="8" fill="#cfefff"/><rect x="-28" y="-44" width="52" height="42" rx="8" fill="#cfefff"/><rect x="36" y="-44" width="56" height="42" rx="8" fill="#cfefff"/><rect x="-110" y="12" width="220" height="12" fill="#1d2b53"/><circle cx="-60" cy="54" r="26" fill="#2b2d42"/><circle cx="60" cy="54" r="26" fill="#2b2d42"/><circle cx="-60" cy="54" r="10" fill="#cbd3df"/><circle cx="60" cy="54" r="10" fill="#cbd3df"/></g>`,
 duck:()=>`<g transform="translate(0,20) scale(.5)">${duck({})}</g>`,
 pea:()=>`<g transform="scale(2.6)"><circle r="22" fill="#7cc95a"/><circle cx="-7" cy="-7" r="7" fill="#b9ec9a"/></g>`,
 egg:()=>`<g transform="scale(.36)">${eggBody()}</g>`,
 toothbrush:()=>`<g transform="translate(-62,40) rotate(-35) scale(.62)">${brush(0,0,0,paste(13))}</g>`,
 toothpaste:()=>`<g transform="scale(1.5)">${tube(0,0,-20,0)}</g>`,
 apple:()=>`<g><path d="M0 -62 Q4 -96 22 -108" fill="none" stroke="#7a4a22" stroke-width="10" stroke-linecap="round"/><path d="M8 -80 Q46 -110 66 -76 Q34 -64 8 -80Z" fill="#3fa34d"/><path d="M0 -58 C-40 -84 -96 -60 -92 0 C-88 60 -44 96 0 80 C44 96 88 60 92 0 C96 -60 40 -84 0 -58Z" fill="#e63946"/><ellipse cx="-46" cy="-24" rx="14" ry="26" fill="#fff" opacity=".45" transform="rotate(20,-46,-24)"/></g>`,
 banana:()=>`<g><path d="M-96 -40 Q-80 70 30 74 Q96 70 104 30 Q40 44 -10 20 Q-60 -4 -74 -54Z" fill="#ffd23f" stroke="#e6b400" stroke-width="8" stroke-linejoin="round"/><path d="M-96 -40 L-84 -62" stroke="#7a4a22" stroke-width="12" stroke-linecap="round"/><path d="M-60 0 Q-20 50 60 52" fill="none" stroke="#e6b400" stroke-width="6" stroke-linecap="round"/></g>`,
 ball:()=>`<g><circle r="92" fill="#ff7b9c"/><path d="M-92 0 Q0 -40 92 0" fill="none" stroke="#fff" stroke-width="16"/><path d="M-80 46 Q0 10 80 46" fill="none" stroke="#ffd23f" stroke-width="16"/><ellipse cx="-36" cy="-52" rx="20" ry="12" fill="#fff" opacity=".5" transform="rotate(-25,-36,-52)"/></g>`,
 sun:()=>`<g>${[...Array(10)].map((_,i)=>{const a=i*PI/5;return `<path d="M${70*cos(a-0.12)} ${70*sin(a-0.12)} L${108*cos(a)} ${108*sin(a)} L${70*cos(a+0.12)} ${70*sin(a+0.12)}Z" fill="#ffb21a"/>`}).join('')}<circle r="66" fill="#ffd23f"/><circle cx="-22" cy="-10" r="8" fill="#1d2b53"/><circle cx="22" cy="-10" r="8" fill="#1d2b53"/><path d="M-22 18 Q0 36 22 18" fill="none" stroke="#1d2b53" stroke-width="7" stroke-linecap="round"/></g>`,
 moon:()=>`<g><path d="M30 -96 A100 100 0 1 0 30 96 A78 78 0 1 1 30 -96Z" fill="#ffe680"/><circle cx="-40" cy="-20" r="12" fill="#f5d24a"/><circle cx="-22" cy="40" r="8" fill="#f5d24a"/></g>`,
 star:()=>`<g><path d="M0 -100 L29 -40 L95 -31 L47 15 L59 81 L0 50 L-59 81 L-47 15 L-95 -31 L-29 -40Z" fill="#ffd23f" stroke="#ffb21a" stroke-width="10" stroke-linejoin="round"/></g>`,
 heart:()=>`<g><path d="M0 84 C-70 30 -100 0 -100 -40 C-100 -80 -50 -96 0 -50 C50 -96 100 -80 100 -40 C100 0 70 30 0 84Z" fill="#ff5c7c"/><ellipse cx="-50" cy="-44" rx="16" ry="10" fill="#fff" opacity=".5" transform="rotate(-30,-50,-44)"/></g>`,
 fish:()=>`<g><path d="M60 0 L112 -46 L104 0 L112 46Z" fill="#ff8a3d"/><ellipse cx="-10" cy="0" rx="86" ry="56" fill="#4d96ff"/><circle cx="-50" cy="-12" r="12" fill="#fff"/><circle cx="-52" cy="-12" r="6" fill="#1d2b53"/><path d="M-10 -40 Q10 0 -10 40" fill="none" stroke="#9be7ff" stroke-width="8" stroke-linecap="round"/></g>`,
 cookie:()=>`<g><circle r="90" fill="#d9a066"/><circle r="90" fill="none" stroke="#b97f45" stroke-width="10"/>${[[-30,-40],[30,-26],[-44,22],[18,30],[50,-2],[-6,-6]].map(([x,y])=>`<circle cx="${x}" cy="${y}" r="11" fill="#5a3416"/>`).join('')}</g>`,
 cup:()=>`<g><path d="M-70 -70 L70 -70 L56 90 L-56 90Z" fill="#9be7ff"/><path d="M-62 -20 L62 -20 L56 90 L-56 90Z" fill="#4d96ff"/><rect x="-80" y="-84" width="160" height="20" rx="10" fill="#fff"/></g>`,
 soap:()=>`<g><rect x="-90" y="-50" width="180" height="100" rx="40" fill="#ff9ab4"/><rect x="-70" y="-36" width="140" height="22" rx="11" fill="#fff" opacity=".45"/><circle cx="64" cy="-74" r="22" fill="#fff" opacity=".85"/><circle cx="28" cy="-92" r="14" fill="#fff" opacity=".85"/></g>`,
 sock:()=>`<g><path d="M-30 -96 L40 -96 L40 30 Q40 86 -10 92 L-80 92 Q-110 92 -110 64 Q-110 36 -80 34 L-30 30Z" fill="#ff7b9c"/><rect x="-30" y="-96" width="70" height="26" fill="#fff"/><path d="M-30 -40 L40 -40" stroke="#ffd23f" stroke-width="14"/></g>`,
 shoe:()=>`<g><path d="M-100 40 L-100 -40 Q-60 -50 -40 -10 L40 10 Q100 20 104 50 L104 66 L-100 66Z" fill="#e63946"/><rect x="-104" y="56" width="212" height="22" rx="10" fill="#fff"/><path d="M-50 -14 L-20 -26 M-34 0 L-4 -12" stroke="#fff" stroke-width="7" stroke-linecap="round"/></g>`,
 book:()=>`<g><path d="M0 -60 Q-50 -86 -104 -70 L-104 80 Q-50 64 0 90 Q50 64 104 80 L104 -70 Q50 -86 0 -60Z" fill="#4d96ff"/><path d="M0 -60 Q-46 -76 -92 -62 L-92 70 Q-46 58 0 78Z" fill="#fff"/><path d="M0 -60 Q46 -76 92 -62 L92 70 Q46 58 0 78Z" fill="#f2f6ff"/><path d="M0 -60 L0 78" stroke="#1d2b53" stroke-width="5"/></g>`,
 car:()=>`<g><path d="M-110 30 L-110 -6 Q-104 -20 -80 -24 L-50 -66 L44 -66 L80 -24 Q110 -20 110 0 L110 30Z" fill="#e63946"/><path d="M-40 -56 L-6 -56 L-6 -24 L-62 -24Z M6 -56 L38 -56 L66 -24 L6 -24Z" fill="#cfefff"/><circle cx="-60" cy="34" r="26" fill="#2b2d42"/><circle cx="60" cy="34" r="26" fill="#2b2d42"/><circle cx="-60" cy="34" r="10" fill="#cbd3df"/><circle cx="60" cy="34" r="10" fill="#cbd3df"/></g>`,
 tree:()=>`<g><rect x="-16" y="20" width="32" height="80" rx="8" fill="#8a5a2b"/><circle cx="0" cy="-40" r="66" fill="#3fa34d"/><circle cx="-50" cy="0" r="46" fill="#4fae3f"/><circle cx="50" cy="0" r="46" fill="#4fae3f"/><circle cx="-24" cy="-60" r="10" fill="#e63946"/><circle cx="30" cy="-20" r="10" fill="#e63946"/></g>`,
 flower:()=>`<g><path d="M0 20 L0 104" stroke="#3fa34d" stroke-width="12" stroke-linecap="round"/><path d="M0 70 Q40 40 56 60 Q34 84 0 74Z" fill="#3fa34d"/>${[0,72,144,216,288].map(a=>`<circle cx="${42*cos((a-90)*PI/180)}" cy="${-30+42*sin((a-90)*PI/180)}" r="32" fill="#ff7b9c"/>`).join('')}<circle cy="-30" r="24" fill="#ffd23f"/></g>`,
 cake:()=>`<g><rect x="-90" y="-10" width="180" height="90" rx="14" fill="#ffb6c8"/><path d="M-90 10 Q-60 34 -30 10 Q0 34 30 10 Q60 34 90 10 L90 -10 L-90 -10Z" fill="#fff"/><rect x="-6" y="-70" width="12" height="60" rx="5" fill="#4d96ff"/><path d="M0 -96 Q14 -80 0 -70 Q-14 -80 0 -96Z" fill="#ffb21a"/><rect x="-100" y="78" width="200" height="14" rx="7" fill="#cbd3df"/></g>`,
 timer:()=>`<g transform="scale(.8)"><circle r="120" fill="#fff" stroke="#1d2b53" stroke-width="12"/><path d="M0 0 L0 -100 A100 100 0 0 1 100 0 Z" fill="#2ec4b6"/><circle r="14" fill="#1d2b53"/><rect x="-28" y="-150" width="56" height="26" rx="8" fill="#1d2b53"/></g>`,
};
function icon(name){return (ICONS[name]||ICONS.star)()}

function bubble(x,y,s,inner){return `<g transform="translate(${x},${y}) scale(${s})"><circle cx="-70" cy="205" r="16" fill="#fff"/><circle cx="-40" cy="165" r="26" fill="#fff"/><ellipse cx="20" cy="20" rx="175" ry="150" fill="#fff"/><g transform="translate(20,20)">${inner}</g></g>`}
function caption(text,u,big,y,fsBig,col){
  if(!text||u<0)return'';
  const pop=u<0.12?lerp(0.3,1.1,ease(u/0.12)):u<0.2?lerp(1.1,1,(u-0.12)/0.08):1;
  const lines=text.split('|'), fs=big?fsBig:96;
  return `<g transform="translate(540,${y}) scale(${pop})" font-family="Poppins" font-weight="700" font-size="${fs}" text-anchor="middle" stroke-linejoin="round">`+
   lines.map((l,i)=>{const yy=(i-(lines.length-1)/2)*fs*1.14+fs*0.35;
     return `<text y="${yy}" stroke="#1d2b53" stroke-width="24" fill="#1d2b53">${l}</text><text y="${yy}" fill="${col||(big?'#ffd23f':'#fff')}">${l}</text>`}).join('')+`</g>`;
}
function stamp(t,t0,y){ // NO, WIBBO! slam
  if(t<t0||t>t0+1.25) return ''; const u=seg(t,t0,t0+0.18); const s=lerp(3.2,1,ease(u))*(1+0.04*sin((t-t0)*40)*Math.exp(-(t-t0)*6));
  const o=1-ease(seg(t,t0+1.0,t0+1.25));
  return `<g transform="translate(540,${y}) rotate(-7) scale(${s})" opacity="${o*cl(u*3)}" font-family="Poppins" font-weight="700" font-size="140" text-anchor="middle" stroke-linejoin="round">
    <text y="50" stroke="#fff" stroke-width="40" fill="#fff">NO, WIBBO!</text><text y="50" stroke="#7a0f1e" stroke-width="16" fill="#e63946">NO, WIBBO!</text></g>`;
}
function popword(text,x,y,u){ // "Quack!" style sound word floating up
  return `<g transform="translate(${x},${y-60*u}) rotate(12) scale(${eob(u*3)})" opacity="${1-ease(seg(u,0.75,1))}" font-family="Poppins" font-weight="700" font-size="92" text-anchor="middle"><text stroke="#1d2b53" stroke-width="20" stroke-linejoin="round" fill="#1d2b53">${text}</text><text fill="#ffd23f">${text}</text></g>`;
}
function digit(n,u,y){
  return `<g transform="translate(540,${y}) scale(${eob(u*2.2)})" opacity="${1-ease(seg(u,0.7,1))}" font-family="Poppins" font-weight="700" font-size="300" text-anchor="middle"><text y="105" stroke="#1d2b53" stroke-width="32" stroke-linejoin="round" fill="#1d2b53">${n}</text><text y="105" fill="#ffd23f">${n}</text></g>`;
}
function timerDial(x,y,sc,u){
  return `<g transform="translate(${x},${y}) scale(${sc})"><circle r="120" fill="#fff" stroke="#1d2b53" stroke-width="12"/><path d="M0 0 L0 -100 A100 100 0 ${u>0.5?1:0} 1 ${100*sin(2*PI*Math.min(u,0.9999))} ${-100*cos(2*PI*Math.min(u,0.9999))} Z" fill="#2ec4b6"/><circle r="14" fill="#1d2b53"/><rect x="-28" y="-150" width="56" height="26" rx="8" fill="#1d2b53"/></g>`;
}
function callout(name,x,y,sc){ // white circle with an icon and a dotted tail (the pea comparison)
  const k=name==='pea'?1/2.6:0.72;
  return `<g transform="translate(${x},${y}) scale(${sc})"><circle r="${name==='pea'?60:110}" fill="#fff" stroke="#1d2b53" stroke-width="8"/><g transform="scale(${k})">${icon(name)}</g><path d="M${name==='pea'?-62:-100} 40 Q-110 70 -130 110" fill="none" stroke="#1d2b53" stroke-width="8" stroke-linecap="round" stroke-dasharray="4 16"/></g>`;
}
