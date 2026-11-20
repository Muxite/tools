/* Uses the original atlas renderer's accessible SVG nodes, edges and navigation. */
function orderedPathGraph({node, wire, region, finish, groups, open, edges}) {
  const edgeStyle = {
    flow: ['call', ''], call: ['call', ''], build: ['build', ''],
    branch: ['build', 'Branch'], rejoin: ['call', 'Rejoin'],
    loop: ['feedback', 'Repeat'], feedback: ['feedback', 'Feedback'],
    support: ['state', 'Support'], state: ['state', 'State'], platform: ['platform', 'Host']
  };
  const positions = new Map();
  const outgoing = new Map(), incoming = new Map();
  const links = edges.map(([from, to, payload, kind = 'flow']) => {
    const [style, qualifier] = edgeStyle[kind] || edgeStyle.flow;
    const edge = {from, to, style, kind, label:qualifier ? qualifier + ' · ' + payload : payload};
    for (const [table, id] of [[outgoing, from], [incoming, to]]) {
      if (!table.has(id)) table.set(id, []);
      table.get(id).push(edge);
    }
    return edge;
  });

  // Leave one labelled departure slot for each outgoing connection. Labels
  // stay beside their source even when the receiving component is stages away.
  const nodeW = 333, nodeH = 55, shelf = 34;
  let top = 8;
  const stageBoxes = [];
  for (const group of groups) {
    const start = top;
    const captionLines = [];
    for (const word of (group.caption || '').split(/\s+/).filter(Boolean)) {
      if (!captionLines.length || captionLines.at(-1).length + word.length > 130) captionLines.push(word);
      else captionLines[captionLines.length - 1] += ' ' + word;
    }
    top += 42 + captionLines.length * 17;
    const host = group.kind === 'platform' || /host|hardware|target environment/i.test(group.title);
    const count = Math.max(group.main.length, group.side.length);
    for (let row = 0; row < count; row++) {
      let maxSlots = 0;
      for (const [lane, column] of [[group.main, 0], [group.side, 1]]) {
        const component = lane[row];
        if (!component) continue;
        if (positions.has(component.id)) throw Error('Repeated path node ' + component.id);
        const box = {x:column ? 629 : 38, y:top, w:nodeW, h:nodeH, component, column, host};
        positions.set(component.id, box);
        maxSlots = Math.max(maxSlots, (outgoing.get(component.id) || []).length);
      }
      top += nodeH + maxSlots * shelf + 17;
    }
    stageBoxes.push({group, start, height:top - start, host, captionLines});
    top += 14;
  }

  for (const {group,start,height,host} of stageBoxes) {
    region(10,start,980,height,group.title,host ? 'ax-region-platform' : '');
  }
  const tracks = [];
  for (const edge of links) {
    const source = positions.get(edge.from), target = positions.get(edge.to);
    if (!source || !target) throw Error('Unresolved path edge ' + edge.from + ' → ' + edge.to);
    const departures = outgoing.get(edge.from), arrivals = incoming.get(edge.to);
    const slot = departures.indexOf(edge);
    const arrival = arrivals.indexOf(edge);
    const labelY = source.y + nodeH + 18 + slot * shelf;
    const sourceX = source.column ? source.x + source.w - 15 - slot * 4 : source.x + 15 + slot * 4;
    const targetX = target.column ? target.x - 2 : target.x + target.w + 2;
    const targetY = target.y + 9 + (arrival + 1) * (nodeH - 18) / (arrivals.length + 1);
    const lo = Math.min(labelY,targetY), hi = Math.max(labelY,targetY);
    let track = tracks.findIndex(spans => spans.every(([a,b]) => hi + 7 < a || lo > b + 7));
    if (track < 0) { track = tracks.length; tracks.push([]); }
    tracks[track].push([lo,hi]);
    edge.geometry = {source, target, labelY, sourceX, targetX, targetY, track};
  }
  for (const edge of links) {
    const {source,labelY,sourceX,targetX,targetY,track} = edge.geometry;
    const rail = 395 + (track + 1) * 210 / (tracks.length + 1);
    const path = 'M' + sourceX + ',' + (source.y + nodeH) + ' V' + labelY +
      ' H' + rail + ' V' + targetY + ' H' + targetX;
    wire(edge.from,edge.to,edge.label,path,source.x+nodeW/2,labelY,edge.style,nodeW-42);
  }
  let svg;
  for (const {component,column,host,x,y,w,h} of positions.values()) {
    const g = node({id:component.id, title:component.name, x,y,w,h,
      code:component.scope==='Extension'?'CONDITIONAL EXTENSION':host?'HOST PROVIDER':undefined,
      tone:host ? 'platform' : column ? 'state' : 'layer',
      onClick:() => open(component.id)});
    svg ||= g?.ownerSVGElement;
  }
  if (svg) {
    const headings = svg.querySelectorAll('.ax-region-title');
    stageBoxes.forEach(({captionLines,start}, index) => {
      const heading = headings[index];
      captionLines.forEach((line, i) => {
        const caption = document.createElementNS(svg.namespaceURI,'text');
        caption.setAttribute('x','27');
        caption.setAttribute('y',String(start + 42 + i * 17));
        caption.setAttribute('class','ax-node-sub');
        caption.textContent = line;
        heading.parentNode.append(caption);
      });
    });
  }
  finish(top - 5);
}
