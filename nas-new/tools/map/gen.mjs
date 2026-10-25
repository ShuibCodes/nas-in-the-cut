// Draws the dotted world map (src/img/world-dots.svg) and the marker positions (tools/markers.json).
// Run:  cd tools/map && npm install && node gen.mjs
// To add a place, add [longitude, latitude] to "places" below, rerun, then add it to MARKERS in build.py.
import fs from 'fs';
import {geoEqualEarth, geoContains} from 'd3-geo';
import {feature} from 'topojson-client';
const topo = JSON.parse(fs.readFileSync('node_modules/world-atlas/land-50m.json'));
const land = feature(topo, topo.objects.land);
const W = 1000, H = 470;
const proj = geoEqualEarth().rotate([-12, 0]);
// Fit the world without Antarctica.
const pts = []; for (let lon = -167.9; lon <= 191.9; lon += 2) for (const lat of [-57, -30, 0, 30, 60, 83]) pts.push([lon, lat]);
proj.fitExtent([[6, 6], [W - 6, H - 6]], {type: 'MultiPoint', coordinates: pts});
const step = 8.2; let d = ''; let n = 0;
for (let y = step / 2; y < H; y += step) {
  for (let x = step / 2; x < W; x += step) {
    const ll = proj.invert([x, y]);
    if (!ll || ll[1] < -57) continue;
    if (geoContains(land, ll)) { d += `M${x.toFixed(1)} ${y.toFixed(1)}h0`; n++; }
  }
}
const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}"><path d="${d}" fill="none" stroke="#a9b4c5" stroke-width="3.6" stroke-linecap="round" opacity=".42"/></svg>`;
fs.writeFileSync('../../src/img/world-dots.svg', svg);
const places = {dubai: [55.27, 25.2], 'cote-divoire': [-4.02, 5.35], gabon: [9.45, 0.39], benin: [2.42, 6.37], rwanda: [30.06, -1.95], uganda: [32.58, 0.35], kenya: [36.82, -1.29]};
const out = {};
for (const [k, ll] of Object.entries(places)) { const [x, y] = proj(ll); out[k] = [+(x / W * 100).toFixed(2), +(y / H * 100).toFixed(2)]; }
fs.writeFileSync('../markers.json', JSON.stringify(out));
console.log(n, 'dots', (svg.length / 1024).toFixed(1) + 'KB', JSON.stringify(out));
