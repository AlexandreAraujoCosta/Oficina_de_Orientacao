(() => {
  const px = v => Math.round(parseFloat(v));
  const cs = el => getComputedStyle(el);
  const lum = c => { const [r,g,b] = c.match(/\d+/g).map(Number).map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)}); return .2126*r+.7152*g+.0722*b; };
  const contraste = (fg,bg) => { const a=lum(fg), b=lum(bg); const [hi,lo]=a>b?[a,b]:[b,a]; return +(((hi+.05)/(lo+.05)).toFixed(2)); };
  const bg = cs(document.body).backgroundColor;

  // largura de linha do texto corrido
  const paras = [...document.querySelectorAll('p')].filter(p => p.textContent.trim().length > 200);
  const larguras = paras.map(p => p.getBoundingClientRect().width);
  const chw = (() => { const s=document.createElement('span'); s.textContent='0'.repeat(100); s.style.cssText='position:absolute;visibility:hidden'; document.body.appendChild(s); const w=s.getBoundingClientRect().width/100; s.remove(); return w; })();

  // caixas: cada combinacao de borda/fundo distinta
  const caixas = {};
  document.querySelectorAll('div,section,article,aside,p,dl').forEach(el => {
    const s = cs(el);
    const tem = s.borderLeftWidth !== '0px' || s.borderWidth !== '0px' || (s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== bg);
    if (!tem || el.getBoundingClientRect().height < 20) return;
    const k = [s.backgroundColor, s.borderTopWidth+' '+s.borderTopColor, s.borderLeftWidth+' '+s.borderLeftColor, s.borderRadius].join(' | ');
    (caixas[k] = caixas[k] || {n:0, ex:''}).n++;
    if (!caixas[k].ex) caixas[k].ex = (el.className||el.tagName)+'';
  });

  const tit = {};
  ['h1','h2','h3','h4'].forEach(t => { const e=document.querySelector(t); if (e) tit[t] = px(cs(e).fontSize)+'px '+cs(e).fontFamily.split(',')[0]+' '+cs(e).fontWeight; });

  const cores = new Set();
  document.querySelectorAll('p,li,dd,dt,span,h1,h2,h3,b,strong').forEach(e => { if (e.textContent.trim()) cores.add(cs(e).color); });

  return {
    corpo: px(cs(document.body).fontSize)+'px/'+cs(document.body).lineHeight+' '+cs(document.body).fontFamily.split(',')[0],
    alturaDoc: Math.round(document.documentElement.scrollHeight),
    paragrafos: paras.length,
    larguraTextoPx: [Math.round(Math.min(...larguras)), Math.round(Math.max(...larguras))],
    larguraTextoCh: [Math.round(Math.min(...larguras)/chw), Math.round(Math.max(...larguras)/chw)],
    titulos: tit,
    caixasDistintas: Object.entries(caixas).map(([k,v]) => v.n+'x '+v.ex+'  ['+k+']'),
    coresDeTexto: [...cores],
    contrasteMenor: Math.min(...[...cores].map(c => contraste(c, bg))),
    links: (() => { const a=document.querySelector('main a, .wrap a'); return a ? cs(a).color+' '+cs(a).textDecorationLine : null; })(),
  };
})()
