const fs = require('fs');
const path = require('path');

const defaults = {
  'site/index.html': 'magnet-3-deposits-rates',
  'site/earning/index.html': 'magnet-11-neuro-marketer',
  'site/of/index.html': 'magnet-7-bad-credit-approval',
  'site/strah/index.html': 'magnet-8-before-policy',
  'site/fin/index.html': 'magnet-3-deposits-rates',
};

const matches = [];
function walk(dir) {
  fs.readdirSync(dir).forEach((f) => {
    const p = path.join(dir, f);
    const stat = fs.statSync(p);
    if (stat.isDirectory()) walk(p);
    else if (p.endsWith('.html')) matches.push(p);
  });
}
walk('site');

let changed = 0;
matches.forEach((p) => {
  const rel = p.replace(/\\/g, '/').replace(/^site\//, 'site/');
  let content = fs.readFileSync(p, 'utf8');
  if (!/name="magnet"\s+value="">/.test(content)) return;
  const def = defaults[rel];
  if (!def) return;
  content = content.replace(
    /name="magnet"\s+value="">/g,
    `name="magnet" value="${def}">`
  );
  fs.writeFileSync(p, content, 'utf8');
  changed++;
  console.log('PATCHED', rel, '->', def);
});
console.log('changed', changed);
