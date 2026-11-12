function bop(p){
  const sx=p.sx||1, sy=p.sy||1, lx=(p.lookX||0)*7, ly=(p.lookY||0)*6, m=p.talk||0, mood=p.mood||'calm';
  const eyeR = mood==='shock'?13:(mood==='sad'?8:10);
  const eyeW = mood==='shock'?22:19;
  let pup = p.blink?`<rect x="${-31+lx}" y="${-78+ly}" width="16" height="4" rx="2" fill="#1a1a1a"/><rect x="${15+lx}" y="${-78+ly}" width="16" height="4" rx="2" fill="#1a1a1a"/>`
     :`<circle cx="${-23+lx}" cy="${-74+ly}" r="${eyeR}" fill="#1a1a1a"/><circle cx="${23+lx}" cy="${-74+ly}" r="${eyeR}" fill="#1a1a1a"/><circle cx="${-27+lx}" cy="${-79+ly}" r="3.5" fill="#fff"/><circle cx="${19+lx}" cy="${-79+ly}" r="3.5" fill="#fff"/>`;
  if(mood==='joy'&&!p.blink) pup=`<path d="M-36 -72 Q-23 -90 -10 -72" fill="none" stroke="#1a1a1a" stroke-width="7" stroke-linecap="round"/><path d="M10 -72 Q23 -90 36 -72" fill="none" stroke="#1a1a1a" stroke-width="7" stroke-linecap="round"/>`;
  const brow={calm:[0,0,-104],happy:[-6,6,-106],shock:[-8,8,-114],sad:[18,-18,-100],sus:[-16,16,-98],joy:[-6,6,-108]}[mood];
  const brows=`<rect x="-36" y="-4" width="26" height="7" rx="3.5" fill="#14564f" transform="translate(0,${brow[2]+4}) rotate(${brow[0]},-23,0)"/><rect x="10" y="-4" width="26" height="7" rx="3.5" fill="#14564f" transform="translate(0,${brow[2]+4}) rotate(${brow[1]},23,0)"/>`;
  let mouth;
  if(m>0.06) mouth=`<ellipse cx="0" cy="${-42+4*m}" rx="${9+5*m}" ry="${3+12*m}" fill="#7a2d2d"/><ellipse cx="0" cy="${-38+8*m}" rx="${5+2*m}" ry="${1+4*m}" fill="#ff8fa3"/>`;
  else if(mood==='happy'||mood==='joy') mouth=`<path d="M-15 -50 Q0 -24 15 -50Z" fill="#7a2d2d"/>`;
  else if(mood==='shock') mouth=`<ellipse cx="0" cy="-40" rx="11" ry="14" fill="#7a2d2d"/>`;
  else if(mood==='sad') mouth=`<path d="M-13 -36 Q0 -48 13 -36" fill="none" stroke="#14564f" stroke-width="5" stroke-linecap="round"/>`;
  else if(mood==='sus') mouth=`<path d="M-12 -44 L12 -46" fill="none" stroke="#14564f" stroke-width="5" stroke-linecap="round"/>`;
  else mouth=`<path d="M-12 -48 Q0 -38 12 -48" fill="none" stroke="#14564f" stroke-width="5" stroke-linecap="round"/>`;
  const ant=(p.ant||0)+(p.droop||0);
  const arm=(side,a)=>`<g transform="translate(${side*58},-62) rotate(${side*-a})"><ellipse cx="${side*8}" cy="22" rx="13" ry="24" fill="#1b998b"/></g>`;
  return `<g transform="scale(${sx},${sy})">
   <g transform="translate(0,-112) rotate(${ant})"><path d="M0 0 Q${4+(p.droop||0)*0.3} -26 14 -50" fill="none" stroke="#1b998b" stroke-width="8" stroke-linecap="round"/><circle cx="16" cy="-56" r="15" fill="#ffd23f"/><circle cx="11" cy="-61" r="5" fill="#fff6c2"/></g>
   ${arm(-1,p.armL||0)}${arm(1,p.armR||0)}
   <ellipse cx="-26" cy="-6" rx="18" ry="10" fill="#1b998b"/><ellipse cx="26" cy="-6" rx="18" ry="10" fill="#1b998b"/>
   <ellipse cx="0" cy="-62" rx="64" ry="58" fill="#2ec4b6"/>
   <ellipse cx="0" cy="-36" rx="38" ry="24" fill="#9df0e4"/>
   <ellipse cx="-30" cy="-98" rx="16" ry="8" fill="#7fe3d8" opacity=".7" transform="rotate(-25,-30,-98)"/>
   <circle cx="-23" cy="-76" r="${eyeW}" fill="#fff"/><circle cx="23" cy="-76" r="${eyeW}" fill="#fff"/>
   ${pup}${brows}
   <circle cx="-46" cy="-50" r="9" fill="#ff7b9c" opacity=".45"/><circle cx="46" cy="-50" r="9" fill="#ff7b9c" opacity=".45"/>
   ${mouth}
  </g>`;
}
