from flask import Flask

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Cosmic Curriculum - Interactive Subject Galaxy</title>
<style>
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    overflow: hidden;
    background: #0a0a1a;
    color: #fff;
    user-select: none;
  }
  #canvas-container {
    position: fixed; inset: 0;
    z-index: 0;
  }
  #header {
    position: fixed; top: 24px; left: 50%; transform: translateX(-50%);
    z-index: 10;
    text-align: center;
    pointer-events: none;
  }
  #header h1 {
    font-size: 1.8rem; font-weight: 300; letter-spacing: 6px;
    text-transform: uppercase;
    text-shadow: 0 0 30px rgba(100,180,255,0.3);
  }
  #header p {
    font-size: 0.85rem; opacity: 0.5; letter-spacing: 2px;
    margin-top: 4px;
  }
  #tooltip {
    position: fixed;
    z-index: 20;
    padding: 6px 16px;
    border-radius: 20px;
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.15);
    font-size: 0.85rem;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s;
    white-space: nowrap;
  }
  #tooltip.visible { opacity: 1; }
  #info-panel {
    position: fixed;
    top: 0; right: 0;
    width: 420px; max-width: 92vw;
    height: 100vh;
    z-index: 30;
    background: rgba(15, 15, 35, 0.65);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-left: 1px solid rgba(255,255,255,0.10);
    box-shadow: -8px 0 40px rgba(0,0,0,0.5);
    transform: translateX(100%);
    transition: transform 0.45s cubic-bezier(0.22, 1, 0.36, 1);
    overflow-y: auto;
    padding: 2rem 1.8rem;
  }
  #info-panel.open { transform: translateX(0); }
  #info-panel::-webkit-scrollbar { width: 4px; }
  #info-panel::-webkit-scrollbar-track { background: transparent; }
  #info-panel::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }
  #panel-close {
    position: absolute; top: 18px; right: 18px;
    background: none; border: none; color: rgba(255,255,255,0.5);
    font-size: 1.6rem; cursor: pointer;
    transition: color 0.2s; line-height: 1;
  }
  #panel-close:hover { color: #fff; }
  #panel-title {
    font-size: 1.6rem; font-weight: 300; letter-spacing: 2px;
    margin-bottom: 1.8rem; padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
  }
  .panel-section {
    margin-bottom: 1.6rem;
  }
  .panel-section h3 {
    font-size: 0.75rem; font-weight: 600; letter-spacing: 3px;
    text-transform: uppercase;
    opacity: 0.5; margin-bottom: 0.6rem;
  }
  .panel-section ul {
    list-style: none;
  }
  .panel-section li {
    padding: 0.5rem 0.75rem;
    margin-bottom: 4px;
    border-radius: 8px;
    background: rgba(255,255,255,0.04);
    border-left: 2px solid rgba(255,255,255,0.08);
    font-size: 0.9rem; font-weight: 300;
    transition: background 0.2s;
  }
  .panel-section li:hover {
    background: rgba(255,255,255,0.08);
  }
  .cat-stem   { --cat-color: #00bfff; }
  .cat-human  { --cat-color: #ff6b35; }
  .cat-lang   { --cat-color: #00e676; }
  .cat-econ   { --cat-color: #ffd700; }
  @media (max-width: 600px) {
    #header h1 { font-size: 1.1rem; letter-spacing: 3px; }
    #header p  { font-size: 0.7rem; }
    #info-panel { width: 100vw; max-width: 100vw; padding: 1.2rem; }
    #panel-title { font-size: 1.2rem; }
  }
</style>
</head>
<body>
  <div id="header">
    <h1>&#10022; Cosmic Curriculum</h1>
    <p>Click a star to explore</p>
  </div>
  <div id="tooltip"></div>
  <div id="canvas-container"></div>
  <div id="info-panel">
    <button id="panel-close">&times;</button>
    <div id="panel-title"></div>
    <div id="panel-body">
      <div class="panel-section">
        <h3>School Topics</h3>
        <ul id="panel-school"></ul>
      </div>
      <div class="panel-section">
        <h3>University Topics</h3>
        <ul id="panel-uni"></ul>
      </div>
    </div>
  </div>
  <script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/"
    }
  }
  </script>
  <script type="module">
  const CATEGORIES = {
    stem: { label: 'STEM & Natural Sciences', color: '#00bfff', cssClass: 'cat-stem' },
    human: { label: 'Humanities',             color: '#ff6b35', cssClass: 'cat-human' },
    lang:  { label: 'Foreign Languages',       color: '#00e676', cssClass: 'cat-lang'  },
    econ:  { label: 'Economics & Law',         color: '#ffd700', cssClass: 'cat-econ'  },
  };
  const SUBJECTS = [
    { id: 'math',      name: 'Mathematics', category: 'stem', pos: [ 0.0,  0.5,  7.0 ],
      school: ['Arithmetic & Number Theory','Algebra','Geometry & Trigonometry','Calculus Basics','Probability & Statistics'],
      uni:    ['Real Analysis','Abstract Algebra','Topology','Differential Geometry','Number Theory'] },
    { id: 'physics',   name: 'Physics', category: 'stem', pos: [ 5.5,  1.2,  3.5 ],
      school: ['Mechanics','Thermodynamics','Optics & Waves','Electricity & Magnetism'],
      uni:    ['Quantum Mechanics','Relativity','Statistical Mechanics','Particle Physics','Astrophysics'] },
    { id: 'chemistry', name: 'Chemistry', category: 'stem', pos: [-5.5, -1.2,  3.5 ],
      school: ['Atomic Structure','Chemical Bonding','Stoichiometry','Organic Chemistry Basics'],
      uni:    ['Quantum Chemistry','Spectroscopy','Polymer Chemistry','Biochemistry','Computational Chemistry'] },
    { id: 'german',    name: 'German', category: 'human', pos: [-4.5,  2.0, -4.0 ],
      school: ['Grammar & Syntax','Text Analysis','Essay Writing','German Literature'],
      uni:    ['German Linguistics',' Medieval Literature','Comparative Literature','German Philology'] },
    { id: 'history',   name: 'History', category: 'human', pos: [ 0.0, -2.2, -6.5 ],
      school: ['Ancient Civilizations','Medieval History','Modern History','World Wars & Cold War'],
      uni:    ['Historiography','Economic History','Cultural History','Historical Methods','Global History'] },
    { id: 'philosophy', name: 'Philosophy', category: 'human', pos: [ 4.5,  1.8, -4.5 ],
      school: ['Logic & Reasoning','Ethics','Political Philosophy','Epistemology Basics'],
      uni:    ['Metaphysics','Philosophy of Mind','Continental Philosophy','Analytic Philosophy','Philosophy of Science'] },
    { id: 'english',   name: 'English', category: 'lang', pos: [ 6.0, -0.6, -1.5 ],
      school: ['Reading Comprehension','Creative Writing','Grammar & Style','Literary Analysis'],
      uni:    ['English Linguistics','Shakespeare Studies','Postcolonial Literature','Critical Theory','Rhetoric'] },
    { id: 'french',    name: 'French', category: 'lang', pos: [-6.0,  0.8, -1.0 ],
      school: ['Vocabulary & Grammar','Conversation','French Culture','French Literature'],
      uni:    ['French Linguistics','Francophone Studies','French Philosophy','Translation Studies'] },
    { id: 'spanish',   name: 'Spanish', category: 'lang', pos: [ 1.5,  3.8, -5.0 ],
      school: ['Vocabulary & Grammar','Conversation','Latin American Culture','Spanish Literature'],
      uni:    ['Spanish Linguistics',' Latin American Studies','Bilingualism','Translation Studies','Hispanic Literature'] },
    { id: 'business',  name: 'Business', category: 'econ', pos: [-2.0, -2.8,  5.5 ],
      school: ['Business Basics','Marketing','Accounting','Entrepreneurship'],
      uni:    ['Corporate Strategy','Organizational Behaviour','Supply Chain Management','Business Ethics','Innovation Management'] },
    { id: 'economics', name: 'Economics', category: 'econ', pos: [ 3.5, -2.5,  3.0 ],
      school: ['Supply & Demand','Market Structures','Macroeconomics','Personal Finance'],
      uni:    ['Microeconomic Theory','Econometrics','Game Theory','Development Economics','Behavioural Economics'] },
    { id: 'law',       name: 'Law', category: 'econ', pos: [-3.0, -1.5, -5.0 ],
      school: ['Constitutional Basics','Criminal Law','Civil Law','Legal Reasoning'],
      uni:    ['Jurisprudence','International Law','Contract Law','Constitutional Theory','Criminal Justice'] },
  ];
  import * as THREE from 'three';
  import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
  import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
  const container = document.getElementById('canvas-container');
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x070714);
  const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 500);
  camera.position.set(0, 4, 16);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  container.appendChild(renderer.domElement);
  const labelRenderer = new CSS2DRenderer();
  labelRenderer.setSize(window.innerWidth, window.innerHeight);
  labelRenderer.domElement.style.position = 'absolute';
  labelRenderer.domElement.style.top = '0';
  labelRenderer.domElement.style.left = '0';
  labelRenderer.domElement.style.pointerEvents = 'none';
  container.appendChild(labelRenderer.domElement);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 3;
  controls.maxDistance = 40;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.6;
  const ambientLight = new THREE.AmbientLight(0x222244, 0.6);
  scene.add(ambientLight);
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
  dirLight.position.set(5, 10, 7);
  scene.add(dirLight);
  const backLight = new THREE.DirectionalLight(0x6688ff, 0.4);
  backLight.position.set(-5, -5, -10);
  scene.add(backLight);
  function createStarField() {
    const count = 3000;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 50 + Math.random() * 150;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      positions[i*3]   = r * Math.sin(phi) * Math.cos(theta);
      positions[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i*3+2] = r * Math.cos(phi);
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const mat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.25, sizeAttenuation: true, transparent: true, opacity: 0.8 });
    const stars = new THREE.Points(geo, mat);
    scene.add(stars);
    return stars;
  }
  const starField = createStarField();
  function makeGlowTexture() {
    const c = document.createElement('canvas');
    c.width = 256; c.height = 256;
    const ctx = c.getContext('2d');
    const grad = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
    grad.addColorStop(0,   'rgba(255,255,255,1)');
    grad.addColorStop(0.15,'rgba(255,255,255,0.9)');
    grad.addColorStop(0.4, 'rgba(255,255,255,0.3)');
    grad.addColorStop(0.7, 'rgba(255,255,255,0.08)');
    grad.addColorStop(1,   'rgba(255,255,255,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 256, 256);
    return new THREE.CanvasTexture(c);
  }
  const glowTexture = makeGlowTexture();
  const starMeshes = [];
  const starObjects = [];
  SUBJECTS.forEach((s, index) => {
    const cat = CATEGORIES[s.category];
    const color = new THREE.Color(cat.color);
    const geo = new THREE.SphereGeometry(0.6, 32, 32);
    const mat = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.3, roughness: 0.2, metalness: 0.1 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(s.pos[0], s.pos[1], s.pos[2]);
    mesh.userData.subjectIndex = index;
    scene.add(mesh);
    starMeshes.push(mesh);
    const glowMat = new THREE.SpriteMaterial({ map: glowTexture, color, transparent: true, blending: THREE.AdditiveBlending, opacity: 0.45, depthWrite: false });
    const glow = new THREE.Sprite(glowMat);
    glow.scale.set(3.2, 3.2, 1);
    glow.position.set(s.pos[0], s.pos[1], s.pos[2]);
    scene.add(glow);
    const labelDiv = document.createElement('div');
    labelDiv.textContent = s.name;
    labelDiv.style.color = '#fff';
    labelDiv.style.fontSize = '14px';
    labelDiv.style.fontWeight = '400';
    labelDiv.style.letterSpacing = '1px';
    labelDiv.style.textShadow = '0 0 20px ' + cat.color + ', 0 0 60px ' + cat.color;
    labelDiv.style.background = 'rgba(0,0,0,0.35)';
    labelDiv.style.padding = '4px 14px';
    labelDiv.style.borderRadius = '12px';
    labelDiv.style.border = '1px solid ' + cat.color + '44';
    labelDiv.style.backdropFilter = 'blur(4px)';
    labelDiv.style.pointerEvents = 'none';
    const label = new CSS2DObject(labelDiv);
    label.position.set(s.pos[0], s.pos[1] - 1.2, s.pos[2]);
    scene.add(label);
    starObjects.push({ mesh, glow, label, data: s, defaultScale: 1, meshMat: mat, glowMat });
  });
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let hoveredIndex = -1;
  let selectedIndex = -1;
  const tooltipEl = document.getElementById('tooltip');
  function onPointerMove(event) {
    const rect = renderer.domElement.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const intersects = raycaster.intersectObjects(starMeshes);
    if (intersects.length > 0) {
      const idx = intersects[0].object.userData.subjectIndex;
      if (idx !== undefined && idx !== hoveredIndex) {
        clearHover();
        hoveredIndex = idx;
        const obj = starObjects[idx];
        obj.meshMat.emissiveIntensity = 0.8;
        obj.glowMat.opacity = 0.8;
      }
      renderer.domElement.style.cursor = 'pointer';
      const s = SUBJECTS[idx];
      tooltipEl.textContent = s.name;
      tooltipEl.style.left = (event.clientX + 14) + 'px';
      tooltipEl.style.top  = (event.clientY - 10) + 'px';
      tooltipEl.classList.add('visible');
    } else {
      if (hoveredIndex >= 0) {
        const obj = starObjects[hoveredIndex];
        obj.meshMat.emissiveIntensity = 0.3;
        obj.glowMat.opacity = 0.45;
        hoveredIndex = -1;
      }
      renderer.domElement.style.cursor = 'default';
      tooltipEl.classList.remove('visible');
    }
  }
  function clearHover() {
    if (hoveredIndex >= 0) {
      const obj = starObjects[hoveredIndex];
      obj.meshMat.emissiveIntensity = 0.3;
      obj.glowMat.opacity = 0.45;
    }
    hoveredIndex = -1;
  }
  function onClick(event) {
    const panel = document.getElementById('info-panel');
    if (panel.classList.contains('open')) {
      const rect = panel.getBoundingClientRect();
      if (event.clientX < rect.left) { closePanel(); return; }
    }
    const rect = renderer.domElement.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const intersects = raycaster.intersectObjects(starMeshes);
    if (intersects.length > 0) {
      const idx = intersects[0].object.userData.subjectIndex;
      if (idx !== undefined) selectStar(idx);
    }
  }
  let isAnimating = false;
  function selectStar(idx) {
    if (isAnimating) return;
    selectedIndex = idx;
    const obj = starObjects[idx];
    const pos = obj.mesh.position.clone();
    const startPos = camera.position.clone();
    const startTarget = controls.target.clone();
    const endTarget = pos.clone();
    const dir = pos.clone().normalize();
    const endPos = pos.clone().add(dir.clone().multiplyScalar(-3.5));
    endPos.y += 1.2;
    isAnimating = true;
    controls.enabled = false;
    controls.autoRotate = false;
    const duration = 900;
    const startTime = performance.now();
    function animStep() {
      const t = Math.min((performance.now() - startTime) / duration, 1);
      const e = 1 - Math.pow(1 - t, 3);
      camera.position.lerpVectors(startPos, endPos, e);
      controls.target.lerpVectors(startTarget, endTarget, e);
      controls.update();
      if (t < 1) requestAnimationFrame(animStep);
      else { isAnimating = false; controls.enabled = true; openPanel(idx); }
    }
    animStep();
  }
  const panel = document.getElementById('info-panel');
  const panelTitle = document.getElementById('panel-title');
  const panelSchool = document.getElementById('panel-school');
  const panelUni = document.getElementById('panel-uni');
  const panelClose = document.getElementById('panel-close');
  function openPanel(idx) {
    const s = SUBJECTS[idx];
    const cat = CATEGORIES[s.category];
    panelTitle.textContent = s.name;
    panelTitle.style.borderBottomColor = cat.color;
    panel.className = 'open ' + cat.cssClass;
    panelSchool.innerHTML = '';
    s.school.forEach(topic => {
      const li = document.createElement('li');
      li.textContent = topic;
      li.style.borderLeftColor = cat.color;
      panelSchool.appendChild(li);
    });
    panelUni.innerHTML = '';
    s.uni.forEach(topic => {
      const li = document.createElement('li');
      li.textContent = topic;
      li.style.borderLeftColor = cat.color;
      panelUni.appendChild(li);
    });
  }
  function closePanel() {
    panel.classList.remove('open');
    panel.className = '';
    selectedIndex = -1;
    controls.autoRotate = true;
  }
  panelClose.addEventListener('click', closePanel);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && panel.classList.contains('open')) closePanel();
  });
  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    const elapsed = clock.getElapsedTime();
    starField.rotation.y = elapsed * 0.004;
    starField.rotation.x = Math.sin(elapsed * 0.002) * 0.02;
    starObjects.forEach((obj, i) => {
      obj.mesh.rotation.y += 0.008;
      obj.mesh.rotation.x += 0.003;
      const offset = i * 0.5;
      const floatY = Math.sin(elapsed * 0.3 + offset) * 0.06;
      const baseY = obj.data.pos[1];
      obj.mesh.position.y = baseY + floatY;
      obj.glow.position.y = baseY + floatY;
      obj.label.position.y = baseY - 1.2 + floatY;
      if (i === hoveredIndex) {
        const pulse = 1 + Math.sin(elapsed * 3 + offset) * 0.08;
        obj.mesh.scale.setScalar(1.2 + (pulse - 1));
        obj.glowMat.opacity = 0.7 + Math.sin(elapsed * 2.5 + offset) * 0.15;
      } else if (i !== selectedIndex || !panel.classList.contains('open')) {
        obj.mesh.scale.setScalar(1);
      }
      if (i === selectedIndex && panel.classList.contains('open')) {
        obj.mesh.scale.setScalar(1 + Math.sin(elapsed * 2 + offset) * 0.05);
        obj.meshMat.emissiveIntensity = 0.6 + Math.sin(elapsed * 2.5) * 0.2;
      }
    });
    controls.update();
    renderer.render(scene, camera);
    labelRenderer.render(scene, camera);
  }
  animate();
  renderer.domElement.addEventListener('pointermove', onPointerMove);
  renderer.domElement.addEventListener('click', onClick);
  function onResize() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
    labelRenderer.setSize(w, h);
  }
  window.addEventListener('resize', onResize);
  </script>
</body>
</html>"""

@app.route("/")
def index():
    return HTML

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
