// Application state
const flags = { flip: false, gradient: false, mirror: false, animate: true };
let currentTab = 'markdown';
let lastUrl = '';

document.getElementById('toggle-animate').classList.add('on');

// Color input synchronization
function syncColor(pickerId, textId) {
  const p = document.getElementById(pickerId);
  const t = document.getElementById(textId);
  p.addEventListener('input', () => { t.value = p.value; debounce(); });
  t.addEventListener('input', () => {
    if (/^#[0-9a-fA-F]{6}$/.test(t.value)) { p.value = t.value; debounce(); }
  });
}
syncColor('color_top_picker', 'color_top');
syncColor('color_bottom_picker', 'color_bottom');
syncColor('text_color_picker', 'text_color');

// Toggle controls
function toggle(key, el) {
  flags[key] = !flags[key];
  el.classList.toggle('on', flags[key]);
  debounce();
}

// Debounced updates
let debTimer = null;
function debounce() {
  clearTimeout(debTimer);
  debTimer = setTimeout(generate, 300);
}

['type','position','width','height','amplitude','frequency','layers','opacity','speed','text_content','text_size','text_style','text_scale_x','text_scale_y','text_x','text_y','text_align'].forEach(id => {
  document.getElementById(id).addEventListener('change', debounce);
  document.getElementById(id).addEventListener('input', debounce);
});

// Wave generation
async function generate() {
  const isTopPosition = document.getElementById('position').value === 'top';
  flags.flip = isTopPosition;
  document.getElementById('toggle-flip').classList.toggle('on', flags.flip);

  const params = new URLSearchParams({
    type:         document.getElementById('type').value,
    width:        document.getElementById('width').value,
    height:       document.getElementById('height').value,
    amplitude:    document.getElementById('amplitude').value,
    frequency:    document.getElementById('frequency').value,
    layers:       document.getElementById('layers').value,
    color_top:    document.getElementById('color_top').value.replace('#',''),
    color_bottom: document.getElementById('color_bottom').value.replace('#',''),
    opacity:      document.getElementById('opacity').value,
    flip:         flags.flip,
    gradient:     flags.gradient,
    mirror:       flags.mirror,
    animate:      flags.animate,
    speed:        document.getElementById('speed').value,
    text:         document.getElementById('text_content').value,
    text_color:   document.getElementById('text_color').value.replace('#',''),
    text_size:    document.getElementById('text_size').value,
    text_style:   document.getElementById('text_style').value,
    text_scale_x: document.getElementById('text_scale_x').value,
    text_scale_y: document.getElementById('text_scale_y').value,
    text_x:       document.getElementById('text_x').value,
    text_y:       document.getElementById('text_y').value,
    text_align:   document.getElementById('text_align').value,
  });

  const url = `/wave?${params}`;
  lastUrl = url;

  document.getElementById('loading-bar').classList.add('active');

  // Fetch inline SVG for preview updates
  try {
    const resp = await fetch(url);
    const svg = await resp.text();
    document.getElementById('preview-wrap').innerHTML = svg;
  } catch(e) {}

  document.getElementById('loading-bar').classList.remove('active');
  document.getElementById('output').classList.add('show');
  updateCode();
}

// Export code output
function updateCode() {
  const abs = window.location.origin + lastUrl;
  let code = '';
  if (currentTab === 'markdown') {
    code = `![Wave divider](${abs})`;
  } else if (currentTab === 'html') {
    code = `<img src="${abs}" alt="Wave divider" style="width:100%;display:block;" />`;
  } else {
    code = abs;
  }
  document.getElementById('code-out').textContent = code;
}

function setTab(tab, btn) {
  currentTab = tab;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  updateCode();
}

function copyCode() {
  navigator.clipboard.writeText(document.getElementById('code-out').textContent).then(() => {
    const b = document.getElementById('copy-btn');
    b.textContent = '✓ Copied'; b.classList.add('ok');
    setTimeout(() => { b.textContent = 'Copy'; b.classList.remove('ok'); }, 2000);
  });
}

// Preset generation
const PRESET_PALETTES = [
  ['#0d1117', '#161b22'], ['#0a1628', '#0f3460'], ['#1a0a2e', '#f72585'],
  ['#0a1a0d', '#1a4a22'], ['#0f0f0f', '#222222'], ['#f0f0f0', '#ffffff'],
  ['#020010', '#0d0030'], ['#111827', '#1f2937'], ['#001219', '#005f73'],
  ['#3c096c', '#ff6d00'], ['#14213d', '#fca311'], ['#10002b', '#240046'],
];

function randomBetween(min, max, step = 1) {
  const count = Math.round((max - min) / step);
  return min + Math.floor(Math.random() * (count + 1)) * step;
}

function buildRandomPresets(count = 4) {
  const types = ['smooth', 'sine', 'bump', 'zigzag'];
  const palettes = [...PRESET_PALETTES].sort(() => Math.random() - 0.5);
  const presets = [];

  for (let i = 0; i < count; i++) {
    const [ct, cb] = palettes[i % palettes.length];
    presets.push({
      label: `Random ${i + 1}`,
      type: types[randomBetween(0, types.length - 1)],
      ct,
      cb,
      amp: randomBetween(10, 35),
      freq: randomBetween(0.5, 3, 0.5),
      layers: randomBetween(1, 3),
      flip: Math.random() > 0.5,
    });
  }

  return presets;
}

function buildPreviewSVG(p) {
  const w = 300, h = 40;
  const amp = p.amp * (h / 80);
  const freq = p.freq;
  const mid = h / 2;
  let path = `M 0 ${mid} `;
  const pts = 60;
  for (let i = 1; i <= pts; i++) {
    const x = (i / pts) * w;
    const prevX = ((i-1) / pts) * w;
    const y = mid + amp * Math.sin(2 * Math.PI * freq * (i / pts));
    const py = mid + amp * Math.sin(2 * Math.PI * freq * ((i-1) / pts));
    const cx = (prevX + x) / 2;
    path += `C ${cx} ${py} ${cx} ${y} ${x} ${y} `;
  }
  path += `L ${w} ${h} L 0 ${h} Z`;
  const transform = p.flip ? `transform="scale(1,-1) translate(0,-${h})"` : '';
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" style="width:100%;height:40px">
    <rect width="${w}" height="${h}" fill="${p.ct}"/>
    <path d="${path}" fill="${p.cb}" ${transform}/>
  </svg>`;
}

function applyPreset(p) {
  document.getElementById('type').value = p.type;
  document.getElementById('position').value = p.flip ? 'top' : 'bottom';
  document.getElementById('amplitude').value = p.amp;
  document.getElementById('frequency').value = p.freq;
  document.getElementById('layers').value = p.layers;
  document.getElementById('color_top').value = p.ct;
  document.getElementById('color_top_picker').value = p.ct;
  document.getElementById('color_bottom').value = p.cb;
  document.getElementById('color_bottom_picker').value = p.cb;

  // Reset toggle state
  ['flip','gradient','mirror','animate'].forEach(f => {
    flags[f] = false;
    document.getElementById(`toggle-${f}`).classList.remove('on');
    document.querySelector(`#toggle-${f} .dot`).style.background = '';
  });
  flags.animate = true;
  document.getElementById('toggle-animate').classList.add('on');

  if (p.flip) {
    flags.flip = true;
    document.getElementById('toggle-flip').classList.add('on');
  }

  generate();
}

const grid = document.getElementById('preset-grid');
const randomPresets = buildRandomPresets(4);
randomPresets.forEach(p => {
  const btn = document.createElement('button');
  btn.className = 'preset-btn';
  btn.innerHTML = `<div class="preset-thumb">${buildPreviewSVG(p)}</div><div class="preset-label">${p.label}</div>`;
  btn.onclick = () => applyPreset(p);
  grid.appendChild(btn);
});

// Initial render
generate();
