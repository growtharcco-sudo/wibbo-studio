// The two looks the channel uses. Each set is a background plus fixed positions for Wibbo and text.
// "mystery" = the sky and grass of episode 1 (mystery egg). "tries" = the bathroom of episode 2 (brushing teeth).
const W=1080,H=1920;
const SETS={
 mystery:{ZX:245, ZY:1430, S:1.95, capY:250, capBig:120, stampY:430, digitY:470, bubble:[250,820], callout:[820,760], timer:[850,760],
   EX:640, EY:1060, shadow:'#2f6b2a', shadowRx:85, shadowRy:17, shadowDy:70, pk:[130,90,60,190,80,110,60,12,95,330,26,20,true], bob:12,
   bg(t){ let g=`<defs><radialGradient id="bg" cx=".5" cy=".5" r=".75"><stop offset="0" stop-color="#8fe3ff"/><stop offset="1" stop-color="#38a8f0"/></radialGradient>
     <linearGradient id="gr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fd66a"/><stop offset="1" stop-color="#4fae3f"/></linearGradient>${EGG_DEFS}</defs>`;
     g+=`<rect x="-30" y="-30" width="${W+60}" height="${H+60}" fill="url(#bg)"/>`;
     for(let i=0;i<16;i++){const a=i/16*2*PI+t*0.12; g+=`<path d="M540 1000 L${540+1700*cos(a)} ${1000+1700*sin(a)} L${540+1700*cos(a+0.2)} ${1000+1700*sin(a+0.2)}Z" fill="#fff" opacity=".10"/>`;}
     g+=`<path d="M-30 1420 Q270 1330 540 1400 Q820 1470 1110 1380 L1110 1950 L-30 1950Z" fill="url(#gr)"/>`;
     for(const [fx,fy,col] of [[120,1560,'#ff7b9c'],[930,1520,'#ffd23f'],[470,1640,'#fff'],[820,1700,'#ff7b9c']])
       g+=`<g transform="translate(${fx},${fy})">`+[0,72,144,216,288].map(a=>`<circle cx="${20*cos(a*PI/180)}" cy="${20*sin(a*PI/180)}" r="15" fill="${col}"/>`).join('')+`<circle r="11" fill="#f4a020"/></g>`;
     return g; }},
 tries:{ZX:430, ZY:1500, S:2.7, capY:260, capBig:118, stampY:470, digitY:470, bubble:[330,700], callout:[820,760], timer:[850,760],
   shadow:'#000', shadowRx:150, shadowRy:26, shadowDy:12, shadowOp:.15, pk:[170,120,80,240,90,140,70,13,120,560,32,24,false], bob:10, lookX:0.6, lookY:0, duckXY:[965,1175],
   bg(t){ let g=`<defs><linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bfeff0"/><stop offset="1" stop-color="#9fe0e6"/></linearGradient>
     <linearGradient id="mir" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eaf9ff"/><stop offset="1" stop-color="#bfe6f5"/></linearGradient>
     <pattern id="tiles" width="120" height="120" patternUnits="userSpaceOnUse"><rect width="120" height="120" fill="none"/><path d="M120 0 L0 0 0 120" fill="none" stroke="#ffffff" stroke-width="6" opacity=".55"/></pattern>${EGG_DEFS}</defs>`;
     g+=`<rect x="-30" y="-30" width="${W+60}" height="1560" fill="url(#wall)"/><rect x="-30" y="-30" width="${W+60}" height="1560" fill="url(#tiles)"/>`;
     g+=`<rect x="-30" y="1500" width="${W+60}" height="460" fill="#f6d7a7"/><rect x="-30" y="1500" width="${W+60}" height="22" fill="#e2b77a"/>`;
     for(let i=0;i<10;i++) g+=`<rect x="${i*120-30}" y="1522" width="6" height="420" fill="#e9c48f"/>`;
     g+=`<rect x="650" y="560" width="380" height="470" rx="60" fill="#fff"/><rect x="668" y="578" width="344" height="434" rx="46" fill="url(#mir)"/><path d="M720 640 L800 600 M720 700 L860 620" stroke="#fff" stroke-width="14" stroke-linecap="round" opacity=".8"/>`;
     g+=`<rect x="610" y="1230" width="520" height="70" rx="20" fill="#fff"/><rect x="640" y="1300" width="460" height="330" rx="16" fill="#ffd9a8"/><rect x="680" y="1340" width="170" height="250" rx="14" fill="#ffc98a"/><rect x="890" y="1340" width="170" height="250" rx="14" fill="#ffc98a"/><circle cx="830" cy="1465" r="10" fill="#e2a25f"/><circle cx="910" cy="1465" r="10" fill="#e2a25f"/>`;
     g+=`<rect x="840" y="1150" width="30" height="85" rx="10" fill="#c9d6e3"/><path d="M855 1150 Q855 1110 815 1110 L790 1110" fill="none" stroke="#c9d6e3" stroke-width="26" stroke-linecap="round"/>`;
     g+=`<rect x="700" y="1150" width="70" height="85" rx="14" fill="#ff7b9c"/><rect x="700" y="1150" width="70" height="20" rx="10" fill="#ff9ab4"/>`;
     return g; }},
};
