const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const buildDir = path.join(root, 'frontend', 'build');

fs.rmSync(buildDir, { recursive: true, force: true });
fs.mkdirSync(path.join(buildDir, 'static'), { recursive: true });

fs.writeFileSync(path.join(buildDir, 'index.html'), `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>BridgeGuard MVP</title>
  <link rel="stylesheet" href="/static/app.css" />
</head>
<body>
  <main class="shell">
    <header class="hero">
      <div>
        <p class="eyebrow">Defensive-only runtime security kernel</p>
        <h1>BridgeGuard</h1>
        <p class="subtitle">Runtime Security Kernel for Cross-Chain Bridges</p>
      </div>
      <div class="status-card"><span class="status-dot" id="api-dot"></span><div><strong id="api-status">Checking API</strong><small id="api-detail">http://127.0.0.1:8000</small></div></div>
    </header>
    <section class="kpi-grid">
      <article class="kpi"><span>Loaded incidents</span><strong id="kpi-incidents">--</strong></article>
      <article class="kpi"><span>Connectors</span><strong id="kpi-connectors">--</strong></article>
      <article class="kpi"><span>Last decision</span><strong id="kpi-decision">--</strong></article>
      <article class="kpi"><span>Risk score</span><strong id="kpi-risk">--</strong></article>
    </section>
    <section class="workspace">
      <article class="card">
        <div class="card-head"><div><p class="eyebrow">Scenario replay</p><h2>Historical Incident</h2></div><button class="ghost-button" id="run-all">Run All</button></div>
        <label class="field-label" for="attack">Select incident</label>
        <select id="attack"></select>
        <button id="run" class="primary-button">Simulate Selected Incident</button>
        <div id="incident" class="incident-profile"></div>
      </article>
      <article class="card">
        <div class="card-head"><div><p class="eyebrow">Runtime policy output</p><h2>Decision Brief</h2></div><button class="ghost-button" id="export" disabled>Export JSON</button></div>
        <div id="decision" class="empty-state">Select an incident or evaluate a connector to generate a client-facing decision brief.</div>
      </article>
    </section>
    <section class="lower-grid">
      <article class="card"><p class="eyebrow">Regression visibility</p><h2>Scenario Matrix</h2><div id="matrix" class="matrix"></div></article>
      <article class="card"><p class="eyebrow">Tester focus</p><h2>What To Verify</h2><ul class="checklist"><li>Policy output is explainable and deterministic.</li><li>Expected scenario decisions match replay results.</li><li>Connectors are read-only local configs.</li><li>No live transaction signing, exploit payload, or secret storage is present.</li></ul><div class="history"><h3>Recent local decisions</h3><div id="history-list" class="history-list muted">No local decisions yet.</div></div></article>
    </section>
    <section class="card connectors-card">
      <div class="card-head"><div><p class="eyebrow">Plug-and-play security layer</p><h2>Connectors</h2></div><div class="toolbar"><button class="ghost-button" id="load-presets">Load preset connectors</button><button class="ghost-button" id="refresh-connectors">Refresh</button></div></div>
      <p class="summary">Configure read-only EVM bridge connectors, store them locally, and evaluate them through BridgeGuard policy decisions. Without Web3/RPC access, the backend returns safe mock data for workflow testing.</p>
      <div class="connectors-grid">
        <div class="connector-form">
          <textarea id="connector-json" class="input textarea" rows="7" placeholder="Paste full ConnectorConfig JSON here, or use the fields below."></textarea>
          <input id="connector-name" class="input" value="Demo EVM Bridge" placeholder="Connector name" />
          <input id="connector-rpc" class="input" value="mock://local" placeholder="RPC URL" />
          <input id="connector-address" class="input" value="0x0000000000000000000000000000000000000000" placeholder="Contract address" />
          <div class="mini-grid"><input id="connector-chain" class="input" value="1" placeholder="Chain ID" /><input id="connector-asset" class="input" value="ETH" placeholder="Asset" /><input id="connector-source" class="input" value="Ethereum" placeholder="Source chain" /><input id="connector-dest" class="input" value="Arbitrum" placeholder="Destination chain" /></div>
          <textarea id="connector-abi" class="input textarea" rows="4">[]</textarea>
          <button class="primary-button" id="create-connector">Create Connector</button>
        </div>
        <div><div id="connectors-list" class="history-list muted">Loading connectors...</div><div id="connector-result" class="connector-result muted"></div></div>
      </div>
    </section>
  </main>
  <script src="/static/app.js"></script>
</body>
</html>`);

fs.writeFileSync(path.join(buildDir, 'static', 'app.css'), `
:root{--bg:#0b0f19;--panel:#1a1f2e;--line:#2a2f3e;--text:#e0e0e0;--muted:#9ca3af;--blue:#2d6ff7;--blue2:#1a5be0;--green:#22c55e;--orange:#f59e0b;--red:#ef4444;--red2:#991b1b;--violet:#a855f7}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top left,#13203a 0,#0b0f19 34%,#070b12 100%);color:var(--text);font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif}button,select,input,textarea{font:inherit}a{color:#93c5fd}.shell{width:min(1480px,calc(100% - 40px));margin:0 auto;padding:26px 0 44px}.hero{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;margin-bottom:22px}.eyebrow{margin:0 0 8px;color:#93c5fd;text-transform:uppercase;letter-spacing:.08em;font-size:12px;font-weight:800}.hero h1{margin:0;font-size:52px;line-height:1}.subtitle{margin:10px 0 0;color:#cbd5e1;font-size:20px}.status-card,.kpi,.card{background:rgba(26,31,46,.92);border:1px solid var(--line);border-radius:12px;box-shadow:0 18px 45px rgba(0,0,0,.28)}.status-card{display:flex;align-items:center;gap:12px;padding:14px 16px;min-width:245px}.status-card small,.muted{color:var(--muted)}.status-dot{width:12px;height:12px;border-radius:50%;background:var(--orange);box-shadow:0 0 18px var(--orange)}.status-dot.ok{background:var(--green);box-shadow:0 0 18px var(--green)}.status-dot.bad{background:var(--red);box-shadow:0 0 18px var(--red)}.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:18px}.kpi{padding:16px}.kpi span{display:block;color:var(--muted);font-size:13px}.kpi strong{display:block;margin-top:7px;font-size:24px}.workspace{display:grid;grid-template-columns:minmax(360px,.95fr) minmax(460px,1.05fr);gap:18px;margin-bottom:18px}.lower-grid{display:grid;grid-template-columns:1.25fr .75fr;gap:18px}.card{padding:24px;margin-bottom:18px}.card-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;margin-bottom:16px}.toolbar{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}.card h2{margin:0 0 14px;font-size:28px}.field-label{display:block;color:#cbd5e1;font-weight:800;margin-bottom:8px}select,.primary-button,.ghost-button,.input{width:100%;border-radius:10px;padding:13px 14px;border:1px solid #34405a;background:#0f172a;color:var(--text)}.primary-button{margin-top:12px;border-color:#3b82f6;background:var(--blue);font-weight:900;cursor:pointer}.primary-button:hover{background:var(--blue2)}.ghost-button{width:auto;background:#162033;cursor:pointer;color:#dbeafe}.ghost-button:disabled{opacity:.5;cursor:not-allowed}.incident-profile{margin-top:18px;display:grid;gap:14px}.incident-title{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.incident-title h3{margin:0;font-size:25px}.pill,.badge{display:inline-flex;align-items:center;min-height:28px;padding:5px 9px;border-radius:999px;font-size:12px;font-weight:900;border:1px solid #3c4a62;background:#253044;color:#dbeafe}.fact-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.fact,.text-box,.history-item,.connector-result{background:#111827;border:1px solid var(--line);border-radius:10px;padding:12px}.fact span{display:block;color:var(--muted);font-size:12px;text-transform:uppercase;font-weight:800}.fact strong{display:block;margin-top:5px}.summary{color:#dbeafe;line-height:1.55}.decision-hero{display:grid;grid-template-columns:150px 1fr;gap:22px;align-items:center}.gauge{width:150px;height:150px;transform:rotate(-90deg)}.gauge-track,.gauge-fill{fill:none;stroke-width:13}.gauge-track{stroke:#0f172a}.gauge-fill{stroke-linecap:round}.gauge-text{fill:var(--text);font-size:30px;font-weight:900;text-anchor:middle;transform:rotate(90deg);transform-origin:60px 60px}.decision-word{font-size:42px;font-weight:1000}.FREEZE{color:var(--red)}.DELAY{color:var(--orange)}.REQUIRE_EXTRA_SIGNATURES{color:#60a5fa}.ESCALATE_TO_GUARDIANS{color:var(--violet)}.ALLOW{color:var(--green)}.score-low{stroke:var(--green)}.score-medium{stroke:var(--orange)}.score-high{stroke:var(--red2)}.score-critical{stroke:var(--red)}.decision-copy{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:18px}.badge-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}.critical{background:rgba(239,68,68,.18);border-color:rgba(239,68,68,.55);color:#fecaca}.high{background:rgba(153,27,27,.22);border-color:rgba(185,28,28,.55);color:#fecaca}.medium{background:rgba(245,158,11,.18);border-color:rgba(245,158,11,.55);color:#fde68a}.low{background:rgba(34,197,94,.16);border-color:rgba(34,197,94,.5);color:#bbf7d0}.matrix,.history-list,.connector-form{display:grid;gap:8px}.matrix-row{display:grid;grid-template-columns:1.2fr .7fr .7fr 90px;gap:10px;align-items:center;padding:10px 12px;background:#111827;border:1px solid var(--line);border-radius:10px}.matrix-row.header{background:#0f172a;color:#cbd5e1;font-weight:900}.match{color:var(--green);font-weight:900}.mismatch{color:var(--red);font-weight:900}.checklist{margin:0;padding-left:20px;color:#dbeafe;line-height:1.65}.history{margin-top:22px}.empty-state{min-height:260px;display:grid;place-items:center;text-align:center;color:var(--muted);border:1px dashed #34405a;border-radius:12px;padding:24px}.connectors-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.mini-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.textarea{resize:vertical}.connector-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}.danger{border-color:rgba(239,68,68,.55);color:#fecaca}.connector-result{margin-top:12px}
@media(max-width:1000px){.hero,.workspace,.lower-grid,.connectors-grid{grid-template-columns:1fr;display:grid}.kpi-grid{grid-template-columns:repeat(2,1fr)}.decision-hero,.decision-copy,.mini-grid{grid-template-columns:1fr}.matrix-row{grid-template-columns:1fr}.matrix-row.header{display:none}}
`);

fs.writeFileSync(path.join(buildDir, 'static', 'app.js'), `
const $=id=>document.getElementById(id);let attacks=[],lastDecision=null;
const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
async function json(url,opts){const r=await fetch(url,opts);if(!r.ok){let detail=r.status+' '+r.statusText;try{const body=await r.json();detail=body.detail||detail;}catch(e){}throw new Error(detail);}return r.json();}
function riskClass(s){return s<=30?'score-low':s<=60?'score-medium':s<=84?'score-high':'score-critical'}
function reasonClass(c){if(['MINT_EXCEEDS_LOCKED','RELEASE_EXCEEDS_BURNED','REPLAY_OR_DUPLICATE_MESSAGE','EMERGENCY_MODE_ACTIVE'].includes(c))return'critical';if(['CONFIG_CHANGE_UNCOOLED','UNKNOWN_OR_CHANGED_ROOT','VALIDATOR_SET_RISK','TVL_DIVERGENCE'].includes(c))return'high';if(['SIGNER_THRESHOLD_WEAK','CHAIN_FINALITY_NOT_REACHED','ROUTE_CAP_EXCEEDED','ASSET_CAP_EXCEEDED'].includes(c))return'medium';return'low'}
function selectedAttack(){return attacks.find(a=>a.name===$('attack').value)}
function renderIncident(a){if(!a)return;$('incident').innerHTML='<div class="incident-title"><h3>'+esc(a.name)+'</h3><span class="pill">'+esc(a.expected_decision)+'</span></div><div class="fact-grid"><div class="fact"><span>Date</span><strong>'+esc(a.date)+'</strong></div><div class="fact"><span>Estimated loss</span><strong>'+esc(a.loss)+'</strong></div><div class="fact"><span>Bridge type</span><strong>'+esc(a.bridge_type)+'</strong></div><div class="fact"><span>Root cause</span><strong>'+esc(a.root_cause_category)+'</strong></div></div><p class="summary">'+esc(a.summary)+'</p><span class="pill">'+esc(a.violated_invariant)+'</span><p class="summary"><b>Defensive control:</b> '+esc(a.defensive_control)+'</p>'+(a.source?'<a target="_blank" rel="noreferrer" href="'+esc(a.source)+'">Open public source</a>':'');}
function renderDecision(d,a){lastDecision=d;const score=Math.max(0,Math.min(100,Number(d.risk_score)||0));const badges=(d.reason_codes||[]).map(x=>'<span class="badge '+reasonClass(x)+'">'+esc(x)+'</span>').join('');const matched=!a||d.decision===a.expected_decision;$('kpi-decision').textContent=d.decision;$('kpi-risk').textContent=score.toFixed(0)+'/100';$('export').disabled=false;$('decision').className='';$('decision').innerHTML='<div class="decision-hero"><svg class="gauge '+riskClass(score)+'" viewBox="0 0 120 120"><circle class="gauge-track" cx="60" cy="60" r="48" pathLength="100"></circle><circle class="gauge-fill" cx="60" cy="60" r="48" pathLength="100" stroke-dasharray="100" stroke-dashoffset="'+(100-score)+'"></circle><text class="gauge-text" x="60" y="65">'+score.toFixed(0)+'</text></svg><div><div class="decision-word '+esc(d.decision)+'">'+esc(d.decision)+'</div><p class="'+(matched?'match':'mismatch')+'">'+(a?(matched?'Matches expected policy':'Does not match expected policy'):'Connector evaluation')+'</p><div class="badge-row">'+badges+'</div></div></div><div class="decision-copy"><div class="text-box"><h3>Why it fired</h3><p>'+esc(d.explanation)+'</p></div><div class="text-box"><h3>Recommended action</h3><p>'+esc(d.recommended_action)+'</p></div></div>';renderHistory();}
async function runSelected(){const a=selectedAttack();if(!a)return;try{renderDecision(await json('/simulate-attack/'+encodeURIComponent(a.name),{method:'POST'}),a);renderMatrix();}catch(e){$('decision').className='empty-state';$('decision').textContent='Simulation failed: '+e.message;}}
async function runAll(){for(const a of attacks){try{await json('/simulate-attack/'+encodeURIComponent(a.name),{method:'POST'});}catch(e){}}await renderHistory();await renderMatrix();}
async function renderMatrix(){const rows=[];for(const a of attacks){try{const d=await json('/simulate-attack/'+encodeURIComponent(a.name),{method:'POST'});rows.push({a,d,ok:d.decision===a.expected_decision});}catch(e){rows.push({a,d:null,ok:false});}}$('matrix').innerHTML='<div class="matrix-row header"><span>Incident</span><span>Expected</span><span>Actual</span><span>Status</span></div>'+rows.map(r=>'<div class="matrix-row"><strong>'+esc(r.a.name)+'</strong><span>'+esc(r.a.expected_decision)+'</span><span>'+esc(r.d?r.d.decision:'ERROR')+'</span><span class="'+(r.ok?'match':'mismatch')+'">'+(r.ok?'MATCH':'CHECK')+'</span></div>').join('');}
async function renderHistory(){try{const data=await json('/decisions');const items=data.slice(-5).reverse();$('history-list').innerHTML=items.length?items.map(d=>'<div class="history-item"><strong>'+esc(d.decision)+'</strong><br><span>'+new Date(d.timestamp).toLocaleString()+' | score '+Number(d.risk_score).toFixed(0)+' | '+esc((d.reason_codes||[])[0]||'NO_REASON')+'</span></div>').join(''):'No local decisions yet.';}catch(e){$('history-list').textContent='History unavailable: '+e.message;}}
async function loadConnectors(){try{const data=await json('/connectors/');$('kpi-connectors').textContent=data.length;$('connectors-list').innerHTML=data.length?data.map(c=>'<div class="history-item"><strong>'+esc(c.name)+'</strong><br><span>'+esc(c.source_chain)+' to '+esc(c.dest_chain)+' | '+esc(c.asset)+' | chain '+esc(c.chain_id)+'</span><div class="connector-actions"><button class="ghost-button" onclick="evaluateConnector(\\''+esc(c.id)+'\\')">Evaluate</button><button class="ghost-button danger" onclick="deleteConnector(\\''+esc(c.id)+'\\')">Delete</button></div></div>').join(''):'No connectors configured yet.';}catch(e){$('connectors-list').textContent='Connectors unavailable: '+e.message;}}
async function createConnector(){try{const pasted=$('connector-json').value.trim();const body=pasted?JSON.parse(pasted):{id:'',name:$('connector-name').value,type:'evm',enabled:true,rpc_url:$('connector-rpc').value,chain_id:Number($('connector-chain').value)||1,contract_address:$('connector-address').value,abi:JSON.parse($('connector-abi').value||'[]'),method_mapping:{locked_collateral:'totalLocked',minted_supply:'totalMinted',burned_proven:'totalBurned',released_supply:'totalReleased'},daily_cap:1000000,route_cap:500000,asset_cap:2000000,source_chain:$('connector-source').value,dest_chain:$('connector-dest').value,asset:$('connector-asset').value,finality_blocks:10};body.id=body.id||'';await json('/connectors/',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});$('connector-result').textContent='Connector created locally.';await loadConnectors();}catch(e){$('connector-result').textContent='Create failed: '+e.message;}}
async function loadPresetConnectors(){try{const existing=await json('/connectors/');const presets=await json('/connectors/presets');const keys=new Set(existing.map(c=>(c.name||'').toLowerCase()+'|'+c.chain_id+'|'+(c.contract_address||'').toLowerCase()));const missing=presets.filter(c=>!keys.has((c.name||'').toLowerCase()+'|'+c.chain_id+'|'+(c.contract_address||'').toLowerCase()));for(const preset of missing){preset.id='';await json('/connectors/',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(preset)});}$('connector-result').textContent=missing.length?'Loaded '+missing.length+' preset connector(s).':'Preset connectors are already loaded.';await loadConnectors();}catch(e){$('connector-result').textContent='Preset load failed: '+e.message;}}
async function evaluateConnector(id){try{const d=await json('/connectors/'+encodeURIComponent(id)+'/evaluate',{method:'POST'});$('connector-result').innerHTML='<strong>'+esc(d.decision)+'</strong> | score '+Number(d.risk_score).toFixed(0)+(d.warning?'<p class="muted">'+esc(d.warning)+'</p>':'');renderDecision(d,null);}catch(e){$('connector-result').textContent='Evaluate failed: '+e.message;}}
async function deleteConnector(id){try{await json('/connectors/'+encodeURIComponent(id),{method:'DELETE'});$('connector-result').textContent='Connector deleted.';await loadConnectors();}catch(e){$('connector-result').textContent='Delete failed: '+e.message;}}
globalThis.evaluateConnector=evaluateConnector;globalThis.deleteConnector=deleteConnector;
$('run').onclick=runSelected;$('run-all').onclick=runAll;$('create-connector').onclick=createConnector;$('load-presets').onclick=loadPresetConnectors;$('refresh-connectors').onclick=loadConnectors;$('export').onclick=()=>{if(!lastDecision)return;const blob=new Blob([JSON.stringify(lastDecision,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='bridgeguard-decision.json';a.click();URL.revokeObjectURL(url)};$('attack').onchange=()=>renderIncident(selectedAttack());
async function init(){try{const health=await json('/health');$('api-dot').className='status-dot ok';$('api-status').textContent='API online';$('api-detail').textContent='version '+health.version;attacks=await json('/attacks');$('kpi-incidents').textContent=attacks.length;$('attack').innerHTML=attacks.map(a=>'<option>'+esc(a.name)+'</option>').join('');renderIncident(attacks[0]);await renderMatrix();await renderHistory();await loadConnectors();}catch(e){$('api-dot').className='status-dot bad';$('api-status').textContent='API offline';$('api-detail').textContent=e.message;}}
init();
`);

console.log('Lightweight frontend build written to frontend/build');
