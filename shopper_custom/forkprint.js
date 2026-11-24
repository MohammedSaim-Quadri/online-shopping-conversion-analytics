/* Conversion Forkprint: custom, proposed composite fork-glyph idiom.
 * Fixed geometry ensures filtering does not change the meaning of branch length.
 * Each traffic-source row has fixed visitor positions. D3 draws every mark.
 */
(function () {
  'use strict';
  function ConversionForkprint(props) {
    const React = window.React;
    const node = React.useRef(null);
    const { data = [], selected = null, setProps } = props;
    React.useEffect(function () {
      if (!node.current) return;
      const container = window.d3 && window.d3.select(node.current);
      if (!container) {
        node.current.textContent = 'D3 failed to load. Check the network connection and browser console.';
        return;
      }
      const d3 = window.d3;
      container.selectAll('*').remove();
      const entries = (data || []).filter(d => Number.isFinite(+d.rate) && +d.sessions > 0);
      if (!entries.length) {
        container.append('div').attr('class', 'fork-empty').text('No sessions match these filters. Clear a filter or a fork selection.');
        return;
      }
      const traffic = [...new Set(entries.map(d => +d.traffic))].sort((a, b) => a - b);
      const visitors = ['Returning_Visitor', 'New_Visitor', 'Other'];
      const visitorsPresent = new Set(entries.map(d => d.visitor));
      const label = { 'Returning_Visitor': 'Returning', 'New_Visitor': 'New', 'Other': 'Other' };
      const left = 100, colWidth = 333, rowHeight = 68, top = 72, bottom = 35;
      const width = left + 3 * colWidth + 12;
      const height = top + traffic.length * rowHeight + bottom;
      const svg = container.append('svg')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('width', width).attr('height', height)
        .attr('role', 'img')
        .attr('aria-label', 'Custom Conversion Forkprint. Each row is a traffic source. Fixed visitor columns show purchase and non-purchase fork arms, conversion percentage, and counts.');
      svg.append('text').attr('x', 10).attr('y', 32).attr('class', 'fork-axis').text('Traffic source');
      visitors.forEach((v, c) => {
        svg.append('text').attr('x', left + c * colWidth + 135).attr('y', 32)
          .attr('text-anchor', 'middle').attr('class', 'fork-axis')
          .attr('opacity', visitorsPresent.has(v) ? 1 : 0.4).text(label[v]);
      });
      const maxSessions = Math.max(
        1,
        Number(entries[0].scaleMax) || Math.max(...entries.map(d => +d.sessions), 1)
      );
      const thickness = d3.scaleSqrt().domain([0, maxSessions]).range([1.3, 7]);
      const lookup = new Map(entries.map(d => [`${d.traffic}|${d.visitor}`, d]));
      const tooltip = container.append('div').attr('class', 'fork-tooltip').style('display', 'none');
      const pct = d3.format('.1%');
      traffic.forEach((ch, r) => {
        const y = top + r * rowHeight + 21;
        svg.append('text').attr('x', 10).attr('y', y + 3).attr('class', 'fork-label').text(`Source ${ch}`);
        svg.append('line').attr('x1', left - 5).attr('x2', width - 8).attr('y1', y + 32)
          .attr('y2', y + 32).attr('stroke', '#e7edf6');
        visitors.forEach((v, c) => {
          const d = lookup.get(`${ch}|${v}`);
          if (!d) return;
          const rate = Math.max(0, Math.min(1, +d.rate));
          const n = +d.sessions, purchases = +d.purchases, nonpurchases = n - purchases;
          const isSelected = !!selected && String(selected.traffic) === String(ch) && selected.visitor === v;
          const x = left + c * colWidth + 8, junction = 108, end = 215, midY = 4;
          const g = svg.append('g').attr('transform', `translate(${x},${y})`)
            .attr('class', 'fork-glyph' + (isSelected ? ' selected' : ''))
            .attr('tabindex', 0).attr('role', 'button')
            .attr('aria-pressed', isSelected ? 'true' : 'false')
            .attr('aria-label', `Traffic source ${ch}, ${label[v]}: ${purchases} purchases among ${n} sessions, ${pct(rate)}. Activate to filter the other charts.`);
          const stroke = thickness(n);
          g.append('path').attr('d', `M 0 ${midY} L ${junction} ${midY}`)
            .attr('stroke', '#8497b1').attr('stroke-width', stroke).attr('stroke-linecap', 'round').attr('fill', 'none');
          // Deflection is proportional to the observed fraction; zero-count arms are omitted.
          // The common baseline is intentionally shared, so a zero is not drawn as a positive fork.
          if (purchases > 0) {
            const purchaseLift = 25 * rate;
            g.append('path').attr('d', `M ${junction} ${midY} Q ${(junction + end) / 2} ${midY} ${end} ${midY - purchaseLift}`)
              .attr('stroke', '#0d9488').attr('stroke-width', Math.max(1.6, stroke * .62))
              .attr('stroke-linecap', 'round').attr('fill', 'none');
            g.append('circle').attr('cx', end).attr('cy', midY - purchaseLift).attr('r', 2.6).attr('fill', '#0d9488');
          }
          if (nonpurchases > 0) {
            const nonpurchaseDrop = 25 * (1 - rate);
            g.append('path').attr('d', `M ${junction} ${midY} Q ${(junction + end) / 2} ${midY} ${end} ${midY + nonpurchaseDrop}`)
              .attr('stroke', '#d68d54').attr('stroke-width', Math.max(1.6, stroke * .62))
              .attr('stroke-linecap', 'round').attr('fill', 'none');
            g.append('circle').attr('cx', end).attr('cy', midY + nonpurchaseDrop).attr('r', 2.6).attr('fill', '#d68d54');
          }
          g.append('text').attr('x', 228).attr('y', 0).attr('class', 'fork-rate').text(pct(rate));
          g.append('text').attr('x', 228).attr('y', 15).attr('class', 'fork-count')
            .text(`${purchases}/${n}${n < 30 ? ' · low n' : ''}`);
          if (n < 30) g.classed('fork-sparse', true);
          g.append('rect').attr('x', -5).attr('y', -26).attr('width', 315).attr('height', 59)
            .attr('fill', 'transparent').attr('class', 'fork-hit');
          const desc = `Traffic ${ch} / ${label[v]}: ${purchases} purchases, ${nonpurchases} non-purchases, ${n} sessions (${pct(rate)})` +
            (n < 30 ? ' — small group; interpret carefully.' : '');
          g.on('mouseenter', () => tooltip.style('display', 'block').text(desc))
            .on('mousemove', event => {
              const bounds = node.current.getBoundingClientRect();
              let lx = event.clientX - bounds.left + 16, ly = event.clientY - bounds.top + 15;
              lx = Math.max(4, Math.min(lx, bounds.width - 285));
              tooltip.style('left', `${lx}px`).style('top', `${ly}px`);
            }).on('mouseleave', () => tooltip.style('display', 'none'));
          function activate() { if (setProps) setProps({ selected: isSelected ? null : { traffic: String(ch), visitor: v } }); }
          g.on('click', activate).on('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); activate(); }
          });
        });
      });
    }, [data, selected, setProps]);
    return React.createElement('div', { id: props.id, className: 'fork-container ' + (props.className || ''), ref: node });
  }
  window.shopper_custom = window.shopper_custom || {};
  window.shopper_custom.ConversionForkprint = ConversionForkprint;
})();
