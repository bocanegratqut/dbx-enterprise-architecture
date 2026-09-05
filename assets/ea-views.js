/* Generated architecture views: render Mermaid, let the reader move shapes, report positions.
 *
 * Nothing here is saved: positions live in a browser-side store for the page's lifetime and
 * are handed to the draw.io export. Mermaid's layout engine is not re-run after a move; the
 * relationships of a moved shape are redrawn as straight connectors and its layer box grows
 * to keep it inside.
 */
(function () {
  const ID_RE = /\[([^\[\]]+)\]\s*$/;

  function ensureMermaid() {
    if (!window.mermaid) { return false; }
    if (!window.__eaMermaidInit) {
      window.mermaid.initialize({
        startOnLoad: false, securityLevel: 'strict', theme: 'neutral',
        flowchart: { htmlLabels: true, useMaxWidth: false, curve: 'basis', nodeSpacing: 30, rankSpacing: 50 },
      });
      window.__eaMermaidInit = true;
    }
    return true;
  }

  function nodeInfo(svg) {
    // mermaid node id -> {el, elementId, cx, cy, w, h}
    const nodes = {};
    svg.querySelectorAll('g.node').forEach(function (g) {
      const m = /^flowchart-(.+)-\d+$/.exec(g.id || '');
      if (!m) { return; }
      const label = (g.textContent || '').trim();
      const idm = ID_RE.exec(label);
      const t = /translate\(([-\d.]+),\s*([-\d.]+)\)/.exec(g.getAttribute('transform') || '');
      let bb;
      try { bb = g.getBBox(); } catch (e) { bb = { x: -60, y: -20, width: 120, height: 40 }; }
      nodes[m[1]] = {
        el: g, elementId: idm ? idm[1] : null,
        cx: t ? parseFloat(t[1]) : 0, cy: t ? parseFloat(t[2]) : 0, w: bb.width, h: bb.height,
      };
    });
    return nodes;
  }

  function edgeInfo(svg, nodes) {
    const ids = Object.keys(nodes).sort(function (a, b) { return b.length - a.length; });
    const edges = [];
    svg.querySelectorAll('path.flowchart-link').forEach(function (p) {
      const id = p.id || '';
      if (!id.startsWith('L_')) { return; }
      let src = null, dst = null;
      for (const a of ids) {
        if (!id.startsWith('L_' + a + '_')) { continue; }
        const rest = id.slice(('L_' + a + '_').length).replace(/_\d+$/, '');
        if (nodes[rest]) { src = a; dst = rest; break; }
      }
      if (!src) { return; }
      const label = svg.querySelector('g.edgeLabel g.label[data-id="' + id + '"]');
      edges.push({ path: p, src: src, dst: dst, labelGroup: label ? label.parentElement : null });
    });
    return edges;
  }

  function clusterInfo(svg, nodes) {
    const clusters = [];
    svg.querySelectorAll('g.cluster').forEach(function (c) {
      const rect = c.querySelector('rect');
      if (!rect) { return; }
      const x = parseFloat(rect.getAttribute('x')), y = parseFloat(rect.getAttribute('y'));
      const w = parseFloat(rect.getAttribute('width')), h = parseFloat(rect.getAttribute('height'));
      const members = Object.keys(nodes).filter(function (k) {
        const n = nodes[k]; return n.cx >= x && n.cx <= x + w && n.cy >= y && n.cy <= y + h;
      });
      const label = c.querySelector('.cluster-label');
      clusters.push({ rect: rect, label: label, members: members, pad: 12 });
    });
    return clusters;
  }

  function borderPoint(n, tx, ty) {
    // where the segment from the node centre towards (tx, ty) leaves the node's rectangle
    const dx = tx - n.cx, dy = ty - n.cy;
    if (dx === 0 && dy === 0) { return { x: n.cx, y: n.cy }; }
    const hw = n.w / 2, hh = n.h / 2;
    const sx = dx !== 0 ? hw / Math.abs(dx) : Infinity, sy = dy !== 0 ? hh / Math.abs(dy) : Infinity;
    const s = Math.min(sx, sy);
    return { x: n.cx + dx * s, y: n.cy + dy * s };
  }

  function reroute(edges, nodes, nodeId) {
    edges.forEach(function (e) {
      if (e.src !== nodeId && e.dst !== nodeId) { return; }
      const a = nodes[e.src], b = nodes[e.dst];
      const p1 = borderPoint(a, b.cx, b.cy), p2 = borderPoint(b, a.cx, a.cy);
      e.path.setAttribute('d', 'M' + p1.x + ',' + p1.y + 'L' + p2.x + ',' + p2.y);
      if (e.labelGroup) {
        e.labelGroup.setAttribute('transform', 'translate(' + (p1.x + p2.x) / 2 + ', ' + (p1.y + p2.y) / 2 + ')');
      }
    });
  }

  function growClusters(clusters, nodes) {
    clusters.forEach(function (c) {
      if (!c.members.length) { return; }
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      c.members.forEach(function (k) {
        const n = nodes[k];
        x0 = Math.min(x0, n.cx - n.w / 2); y0 = Math.min(y0, n.cy - n.h / 2);
        x1 = Math.max(x1, n.cx + n.w / 2); y1 = Math.max(y1, n.cy + n.h / 2);
      });
      const rx = parseFloat(c.rect.getAttribute('x')), ry = parseFloat(c.rect.getAttribute('y'));
      const rw = parseFloat(c.rect.getAttribute('width')), rh = parseFloat(c.rect.getAttribute('height'));
      const nx = Math.min(rx, x0 - c.pad), ny = Math.min(ry, y0 - c.pad - 24);
      const nx1 = Math.max(rx + rw, x1 + c.pad), ny1 = Math.max(ry + rh, y1 + c.pad);
      c.rect.setAttribute('x', nx); c.rect.setAttribute('y', ny);
      c.rect.setAttribute('width', nx1 - nx); c.rect.setAttribute('height', ny1 - ny);
      if (c.label) {
        const t = /translate\(([-\d.]+),\s*([-\d.]+)\)/.exec(c.label.getAttribute('transform') || '');
        if (t) { c.label.setAttribute('transform', 'translate(' + ((nx + nx1) / 2) + ', ' + ny + ')'); }
      }
    });
  }

  function positionsOf(nodes) {
    const out = {};
    Object.keys(nodes).forEach(function (k) {
      const n = nodes[k];
      if (n.elementId) { out[n.elementId] = { x: n.cx, y: n.cy, w: n.w, h: n.h }; }
    });
    return out;
  }

  function enableDrag(svg, onChange) {
    const nodes = nodeInfo(svg);
    const edges = edgeInfo(svg, nodes);
    const clusters = clusterInfo(svg, nodes);
    let dragging = null, start = null, origin = null;
    function toSvg(evt) {
      const pt = svg.createSVGPoint(); pt.x = evt.clientX; pt.y = evt.clientY;
      return pt.matrixTransform(svg.getScreenCTM().inverse());
    }
    Object.keys(nodes).forEach(function (k) {
      const n = nodes[k];
      n.el.style.cursor = 'grab';
      n.el.addEventListener('pointerdown', function (evt) {
        dragging = k; start = toSvg(evt); origin = { cx: n.cx, cy: n.cy };
        n.el.style.cursor = 'grabbing'; evt.preventDefault(); evt.stopPropagation();
        try { n.el.setPointerCapture(evt.pointerId); } catch (e) { /* older browsers */ }
      });
      n.el.addEventListener('pointermove', function (evt) {
        if (dragging !== k) { return; }
        const p = toSvg(evt);
        n.cx = origin.cx + (p.x - start.x); n.cy = origin.cy + (p.y - start.y);
        n.el.setAttribute('transform', 'translate(' + n.cx + ', ' + n.cy + ')');
        reroute(edges, nodes, k);
        growClusters(clusters, nodes);
      });
      const end = function (evt) {
        if (dragging !== k) { return; }
        dragging = null; n.el.style.cursor = 'grab';
        // let the canvas grow with the shapes so nothing is clipped
        try {
          const bb = svg.getBBox();
          svg.setAttribute('viewBox', (bb.x - 10) + ' ' + (bb.y - 10) + ' ' + (bb.width + 20) + ' ' + (bb.height + 20));
          svg.setAttribute('width', bb.width + 20); svg.setAttribute('height', bb.height + 20);
        } catch (e) { /* ignore */ }
        if (onChange) { onChange(positionsOf(nodes)); }
      };
      n.el.addEventListener('pointerup', end);
      n.el.addEventListener('pointercancel', end);
    });
    return positionsOf(nodes);
  }

  // Render `code` into the target container, make it draggable, return a promise of the positions.
  window.eaViews = {
    render: function (targetId, code, onChange) {
      const el = document.getElementById(targetId);
      if (!el) { return Promise.resolve(null); }
      if (!code || !code.trim()) { el.innerHTML = ''; return Promise.resolve({}); }
      if (!ensureMermaid()) { el.innerHTML = '<div style="color:#c92a2a;font-size:12px">Mermaid is not loaded.</div>'; return Promise.resolve(null); }
      const uid = 'ea-svg-' + Math.random().toString(36).slice(2, 10);
      return window.mermaid.render(uid, code).then(function (r) {
        el.innerHTML = r.svg;
        const svg = el.querySelector('svg');
        if (!svg) { return {}; }
        svg.style.maxWidth = 'none';
        return enableDrag(svg, onChange);
      }).catch(function (err) {
        el.innerHTML = '<pre style="color:#c92a2a;font-size:12px;white-space:pre-wrap">' + String(err) + '</pre>';
        return null;
      });
    },
  };
})();
