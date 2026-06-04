import streamlit as st

st.set_page_config(page_title="Cosmic Curriculum", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
  .stApp { margin: 0; padding: 0; overflow: hidden; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
  iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Cosmic Curriculum</title>
<style>
  *,*::before,*::after { margin:0; padding:0; box-sizing:border-box; }
  html,body { width:100%; height:100%; overflow:hidden; background:#0a0a1a; color:#fff; font-family:'Segoe UI',system-ui,-apple-system,sans-serif; user-select:none; }
  #error-msg { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; color:#fff; font-size:1.2rem; background:#0a0a1a; z-index:100; padding:2rem; text-align:center; }
  #error-msg.hidden { display:none; }
  #canvas-container { position:fixed; inset:0; z-index:0; }
  #header { position:fixed; top:24px; left:50%; transform:translateX(-50%); z-index:10; text-align:center; pointer-events:none; }
  #header h1 { font-size:1.8rem; font-weight:300; letter-spacing:6px; text-transform:uppercase; text-shadow:0 0 30px rgba(100,180,255,0.3); }
  #header p { font-size:0.85rem; opacity:0.5; letter-spacing:2px; margin-top:4px; }
  #tooltip { position:fixed; z-index:20; padding:6px 16px; border-radius:20px; background:rgba(255,255,255,0.12); backdrop-filter:blur(8px); border:1px solid rgba(255,255,255,0.15); font-size:0.85rem; pointer-events:none; opacity:0; transition:opacity 0.2s; white-space:nowrap; }
  #tooltip.visible { opacity:1; }
  #info-panel { position:fixed; top:0; right:0; width:420px; max-width:92vw; height:100vh; z-index:30; background:rgba(15,15,35,0.65); backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px); border-left:1px solid rgba(255,255,255,0.10); box-shadow:-8px 0 40px rgba(0,0,0,0.5); transform:translateX(100%); transition:transform 0.45s cubic-bezier(0.22,1,0.36,1); overflow-y:auto; padding:2rem 1.8rem; }
  #info-panel.open { transform:translateX(0); }
  #info-panel::-webkit-scrollbar { width:4px; }
  #info-panel::-webkit-scrollbar-track { background:transparent; }
  #info-panel::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.2); border-radius:4px; }
  #panel-close { position:absolute; top:18px; right:18px; background:none; border:none; color:rgba(255,255,255,0.5); font-size:1.6rem; cursor:pointer; transition:color 0.2s; line-height:1; }
  #panel-close:hover { color:#fff; }
  #panel-title { font-size:1.6rem; font-weight:300; letter-spacing:2px; margin-bottom:1.8rem; padding-bottom:0.8rem; border-bottom:1px solid rgba(255,255,255,0.08); }
  .panel-section { margin-bottom:1.6rem; }
  .panel-section h3 { font-size:0.75rem; font-weight:600; letter-spacing:3px; text-transform:uppercase; opacity:0.5; margin-bottom:0.6rem; }
  .panel-section ul { list-style:none; }
  .panel-section li { padding:0.5rem 0.75rem; margin-bottom:4px; border-radius:8px; background:rgba(255,255,255,0.04); border-left:2px solid rgba(255,255,255,0.08); font-size:0.9rem; font-weight:300; transition:background 0.2s; }
  .panel-section li:hover { background:rgba(255,255,255,0.08); }
  .cat-stem { --cat-color:#00bfff; } .cat-human { --cat-color:#ff6b35; } .cat-lang { --cat-color:#00e676; } .cat-econ { --cat-color:#ffd700; }
  @media (max-width:600px) { #header h1 { font-size:1.1rem; letter-spacing:3px; } #header p { font-size:0.7rem; } #info-panel { width:100vw; max-width:100vw; padding:1.2rem; } #panel-title { font-size:1.2rem; } }
</style>
</head>
<body>
<div id="error-msg">Loading Cosmic Curriculum&hellip;</div>
<div id="header"><h1>&#10022; Cosmic Curriculum</h1><p>Click a star to explore</p></div>
<div id="tooltip"></div>
<div id="canvas-container"></div>
<div id="info-panel">
  <button id="panel-close">&times;</button>
  <div id="panel-title"></div>
  <div id="panel-body">
    <div class="panel-section"><h3>School Topics</h3><ul id="panel-school"></ul></div>
    <div class="panel-section"><h3>University Topics</h3><ul id="panel-uni"></ul></div>
  </div>
</div>
<script>
(async function() {
  const errorEl = document.getElementById('error-msg');
  try {
    const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.163.0/build/three.module.js');
    const { OrbitControls } = await import('https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/controls/OrbitControls.js');
    const { CSS2DRenderer, CSS2DObject } = await import('https://cdn.jsdelivr.net/npm/three@0.163.0/examples/jsm/renderers/CSS2DRenderer.js');

    const CATEGORIES = { stem:{label:'STEM',color:'#00bfff',cssClass:'cat-stem'}, human:{label:'Humanities',color:'#ff6b35',cssClass:'cat-human'}, lang:{label:'Languages',color:'#00e676',cssClass:'cat-lang'}, econ:{label:'Economics & Law',color:'#ffd700',cssClass:'cat-econ'} };
    const SUBJECTS = [
      { id:'math',name:'Mathematics',category:'stem',pos:[0,0.5,7], school:['Algebra','Geometry','Trigonometry','Calculus Basics','Statistics'], uni:['Real Analysis','Abstract Algebra','Topology','Differential Geometry','Number Theory'] },
      { id:'physics',name:'Physics',category:'stem',pos:[5.5,1.2,3.5], school:['Mechanics','Thermodynamics','Optics','Electricity & Magnetism'], uni:['Quantum Mechanics','Relativity','Statistical Mechanics','Particle Physics','Astrophysics'] },
      { id:'chemistry',name:'Chemistry',category:'stem',pos:[-5.5,-1.2,3.5], school:['Atomic Structure','Bonding','Stoichiometry','Organic Basics'], uni:['Quantum Chemistry','Spectroscopy','Polymer Chemistry','Biochemistry'] },
      { id:'german',name:'German',category:'human',pos:[-4.5,2,-4], school:['Grammar','Text Analysis','Essay Writing','Literature'], uni:['German Linguistics','Medieval Literature','Comparative Literature','Philology'] },
      { id:'history',name:'History',category:'human',pos:[0,-2.2,-6.5], school:['Ancient Civilizations','Medieval','Modern','World Wars'], uni:['Historiography','Economic History','Cultural History','Historical Methods'] },
      { id:'philosophy',name:'Philosophy',category:'human',pos:[4.5,1.8,-4.5], school:['Logic','Ethics','Political Philosophy','Epistemology'], uni:['Metaphysics','Philosophy of Mind','Continental','Analytic Philosophy'] },
      { id:'english',name:'English',category:'lang',pos:[6,-0.6,-1.5], school:['Comprehension','Creative Writing','Grammar','Literary Analysis'], uni:['English Linguistics','Shakespeare','Postcolonial Literature','Critical Theory'] },
      { id:'french',name:'French',category:'lang',pos:[-6,0.8,-1], school:['Vocabulary & Grammar','Conversation','Culture','Literature'], uni:['French Linguistics','Francophone Studies','French Philosophy','Translation'] },
      { id:'spanish',name:'Spanish',category:'lang',pos:[1.5,3.8,-5], school:['Vocabulary & Grammar','Conversation','Culture','Literature'], uni:['Spanish Linguistics','Latin American Studies','Bilingualism','Translation'] },
      { id:'business',name:'Business',category:'econ',pos:[-2,-2.8,5.5], school:['Business Basics','Marketing','Accounting','Entrepreneurship'], uni:['Corporate Strategy','Organizational Behaviour','Supply Chain','Business Ethics'] },
      { id:'economics',name:'Economics',category:'econ',pos:[3.5,-2.5,3], school:['Supply & Demand','Market Structures','Macroeconomics','Personal Finance'], uni:['Microeconomic Theory','Econometrics','Game Theory','Development Economics'] },
      { id:'law',name:'Law',category:'econ',pos:[-3,-1.5,-5], school:['Constitutional Basics','Criminal Law','Civil Law','Legal Reasoning'], uni:['Jurisprudence','International Law','Contract Law','Constitutional Theory'] },
    ];

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
    scene.add(new THREE.AmbientLight(0x222244, 0.6));
    const dl = new THREE.DirectionalLight(0xffffff, 1.2);
    dl.position.set(5, 10, 7);
    scene.add(dl);
    const bl = new THREE.DirectionalLight(0x6688ff, 0.4);
    bl.position.set(-5, -5, -10);
    scene.add(bl);

    (function() {
      const count = 3000;
      const positions = new Float32Array(count * 3);
      for (let i = 0; i < count; i++) {
        const r = 50 + Math.random() * 150;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);
        positions[i*3] = r * Math.sin(phi) * Math.cos(theta);
        positions[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
        positions[i*3+2] = r * Math.cos(phi);
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      scene.add(new THREE.Points(geo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.25, sizeAttenuation: true, transparent: true, opacity: 0.8 })));
    })();

    const glowTex = (function() {
      const c = document.createElement('canvas'); c.width = 256; c.height = 256;
      const ctx = c.getContext('2d');
      const g = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
      g.addColorStop(0,'rgba(255,255,255,1)'); g.addColorStop(0.15,'rgba(255,255,255,0.9)'); g.addColorStop(0.4,'rgba(255,255,255,0.3)'); g.addColorStop(0.7,'rgba(255,255,255,0.08)'); g.addColorStop(1,'rgba(255,255,255,0)');
      ctx.fillStyle = g; ctx.fillRect(0, 0, 256, 256);
      return new THREE.CanvasTexture(c);
    })();

    const starMeshes = [], starObjs = [];
    SUBJECTS.forEach((s, i) => {
      const cat = CATEGORIES[s.category];
      const col = new THREE.Color(cat.color);
      const mesh = new THREE.Mesh(new THREE.SphereGeometry(0.6, 32, 32), new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: 0.3, roughness: 0.2, metalness: 0.1 }));
      mesh.position.set(s.pos[0], s.pos[1], s.pos[2]);
      mesh.userData.subjectIndex = i;
      scene.add(mesh);
      starMeshes.push(mesh);
      const glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: col, transparent: true, blending: THREE.AdditiveBlending, opacity: 0.45, depthWrite: false }));
      glow.scale.set(3.2, 3.2, 1);
      glow.position.set(s.pos[0], s.pos[1], s.pos[2]);
      scene.add(glow);
      const div = document.createElement('div');
      div.textContent = s.name;
      div.style.cssText = 'color:#fff;font-size:14px;font-weight:400;letter-spacing:1px;text-shadow:0 0 20px ' + cat.color + ',0 0 60px ' + cat.color + ';background:rgba(0,0,0,0.35);padding:4px 14px;border-radius:12px;border:1px solid ' + cat.color + '44;backdrop-filter:blur(4px);pointer-events:none;';
      const label = new CSS2DObject(div);
      label.position.set(s.pos[0], s.pos[1] - 1.2, s.pos[2]);
      scene.add(label);
      starObjs.push({ mesh, glow, label, data: s, meshMat: mesh.material, glowMat: glow.material });
    });

    const raycaster = new THREE.Raycaster(), pointer = new THREE.Vector2();
    let hover = -1, selected = -1;
    const tooltip = document.getElementById('tooltip'), panel = document.getElementById('info-panel');
    const pTitle = document.getElementById('panel-title'), pSchool = document.getElementById('panel-school'), pUni = document.getElementById('panel-uni');

    function clearHover() { if (hover >= 0) { const o = starObjs[hover]; o.meshMat.emissiveIntensity = 0.3; o.glowMat.opacity = 0.45; } hover = -1; }
    function closeP() { panel.classList.remove('open'); panel.className = ''; selected = -1; controls.autoRotate = true; }
    function openP(idx) {
      const s = SUBJECTS[idx], c = CATEGORIES[s.category];
      pTitle.textContent = s.name; pTitle.style.borderBottomColor = c.color;
      panel.className = 'open ' + c.cssClass;
      pSchool.innerHTML = ''; s.school.forEach(t => { const l = document.createElement('li'); l.textContent = t; l.style.borderLeftColor = c.color; pSchool.appendChild(l); });
      pUni.innerHTML = ''; s.uni.forEach(t => { const l = document.createElement('li'); l.textContent = t; l.style.borderLeftColor = c.color; pUni.appendChild(l); });
    }

    renderer.domElement.addEventListener('pointermove', e => {
      const r = renderer.domElement.getBoundingClientRect();
      pointer.x = ((e.clientX - r.left) / r.width) * 2 - 1;
      pointer.y = -((e.clientY - r.top) / r.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const hits = raycaster.intersectObjects(starMeshes);
      if (hits.length > 0) {
        const idx = hits[0].object.userData.subjectIndex;
        if (idx !== undefined && idx !== hover) { clearHover(); hover = idx; const o = starObjs[idx]; o.meshMat.emissiveIntensity = 0.8; o.glowMat.opacity = 0.8; }
        renderer.domElement.style.cursor = 'pointer';
        tooltip.textContent = SUBJECTS[idx].name;
        tooltip.style.left = (e.clientX + 14) + 'px'; tooltip.style.top = (e.clientY - 10) + 'px';
        tooltip.classList.add('visible');
      } else { if (hover >= 0) clearHover(); renderer.domElement.style.cursor = 'default'; tooltip.classList.remove('visible'); }
    });

    let animating = false;
    renderer.domElement.addEventListener('click', e => {
      if (panel.classList.contains('open')) { const r = panel.getBoundingClientRect(); if (e.clientX < r.left) { closeP(); return; } }
      const r = renderer.domElement.getBoundingClientRect();
      pointer.x = ((e.clientX - r.left) / r.width) * 2 - 1;
      pointer.y = -((e.clientY - r.top) / r.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const hits = raycaster.intersectObjects(starMeshes);
      if (hits.length > 0) { const idx = hits[0].object.userData.subjectIndex; if (idx !== undefined) selectStar(idx); }
    });

    function selectStar(idx) {
      if (animating) return;
      selected = idx;
      const o = starObjs[idx], p = o.mesh.position.clone();
      const sp = camera.position.clone(), st = controls.target.clone(), et = p.clone();
      const ep = p.clone().add(p.clone().normalize().multiplyScalar(-3.5)); ep.y += 1.2;
      animating = true; controls.enabled = false; controls.autoRotate = false;
      const dur = 900, sTime = performance.now();
      (function step() { const t = Math.min((performance.now() - sTime) / dur, 1), e = 1 - Math.pow(1 - t, 3); camera.position.lerpVectors(sp, ep, e); controls.target.lerpVectors(st, et, e); controls.update(); if (t < 1) requestAnimationFrame(step); else { animating = false; controls.enabled = true; openP(idx); } })();
    }

    document.getElementById('panel-close').addEventListener('click', closeP);
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && panel.classList.contains('open')) closeP(); });

    const starField = scene.children.find(c => c.isPoints);
    const clock = new THREE.Clock();
    function animate() {
      requestAnimationFrame(animate);
      const t = clock.getElapsedTime();
      starField.rotation.y = t * 0.004; starField.rotation.x = Math.sin(t * 0.002) * 0.02;
      starObjs.forEach((o, i) => {
        o.mesh.rotation.y += 0.008; o.mesh.rotation.x += 0.003;
        const off = i * 0.5, fy = Math.sin(t * 0.3 + off) * 0.06, by = o.data.pos[1];
        o.mesh.position.y = by + fy; o.glow.position.y = by + fy; o.label.position.y = by - 1.2 + fy;
        if (i === hover) { o.mesh.scale.setScalar(1.2 + Math.sin(t * 3 + off) * 0.08); o.glowMat.opacity = 0.7 + Math.sin(t * 2.5 + off) * 0.15; }
        else if (i !== selected || !panel.classList.contains('open')) o.mesh.scale.setScalar(1);
        if (i === selected && panel.classList.contains('open')) { o.mesh.scale.setScalar(1 + Math.sin(t * 2 + off) * 0.05); o.meshMat.emissiveIntensity = 0.6 + Math.sin(t * 2.5) * 0.2; }
      });
      controls.update(); renderer.render(scene, camera); labelRenderer.render(scene, camera);
    }

    window.addEventListener('resize', () => { const w = window.innerWidth, h = window.innerHeight; camera.aspect = w / h; camera.updateProjectionMatrix(); renderer.setSize(w, h); labelRenderer.setSize(w, h); });

    errorEl.classList.add('hidden');
    animate();
  } catch (err) { errorEl.textContent = 'Error: ' + err.message; console.error(err); }
})();
</script>
</body>
</html>"""

st.components.v1.html(HTML, height=900, scrolling=False)
