/* Interactive, offline text-engine and software-factory diagrams. */
function drawAtlas(container, options) {
  const ns = 'http://www.w3.org/2000/svg';
  const { layers, mode, onLayer, onOp, onRole, onEdge } = options;
  const idOf = value => typeof value === 'string' ? value : value?.id;
  const selectedLayer = layers.find(x => x.id === idOf(options.layer));
  const selectedOp = selectedLayer?.ops.find(x => x.id === idOf(options.op));
  const groupNames = [...new Set(selectedLayer?.ops.map(o=>o.group).filter(Boolean) || [])];
  const activeGroup = selectedOp?.group || (groupNames.includes(options.group) ? options.group : '');
  const groupKey = g => '@group/'+g;
  const openGroup = group => options.onGroup ? options.onGroup(selectedLayer.id,group) : drawAtlas(container,{...options,op:'',role:'',group});
  const selectedRole = idOf(options.role);
  const uid = 'ax' + (drawAtlas.serial = (drawAtlas.serial || 0) + 1);
  const trace = options.trace || {};
  const traced = new Set(Array.isArray(trace) || trace instanceof Set ? trace : [...(trace.layers || []), ...(trace.ops || [])]);
  const tracedEdges = new Set((Array.isArray(trace.edges) ? trace.edges : []).map(e => e.slice(0, 2).join('|')));
  const html = (tag, cls, text) => {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    if (text !== undefined) el.textContent = text;
    return el;
  };
  const svgEl = (parent, tag, attrs = {}, text) => {
    const el = document.createElementNS(ns, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    if (text !== undefined) el.textContent = text;
    parent.append(el);
    return el;
  };
  const button = (parent, text, action, cls) => {
    const b = html('button', cls || '', text);
    b.type = 'button'; b.onclick = action; parent.append(b); return b;
  };
  function bind(g, label, action) {
    g.setAttribute('tabindex', '0'); g.setAttribute('role', 'button');
    g.setAttribute('aria-label', label); svgEl(g, 'title', {}, label);
    g.addEventListener('click', action);
    g.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); action(); }
    });
  }
  function lines(value, limit, max = 2) {
    const s = String(value || ''), words = s.split(/\s+/), out = [];
    for (const word of words) {
      if (!out.length || out.at(-1).length + word.length + 1 > limit) out.push(word);
      else out[out.length - 1] += ' ' + word;
    }
    if (out.length > max) {
      out.length = max; out[max - 1] = out[max - 1].replace(/[,;:·]$/, '') + '…';
    }
    return out;
  }
  const stripLevel = s => String(s).replace(/^(?:L[0-6]|M)\s*(?:[·:|–—-]\s*|\s+)/i, '');
  const levelNames = { startup: 'L0', interface: 'L1', schedule: 'L2', generate: 'L3', model: 'L4', backend: 'L5', state: 'M', host: 'L6' };
  const palette = mode === 'factory' || layers.every(x => x.id.startsWith('f_')) ? 'factory' : 'engine';
  const getCC = v => typeof v === 'string' ? v : v?.id;
  const coreLayer = id => layers.find(x => x.id === id);
  const overlayName = typeof options.overlay === 'string' ? options.overlay : '';
  const showBindings = overlayName && Array.isArray(options.bindings) && options.bindings.some(x => x.engine === overlayName);
  const bindingCounts = new Map();
  if (showBindings) {
    const byCC = new Map();
    for(const row of options.bindings)if(row.engine === overlayName)byCC.set(row.assigned,(byCC.get(row.assigned)||0)+1);
    for(const [id,n] of byCC)bindingCounts.set(id,n);
    for(const l of layers) {
      const jobs=new Set();
      for(const op of l.ops) {
        const cc=op.cc.map(getCC);
        cc.forEach(id=>jobs.add(id));
        bindingCounts.set(l.id+'/'+op.id,cc.reduce((n,id)=>n+(byCC.get(id)||0),0));
      }
      bindingCounts.set(l.id,[...jobs].reduce((n,id)=>n+(byCC.get(id)||0),0));
    }
  }
  const rawEdges = options.edges || [];
  const width = 1000;
  container.replaceChildren();
  const shell = html('div', 'ax-atlas ax-' + palette);
  container.append(shell);
  const crumb = html('div', 'ax-breadcrumb');
  shell.append(crumb);
  const rootTitle = palette === 'factory' ? 'Software factory' : 'Inference engine';
  if (selectedLayer) button(crumb, rootTitle, () => onLayer?.(''), 'ax-back');
  else crumb.append(html('strong', '', rootTitle));
  if (selectedLayer) {
    crumb.append(html('span', 'ax-divider', '›'));
    if (selectedOp || activeGroup) button(crumb, stripLevel(selectedLayer.title), () => options.onGroup ? options.onGroup(selectedLayer.id,'') : (activeGroup&&!selectedOp?openGroup(''):onLayer?.(selectedLayer.id)), 'ax-back');
    else crumb.append(html('strong', '', stripLevel(selectedLayer.title)));
  }
  if (activeGroup) {
    crumb.append(html('span','ax-divider','›'));
    if(selectedOp)button(crumb,activeGroup,()=>openGroup(activeGroup),'ax-back');
    else crumb.append(html('strong','',activeGroup));
  }
  if (selectedOp) {
    crumb.append(html('span', 'ax-divider', '›'));
    crumb.append(html('strong', '', selectedOp.title));
  }
  const viewport = html('div', 'ax-viewport'); shell.append(viewport);
  const canvas = svgEl(viewport, 'svg', { class: 'ax-canvas', role: 'group', 'aria-label': selectedOp?.title || selectedLayer?.title || rootTitle, preserveAspectRatio: 'xMinYMin meet' });
  const defs = svgEl(canvas, 'defs');
  ['call', 'state', 'platform', 'build', 'feedback', 'trace'].forEach(kind => {
    const marker = svgEl(defs, 'marker', { id: uid + '-' + kind, viewBox: '0 0 10 8', refX: 9, refY: 4, markerWidth: 8, markerHeight: 7, orient: 'auto-start-reverse', markerUnits: 'userSpaceOnUse' });
    svgEl(marker, 'path', { d: 'M0,0 L10,4 L0,8 Z', class: 'ax-fill-' + kind });
  });
  const back = svgEl(canvas, 'g'), wires = svgEl(canvas, 'g'), blocks = svgEl(canvas, 'g'), labels = svgEl(canvas, 'g');
  const drawn = [];
  const region = (x, y, w, h, title, cls) => {
    svgEl(back, 'rect', { x, y, width: w, height: h, rx: 13, class: 'ax-region ' + (cls || '') });
    svgEl(back, 'text', { x: x + 17, y: y + 24, class: 'ax-region-title' }, title);
  };
  function wire(a, b, label, path, x, y, kind = 'call', span = 190, showLabel = true) {
    const active = tracedEdges.has([a,b].join('|')) || (traced.has(a) && traced.has(b));
    const edgeKind = active ? 'trace' : kind;
    const g = svgEl(wires, 'g', { class: 'ax-wire ax-wire-' + edgeKind, 'data-from': a, 'data-to': b });
    svgEl(g, 'path', { class: 'ax-line', d: path, 'marker-end': 'url(#' + uid + '-' + edgeKind + ')' });
    svgEl(g, 'path', { class: 'ax-line-hit', d: path });
    const act = () => onEdge?.(a, b, label);
    bind(g, a + ' → ' + b + ' · ' + label, act);
    let badge;
    if (showLabel) {
      const txt = lines(label, Math.floor(span / 6.7), 2), w = Math.min(span + 8, Math.max(24, Math.max(...txt.map(t => t.length)) * 6.9 + 15));
      badge = svgEl(labels, 'g', { class: 'ax-edge-label ax-label-' + edgeKind, 'data-from': a, 'data-to': b, 'aria-hidden': 'true' });
      svgEl(badge, 'rect', { x: x - w/2, y: y - txt.length*7 - 3, width: w, height: txt.length*14 + 6, rx: 4 });
      txt.forEach((s, i) => svgEl(badge, 'text', { x, y: y - (txt.length-1)*7 + i*14 + 4.2, 'text-anchor':'middle' }, s));
      badge.addEventListener('click', act);
    }
    drawn.push({ a, b, label, g, badge });
  }
  function markBinding(g,id,x,y) {
    if (!showBindings) return;
    const n=bindingCounts.get(id)||0;
    const badge=svgEl(g,'g',{class:'ax-overlay-badge '+(n?'ax-bound':'ax-unbound')});
    svgEl(badge,'circle',{cx:x,cy:y,r:4.6});
    svgEl(badge,'title',{},overlayName+' · '+n+' source examples linked through CCs');
  }
  function node({ id, title, x, y, w, h, code, sub, tone, onClick, selected, cc = false }) {
    const g = svgEl(blocks, 'g', { class: ['ax-node', 'ax-node-' + (tone || 'operation'), selected ? 'ax-selected' : '', traced.has(id) ? 'ax-traced' : ''].join(' '), 'data-ax-id': id });
    bind(g, title + (code ? ' · ' + code : '') + (sub ? ' · ' + sub : ''), onClick);
    svgEl(g, 'rect', { x, y, width:w, height:h, rx:9, class:'ax-box' });
    const qualified=id.includes('/')&&!id.startsWith('@group/');
    const bindingKey = selectedLayer && !qualified && !cc && !levelNames[id] && !coreLayer(id) ? selectedLayer.id+'/'+id : id;
    markBinding(g,bindingKey,x+w-12,y+12);
    const px = x + 14, titleWidth = w - 35;
    const lineLen = Math.floor(titleWidth / (cc ? 7.8 : 8.1));
    const titleLines = lines(title, lineLen, sub ? 1 : 3);
    let yy = y + (code ? 17 : (h - titleLines.length*17)/2);
    if (code) { svgEl(g, 'text', { x:px, y:yy, class:'ax-node-code' }, code); yy += 20; }
    else yy += 14;
    titleLines.forEach(t => {
      const line=svgEl(g, 'text', { x:px,y:yy,class:cc?'ax-node-title ax-cc-title':'ax-node-title' }, t);
      if(cc&&t.length*7.9>titleWidth){line.setAttribute('textLength',titleWidth);line.setAttribute('lengthAdjust','spacingAndGlyphs')}
      yy += 17;
    });
    if (sub) lines(sub, Math.floor(titleWidth/6.7), Math.max(1, Math.floor((y+h-yy)/15)+1)).forEach(t => { svgEl(g,'text',{x:px,y:yy,class:'ax-node-sub'},t); yy+=15; });
    const emphasis = enabled => {
      for(const edge of drawn) {
        const faded = enabled && edge.a !== id && edge.b !== id;
        edge.g.classList.toggle('ax-muted',faded); edge.badge?.classList.toggle('ax-muted',faded);
      }
    };
    g.addEventListener('mouseenter',()=>emphasis(true)); g.addEventListener('mouseleave',()=>emphasis(false));
    g.addEventListener('focus',()=>emphasis(true)); g.addEventListener('blur',()=>emphasis(false));
    return g;
  }
  const finish = height => {
    canvas.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
    canvas.style.aspectRatio = width + ' / ' + height;
  };
  function kindFor(a,b,k) {
    const s = String(k || '').toLowerCase();
    if (a==='host' || b==='host' || /hardware|host|platform/.test(s)) return 'platform';
    if (a==='state' || b==='state' || /read|write|state|memory/.test(s)) return 'state';
    return /feedback|return|loop/.test(s) ? 'feedback' : 'call';
  }
  function engineOverview() {
    const seq = ['startup','interface','schedule','generate','model','backend'].map(coreLayer).filter(Boolean);
    if (!seq.length || !coreLayer('state') || !coreLayer('host')) return operationMap(layers,rawEdges,'layer');
    const mainX=133, mainW=397, boxH=66, pitch=103, startY=48;
    const pos = new Map(seq.map((s,i)=>[s.id,{x:mainX,y:startY+i*pitch,w:mainW,h:boxH}]));
    const mem=coreLayer('state'),host=coreLayer('host'),sideX=724,sideW=251;
    const floor = startY+(seq.length-1)*pitch+boxH;
    const hostY=floor+76;
    region(12,6,976,floor+14,'ENGINE IMAGE');
    region(12,hostY-37,976,122,'TARGET ENVIRONMENT','ax-region-platform');
    pos.set('state',{x:sideX,y:startY,w:sideW,h:floor-startY});
    pos.set('host',{x:mainX,y:hostY,w:mainW,h:65});
    let left=0,right=0;
    const statePorts=new Map(), pairCounts=new Map();
    for(const [a,b,label,k] of rawEdges) {
      const A=pos.get(a), B=pos.get(b); if(!A||!B)continue;
      const kind=kindFor(a,b,k),xA=A.x+A.w/2,xB=B.x+B.w/2,yA=A.y+A.h/2,yB=B.y+B.h/2;
      const count=pairCounts.get(a+'|'+b)||0;pairCounts.set(a+'|'+b,count+1);
      if(a==='state'||b==='state') {
        const peer=a==='state'?b:a, p=pos.get(peer), num=statePorts.get(peer)||0;statePorts.set(peer,num+1);
        const yp=p.y+p.h/2+(num%3-0.5)*17,ys=Math.min(floor-8,Math.max(startY+10,yp));
        const xn=p.x+p.w, xm=(xn+sideX)/2;
        const path=a==='state'?`M${sideX},${ys} H${xm} V${yp} H${xn+2}`:`M${xn},${yp} H${xm} V${ys} H${sideX-2}`;
        wire(a,b,label,path,xm,(yp+ys)/2,kind,164);
      } else if(b==='host' || a==='host') {
        const fromTop=b==='host',p=fromTop?A:B,x=fromTop?p.x+p.w-15:p.x+19;
        if(p.y===pos.get(seq.at(-1).id).y){
          wire(a,b,label,fromTop?`M${x},${p.y+p.h} V${hostY-2}`:`M${x},${hostY} V${p.y+p.h+2}`,x,floor+23,kind,180);
        }else{
          const track=85-(left++%5)*12;
          wire(a,b,label,`M${A.x},${yA} H${track} V${yB} H${B.x-2}`,69,(yA+yB)/2,kind,112);
        }
      }else if(B.y-A.y===pitch && !count){
        wire(a,b,label,`M${xA},${A.y+A.h} V${B.y-2}`,xA,(A.y+A.h+B.y)/2,kind,290);
      }else{
        const forward=B.y>A.y,track=forward?Math.min(698,552+(right++%6)*17):Math.max(21,108-(left++%7)*12);
        const sx=forward?A.x+A.w:A.x,tx=forward?B.x+B.w:B.x;
        const labelY=(yA+yB)/2+((left+right)%3-1)*20;
        wire(a,b,label,`M${sx},${yA+12} H${track} V${yB+13} H${tx+(forward?2:-2)}`,forward?622:70,labelY,forward?kind:'feedback',forward?157:112);
      }
    }
    for(const s of seq){
      const p=pos.get(s.id);
      node({...p,id:s.id,code:levelNames[s.id],title:stripLevel(s.title),sub:s.ops.slice(0,3).map(o=>o.title).join(' · '),tone:'layer',onClick:()=>onLayer?.(s.id)});
    }
    const sbox=pos.get('state');
    const g=svgEl(blocks,'g',{class:'ax-node ax-node-state','data-ax-id':'state'});
    bind(g,mem.title,()=>onLayer?.('state'));
    svgEl(g,'rect',{...{x:sbox.x,y:sbox.y,width:sbox.w,height:sbox.h},rx:10,class:'ax-box'});
    markBinding(g,'state',sideX+sideW-13,startY+18);
    svgEl(g,'text',{x:sideX+16,y:startY+25,class:'ax-node-code'},'M · CROSS-LAYER');
    lines(stripLevel(mem.title),26).forEach((s,i)=>svgEl(g,'text',{x:sideX+16,y:startY+51+i*18,class:'ax-node-title'},s));
    let sy=startY+95;
    for(const text of lines(mem.summary,32,4)){svgEl(g,'text',{x:sideX+16,y:sy,class:'ax-node-sub'},text);sy+=17}
    sy+=20;
    for(const o of mem.ops.slice(0,Math.floor((floor-sy-18)/43))){
      const sg=svgEl(blocks,'g',{class:'ax-state-item','data-ax-id':o.id});
      bind(sg,o.title,()=>onOp?.('state',o.id));
      svgEl(sg,'rect',{x:sideX+12,y:sy-17,width:sideW-24,height:36,rx:5});
      lines(o.title,30,2).forEach((t,i)=>svgEl(sg,'text',{x:sideX+22,y:sy+i*14,class:'ax-state-title'},t));
      sy+=43;
    }
    node({...pos.get('host'),id:'host',code:'L6',title:stripLevel(host.title),sub:host.ops.slice(0,3).map(o=>o.title).join(' · '),tone:'platform',onClick:()=>onLayer?.('host')});
    finish(hostY+94);
  }
  function operationMap(records,edges,scope) {
    const byId=new Map(records.map(r=>[r.id,r])), rank=new Map(records.map(r=>[r.id,0]));
    const next=new Map(records.map(r=>[r.id,[]])),backEdges=new Set(), visiting=new Set(),done=new Set(),order=[];
    const valid=edges.filter(([a,b])=>byId.has(a)&&byId.has(b));
    valid.forEach(([a,b])=>next.get(a).push(b));
    function visit(id) {
      if(done.has(id))return;
      visiting.add(id);
      for(const dest of next.get(id)){if(visiting.has(dest))backEdges.add(id+'|'+dest);else visit(dest)}
      visiting.delete(id);done.add(id);order.push(id);
    }
    records.forEach(r=>visit(r.id));
    for(const id of order.reverse())for(const dest of next.get(id))if(!backEdges.has(id+'|'+dest))rank.set(dest,Math.max(rank.get(dest),rank.get(id)+1));
    const rows=[];
    for(const n of [...new Set(rank.values())].sort((a,b)=>a-b)){
      const items=records.filter(r=>rank.get(r.id)===n);
      for(let i=0;i<items.length;i+=3)rows.push(items.slice(i,i+3));
    }
    const grid=new Map(),rowOf=new Map();
    rows.forEach((items,i)=>items.forEach(r=>rowOf.set(r.id,i)));
    const gapEdges=rows.map(()=>[]);
    valid.forEach(e=>{if(rowOf.get(e[1])===rowOf.get(e[0])+1)gapEdges[rowOf.get(e[0])].push(e)});
    let y=57;
    rows.forEach((items,i)=>{
      const w=items.length===3?220:items.length===2?268:348, gap=items.length===3?22:48;
      items.forEach((r,j)=>{grid.set(r.id,{x:(width-items.length*w-(items.length-1)*gap)/2+j*(w+gap),y,w,h:70,row:i})});
      y+=70+Math.max(57,Math.min(8,gapEdges[i].length)*27+22);
    });
    const chartTitle=scope==='layer'?'FACTORY WORKFLOW':scope==='groups'?stripLevel(selectedLayer.title)+' · subsystems':(activeGroup||stripLevel(selectedLayer.title))+' · operations';
    region(10,7,width-20,y-13,chartTitle.toUpperCase());
    let left=0,right=0;
    for(const e of valid){
      const [a,b,label,k]=e,A=grid.get(a),B=grid.get(b),x1=A.x+A.w/2,x2=B.x+B.w/2;
      if(B.row===A.row+1){
        const batch=gapEdges[A.row],slot=batch.indexOf(e),gy=A.y+A.h+(B.y-A.y-A.h)*(slot+1)/(batch.length+1);
        wire(a,b,label,`M${x1},${A.y+A.h} V${gy} H${x2} V${B.y-2}`,(x1+x2)/2,gy,kindFor(a,b,k),210);
      }else{
        const goLeft=B.row<=A.row || (left+right)%2===0, ix=goLeft?left++:right++,track=goLeft?34+(ix%5)*14:width-34-(ix%5)*14;
        const sx=goLeft?A.x:A.x+A.w,tx=goLeft?B.x:B.x+B.w,sy=A.y+24,ty=B.y+46;
        wire(a,b,label,`M${sx},${sy} H${track} V${ty} H${tx+(goLeft?-2:2)}`,goLeft?77:width-77,(sy+ty)/2+((ix%3)-1)*18,B.row<=A.row?'feedback':kindFor(a,b,k),116);
      }
    }
    for(const r of records){
      const isLayer=scope==='layer',isGroup=scope==='groups'||r.boundary;
      const cap=isLayer||isGroup ? r.ops.length+' OPERATION'+(r.ops.length===1?'':'S') : r.cc.length+' CC'+(r.cc.length===1?'':'s');
      node({...grid.get(r.id),id:r.id,title:isLayer?stripLevel(r.title):r.title,code:r.boundary?'CONNECTED SUBSYSTEM':cap,tone:r.boundary?'neighbor':isLayer||isGroup?'layer':'operation',onClick:()=>isLayer?onLayer?.(r.id):isGroup?openGroup(r.title):onOp?.(selectedLayer.id,r.id)});
    }
    finish(y+4);
  }
  function layerComposition() {
    const l=selectedLayer;
    if(groupNames.length<2){operationMap(l.ops,l.edges,'op');return}
    const groups=new Map(groupNames.map(g=>[g,{id:groupKey(g),title:g,ops:l.ops.filter(o=>o.group===g)}]));
    const opGroups=new Map(l.ops.map(o=>[o.id,o.group]));
    for(const [g,r] of groups){
      bindingCounts.set(l.id+'/'+r.id,r.ops.reduce((n,o)=>n+(bindingCounts.get(l.id+'/'+o.id)||0),0));
      if(r.ops.some(o=>traced.has(o.id)))traced.add(r.id);
    }
    if(!activeGroup){
      const links=new Map();
      for(const [a,b,label,kind] of l.edges){
        const from=opGroups.get(a),to=opGroups.get(b);
        if(from===to||!from||!to)continue;
        const key=from+'|'+to;
        if(!links.has(key))links.set(key,[groupKey(from),groupKey(to),label,kind]);
      }
      operationMap([...groups.values()],[...links.values()],'groups');return;
    }
    const records=[...groups.get(activeGroup).ops],seen=new Set(records.map(r=>r.id)),edges=[];
    for(const [a,b,label,kind] of l.edges){
      const from=opGroups.get(a),to=opGroups.get(b);
      if(from!==activeGroup&&to!==activeGroup)continue;
      for(const other of [from,to]){
        if(other===activeGroup || !other || seen.has(groupKey(other)))continue;
        records.push({...groups.get(other),boundary:true});seen.add(groupKey(other));
      }
      edges.push([from===activeGroup?a:groupKey(from),to===activeGroup?b:groupKey(to),label,kind]);
    }
    operationMap(records,edges,'op');
  }
  function focusedOp(){
    const o=selectedOp,parent=selectedLayer, ops=new Map(parent.ops.map(r=>[r.id,r]));
    const inc=parent.edges.filter(([a,b])=>b===o.id&&a!==o.id&&ops.has(a));
    const out=parent.edges.filter(([a,b])=>a===o.id&&b!==o.id&&ops.has(b));
    const sideRows=Math.max(inc.length,out.length,1),sideBottom=72+sideRows*89,cy=72+(sideRows-1)*44.5;
    const center={x:355,y:cy,w:290,h:74};
    const ccs=[...new Set(o.cc.map(getCC).filter(Boolean))],ccY=sideBottom+65;
    const localHeight=ccY+Math.ceil(ccs.length/3)*87+24;
    const here=parent.id+'/'+o.id,ports={incoming:new Map(),outgoing:new Map()};
    for(const [from,to,label,kind] of options.cross||[]){
      if(from!==here&&to!==here)continue;
      const incoming=to===here,endpoint=incoming?from:to;
      const [lid,oid]=endpoint.split('/'),layer=coreLayer(lid),remote=layer?.ops.find(x=>x.id===oid);
      if(!remote||lid===parent.id)continue;
      const map=incoming?ports.incoming:ports.outgoing;
      if(!map.has(endpoint))map.set(endpoint,{from,to,kind,layer,remote,labels:[]});
      const entries=map.get(endpoint).labels;if(!entries.includes(label))entries.push(label);
    }
    const nPorts=Math.max(ports.incoming.size,ports.outgoing.size),crossHeight=nPorts?97+nPorts*86:0;
    region(8,7,width-16,localHeight-14,stripLevel(parent.title).toUpperCase()+' · OPERATION');
    const neighbors=[];
    function sides(edges, leftSide){
      edges.forEach(([a,b,label],i)=>{
        const id=leftSide?a:b, r=ops.get(id),dy=72+(sideRows-edges.length)*44.5+i*89, w=207, x=leftSide?24:width-w-24;
        const sy=dy+34, ey=cy+35+(i-(edges.length-1)/2)*6;
        const mid=leftSide?289:711;
        wire(a,b,label,leftSide?`M${x+w},${sy} H${mid} V${ey} H${center.x-2}`:`M${center.x+center.w},${ey} H${mid} V${sy} H${x-2}`,mid,sy,leftSide?'state':'call',112);
        neighbors.push({id,title:r.title,x,y:dy,w,h:67,code:leftSide?'INPUT FROM':'PASSES TO',tone:'neighbor',onClick:()=>onOp?.(parent.id,id)});
      });
    }
    sides(inc,true);sides(out,false);
    const ccNodes=[];
    ccs.forEach((id,i)=>{
      const row=Math.floor(i/3),col=i%3,count=Math.min(3,ccs.length-row*3),w=288,gap=17;
      const x=(width-count*w-(count-1)*gap)/2+col*(w+gap),y=ccY+row*87,tx=x+w/2;
      const gy=ccY-24;
      const path=row===0?`M500,${cy+74} V${gy} H${tx} V${y-2}`:`M500,${cy+74} V${gy} H16 V${y-10} H${tx} V${y-2}`;
      wire(o.id,id,'built by',path,500,gy,'build',112,i===0);
      const chunks=id.split('.');
      ccNodes.push({id,title:id,x,y,w,h:64,code:'CC · '+(chunks[0]||'').toUpperCase(),tone:'cc',selected:id===selectedRole,cc:true,onClick:()=>onRole?.(id)});
    });
    neighbors.forEach(node);
    node({...center,id:o.id,title:o.title,code:'SELECTED OPERATION',tone:'focus',selected:true,onClick:()=>onOp?.(parent.id,o.id)});
    ccNodes.forEach(node);
    if(!ccs.length)svgEl(labels,'text',{x:500,y:ccY,'text-anchor':'middle',class:'ax-node-sub'},'External dependency');
    for(const [a,b,l] of parent.edges.filter(([a,b])=>a===o.id&&b===o.id)){
      wire(a,b,l,`M505,${cy} v-21 h-63 v19`,478,cy-19,'feedback',155);
    }
    if(nPorts){
      const top=localHeight+9,my=top+53+(nPorts-1)*43;
      region(8,top,width-16,crossHeight-13,'ACROSS LAYERS');
      const connected=[];
      for(const [direction,entries] of Object.entries(ports)){
        const incoming=direction==='incoming';
        [...entries.values()].forEach(({from,to,kind,layer,remote,labels},i)=>{
          const x=incoming?24:769,y=top+52+(nPorts-entries.size)*43+i*86,ry=y+35,sy=my+35+(i-(entries.size-1)/2)*6;
          const mid=incoming?290:710;
          const d=incoming?`M231,${ry} H${mid} V${sy} H353`:`M645,${sy} H${mid} V${ry} H767`;
          wire(from,to,labels.join(' · '),d,mid,ry,kindFor(parent.id,layer.id,kind),112);
          connected.push({id:layer.id+'/'+remote.id,title:remote.title,code:(levelNames[layer.id]||'')+' '+stripLevel(layer.title).toUpperCase(),tone:'neighbor',x,y,w:207,h:70,onClick:()=>onOp?.(layer.id,remote.id)});
        });
      }
      node({id:here,title:o.title,code:'THIS OPERATION',tone:'focus',selected:true,x:355,y:my,w:290,h:70,onClick:()=>onOp?.(parent.id,o.id)});
      connected.forEach(node);
    }
    finish(localHeight+crossHeight+7);
  }
  if(selectedOp) focusedOp();
  else if(selectedLayer) layerComposition();
  else if(palette==='engine') engineOverview();
  else operationMap(layers,rawEdges,'layer');
  const legend=html('div','ax-legend');
  if (showBindings) legend.append(html('span','ax-overlay-key',overlayName+' · filled dot = linked source evidence'));
  const kinds=new Set(drawn.map(e=>[...e.g.classList].find(v=>v.startsWith('ax-wire-'))?.slice(8)));
  const typeLabels={call:palette==='factory'?'Handoff':'Call / data',state:'State / input',feedback:'Return / repeat',build:'Built by',platform:'Device / host',trace:'Selected path'};
  for(const k of Object.keys(typeLabels))if(kinds.has(k)){
    const item=html('span','ax-key ax-key-'+k);item.append(html('i',''),document.createTextNode(typeLabels[k]));legend.append(item);
  }
  shell.append(legend);
  const index=html('details','ax-index');const summary=html('summary','', 'Connections ('+drawn.length+')');index.append(summary);
  const titles=new Map(layers.flatMap(l=>[[l.id,stripLevel(l.title)],...l.ops.map(o=>[o.id,o.title])]));
  for(const l of layers)for(const o of l.ops)titles.set(l.id+'/'+o.id,stripLevel(l.title)+' / '+o.title);
  for(const g of groupNames)titles.set(groupKey(g),g);
  for(const {a,b,label} of drawn){
    const row=html('div','ax-index-row');
    const src=html('strong','',titles.get(a)||a), action=html('span','',label), dst=html('strong','',titles.get(b)||b);
    row.append(src,action,dst);index.append(row);
  }
  if(drawn.length)shell.append(index);
  return shell;
}
