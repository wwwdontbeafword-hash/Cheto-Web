from flask import Flask, jsonify, request, Response
from pathlib import Path
from urllib.parse import quote
import json
import os
import re
import threading

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "design.json"
LOCK = threading.Lock()

DEFAULT_DESIGN = {
    "version": 1,
    "title": "IDc Studio",
    "width": 470,
    "height": 420,
    "offset_x": 0,
    "offset_y": 0,
    "background": "#111318",
    "background_opacity": 0.94,
    "accent": "#ff3b30",
    "text_color": "#ffffff",
    "row_color": "#1d2028",
    "on_color": "#22c55e",
    "off_color": "#ef4444",
    "title_size": 24,
    "font_size": 16,
    "row_height": 44,
    "gap": 8,
    "corner_radius": 20,
    "items": [
        {"type": "toggle", "label": "Enemy ESP", "action": "ESP"},
        {"type": "toggle", "label": "iAwareness Text", "action": "IAwarenessText"},
        {"type": "toggle", "label": "Radar", "action": "Radar"},
        {"type": "button", "label": "TEST ON", "action": "TEST"},
        {"type": "button", "label": "Refresh design", "action": "REFRESH"},
    ],
}

ALLOWED_TYPES = {"toggle", "button", "text"}
ALLOWED_ACTIONS = {
    "NONE", "TEST", "REFRESH", "ESP", "ESPLine", "EnemyESPWeapon",
    "EnemyESPWeaponOnly", "IAwarenessText", "IAwarenessArrows", "Radar",
    "VehicleESP", "ItemESP", "GrenadeESP", "AirdropESP", "TombBoxESP",
}
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def clamp(v, lo, hi, default):
    try:
        v = float(v)
    except Exception:
        return default
    return max(lo, min(hi, v))


def clean_hex(v, default):
    v = str(v or "").strip()
    return v.lower() if HEX_RE.match(v) else default


def clean_design(raw, previous_version=0):
    if not isinstance(raw, dict):
        raw = {}
    out = dict(DEFAULT_DESIGN)
    out["version"] = max(int(previous_version) + 1, 1)
    out["title"] = str(raw.get("title", out["title"]))[:48]
    out["width"] = int(clamp(raw.get("width"), 300, 760, out["width"]))
    out["height"] = int(clamp(raw.get("height"), 220, 760, out["height"]))
    out["offset_x"] = int(clamp(raw.get("offset_x"), -500, 500, 0))
    out["offset_y"] = int(clamp(raw.get("offset_y"), -500, 500, 0))
    out["background"] = clean_hex(raw.get("background"), out["background"])
    out["background_opacity"] = round(clamp(raw.get("background_opacity"), 0.15, 1.0, out["background_opacity"]), 2)
    out["accent"] = clean_hex(raw.get("accent"), out["accent"])
    out["text_color"] = clean_hex(raw.get("text_color"), out["text_color"])
    out["row_color"] = clean_hex(raw.get("row_color"), out["row_color"])
    out["on_color"] = clean_hex(raw.get("on_color"), out["on_color"])
    out["off_color"] = clean_hex(raw.get("off_color"), out["off_color"])
    out["title_size"] = int(clamp(raw.get("title_size"), 14, 42, out["title_size"]))
    out["font_size"] = int(clamp(raw.get("font_size"), 10, 30, out["font_size"]))
    out["row_height"] = int(clamp(raw.get("row_height"), 28, 72, out["row_height"]))
    out["gap"] = int(clamp(raw.get("gap"), 0, 24, out["gap"]))
    out["corner_radius"] = int(clamp(raw.get("corner_radius"), 0, 40, out["corner_radius"]))

    items = []
    for item in raw.get("items", [])[:20]:
        if not isinstance(item, dict):
            continue
        typ = str(item.get("type", "toggle")).lower()
        if typ not in ALLOWED_TYPES:
            typ = "toggle"
        label = str(item.get("label", "Item"))[:64]
        action = str(item.get("action", "NONE"))
        if action not in ALLOWED_ACTIONS:
            action = "NONE"
        items.append({"type": typ, "label": label, "action": action})
    out["items"] = items or list(DEFAULT_DESIGN["items"])
    return out


def load_design():
    with LOCK:
        if DATA_FILE.exists():
            try:
                data = json.loads(DATA_FILE.read_text("utf-8"))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        return dict(DEFAULT_DESIGN)


def save_design(data):
    with LOCK:
        tmp = DATA_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
        tmp.replace(DATA_FILE)


@app.get("/")
def editor():
    return Response(EDITOR_HTML, mimetype="text/html")


@app.route("/api/design", methods=["GET", "POST"])
def api_design():
    if request.method == "GET":
        return jsonify(load_design())
    old = load_design()
    incoming = request.get_json(silent=True) or {}
    design = clean_design(incoming, old.get("version", 0))
    save_design(design)
    return jsonify({"ok": True, "design": design})


@app.route("/api/lua-design", methods=["GET", "POST"])
def lua_design():
    d = load_design()
    lines = [
        "CHETO_UI_V1",
        f"version={int(d.get('version', 1))}",
        "title=" + quote(str(d.get("title", "IDc Studio")), safe=""),
        f"width={int(d.get('width', 470))}",
        f"height={int(d.get('height', 420))}",
        f"offset_x={int(d.get('offset_x', 0))}",
        f"offset_y={int(d.get('offset_y', 0))}",
        f"background={d.get('background', '#111318')}",
        f"background_opacity={float(d.get('background_opacity', .94)):.2f}",
        f"accent={d.get('accent', '#ff3b30')}",
        f"text_color={d.get('text_color', '#ffffff')}",
        f"row_color={d.get('row_color', '#1d2028')}",
        f"on_color={d.get('on_color', '#22c55e')}",
        f"off_color={d.get('off_color', '#ef4444')}",
        f"title_size={int(d.get('title_size', 24))}",
        f"font_size={int(d.get('font_size', 16))}",
        f"row_height={int(d.get('row_height', 44))}",
        f"gap={int(d.get('gap', 8))}",
        f"corner_radius={int(d.get('corner_radius', 20))}",
    ]
    for item in d.get("items", []):
        label = quote(str(item.get("label", "Item")), safe="")
        lines.append("item=%s|%s|%s" % (
            str(item.get("type", "toggle")), label, str(item.get("action", "NONE"))
        ))
    return Response("\n".join(lines) + "\n", mimetype="text/plain")


@app.get("/health")
def health():
    return jsonify(ok=True, version=load_design().get("version", 1))


EDITOR_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IDc Remote GUI Builder</title>
<style>
:root{--bg:#07080c;--card:#11131a;--line:#242734;--txt:#f7f7fb;--muted:#9096a8;--accent:#ff3b30}
*{box-sizing:border-box} body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto;background:radial-gradient(circle at 15% 10%,#271014 0,transparent 28%),radial-gradient(circle at 90% 80%,#101a35 0,transparent 30%),var(--bg);color:var(--txt);min-height:100vh;overflow-x:hidden}
body:before{content:"";position:fixed;inset:-40%;background:conic-gradient(from 0deg,transparent,#ff3b3020,transparent,#4777ff20,transparent);animation:spin 18s linear infinite;pointer-events:none}@keyframes spin{to{transform:rotate(360deg)}}
.shell{position:relative;display:grid;grid-template-columns:390px minmax(420px,1fr);gap:20px;padding:22px;min-height:100vh}.panel{background:#0f1118e8;border:1px solid #262a38;border-radius:24px;box-shadow:0 24px 80px #0008;backdrop-filter:blur(18px);overflow:hidden}.head{padding:22px 22px 14px;border-bottom:1px solid var(--line)}.brand{font-size:21px;font-weight:800;letter-spacing:.2px}.sub{color:var(--muted);font-size:12px;margin-top:5px}.controls{padding:18px;max-height:calc(100vh - 110px);overflow:auto}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}.field{margin-bottom:11px}.field label{display:block;color:#abb1c2;font-size:11px;font-weight:700;margin:0 0 6px;text-transform:uppercase;letter-spacing:.7px}.field input,.field select{width:100%;border:1px solid #2b2f3f;background:#0a0c12;color:white;border-radius:12px;padding:11px 12px;outline:none;transition:.2s}.field input:focus,.field select:focus{border-color:#ff4b42;box-shadow:0 0 0 3px #ff3b3018}.colorrow input{height:42px;padding:4px}.section-title{display:flex;align-items:center;justify-content:space-between;margin:18px 0 10px;font-weight:800}.tiny{font-size:11px;color:var(--muted)}
.item{display:grid;grid-template-columns:32px 1.35fr .85fr 1fr 34px;gap:7px;align-items:center;background:#151822;border:1px solid #292d3b;border-radius:14px;padding:8px;margin-bottom:8px;animation:pop .25s ease}.item input,.item select{min-width:0;width:100%;border:1px solid #303548;background:#0d0f16;color:#fff;border-radius:9px;padding:8px}.drag{cursor:grab;color:#747b91;text-align:center;font-size:18px}.del{border:0;background:#291115;color:#ff6b64;border-radius:9px;height:34px;cursor:pointer}.buttons{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:12px}.btn{border:0;border-radius:13px;padding:12px 14px;font-weight:800;cursor:pointer;transition:.18s}.btn:hover{transform:translateY(-1px)}.primary{background:linear-gradient(135deg,#ff4b42,#d81f29);color:white;box-shadow:0 10px 26px #ff3b3030}.secondary{background:#1a1d28;color:#d8dbe6;border:1px solid #303548}.publish{width:100%;margin-top:14px;padding:15px;border-radius:15px;background:linear-gradient(90deg,#ff443a,#ff713f);color:#fff;border:0;font-weight:900;letter-spacing:.6px;cursor:pointer;box-shadow:0 14px 35px #ff3b3030}.status{height:20px;color:#9ba2b6;font-size:12px;text-align:center;margin-top:9px}
.stage{display:flex;align-items:center;justify-content:center;position:relative;min-height:calc(100vh - 44px);overflow:hidden}.stage:before{content:"GAME PREVIEW";position:absolute;top:20px;left:22px;color:#565d72;font-size:11px;font-weight:800;letter-spacing:1.6px}.fakegame{position:absolute;inset:0;background:linear-gradient(135deg,#111b16,#15131a);opacity:.55}.fakegame:after{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,transparent 0 79px,#ffffff05 80px),repeating-linear-gradient(0deg,transparent 0 79px,#ffffff05 80px)}
.preview{position:relative;z-index:2;display:flex;flex-direction:column;box-shadow:0 34px 90px #000b;border:1px solid #ffffff12;overflow:hidden;animation:float 4s ease-in-out infinite}@keyframes float{50%{transform:translateY(-4px)}}.preview .accent{height:3px;flex:0 0 3px}.pvhead{padding:18px 20px 13px;font-weight:900}.pvitems{padding:4px 16px 18px;overflow:hidden}.pvrow{display:flex;align-items:center;justify-content:space-between;padding:0 12px;border:1px solid #ffffff0d}.pvtoggle{min-width:54px;text-align:center;padding:7px 9px;font-size:11px;font-weight:900;border-radius:9px}.pvbutton{width:100%;text-align:center;font-weight:900;border:0}.pvtext{background:transparent!important;border-color:transparent!important}.hint{position:absolute;bottom:18px;color:#6c7388;font-size:12px;z-index:3}.flash{animation:flash .45s ease}@keyframes flash{0%{filter:brightness(1.9);transform:scale(1.02)}100%{filter:none;transform:none}}@keyframes pop{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
@media(max-width:920px){.shell{grid-template-columns:1fr;padding:12px}.controls{max-height:none}.stage{min-height:620px}}
</style>
</head>
<body><div class="shell">
<section class="panel"><div class="head"><div class="brand">IDc Remote GUI Builder</div><div class="sub">Design here → Publish → reopen/refresh the Lua menu.</div></div><div class="controls">
<div class="field"><label>Menu title</label><input id="title"></div>
<div class="grid2"><div class="field"><label>Width</label><input id="width" type="number"></div><div class="field"><label>Height</label><input id="height" type="number"></div></div>
<div class="grid2"><div class="field"><label>Offset X</label><input id="offset_x" type="number"></div><div class="field"><label>Offset Y</label><input id="offset_y" type="number"></div></div>
<div class="grid2 colorrow"><div class="field"><label>Background</label><input id="background" type="color"></div><div class="field"><label>Accent</label><input id="accent" type="color"></div></div>
<div class="grid2 colorrow"><div class="field"><label>Text</label><input id="text_color" type="color"></div><div class="field"><label>Row</label><input id="row_color" type="color"></div></div>
<div class="grid2 colorrow"><div class="field"><label>ON color</label><input id="on_color" type="color"></div><div class="field"><label>OFF color</label><input id="off_color" type="color"></div></div>
<div class="grid2"><div class="field"><label>Opacity</label><input id="background_opacity" type="number" min="0.15" max="1" step="0.01"></div><div class="field"><label>Corner radius</label><input id="corner_radius" type="number"></div></div>
<div class="grid2"><div class="field"><label>Title size</label><input id="title_size" type="number"></div><div class="field"><label>Font size</label><input id="font_size" type="number"></div></div>
<div class="grid2"><div class="field"><label>Row height</label><input id="row_height" type="number"></div><div class="field"><label>Gap</label><input id="gap" type="number"></div></div>
<div class="section-title"><span>Elements</span><span class="tiny">drag to reorder</span></div><div id="items"></div>
<div class="buttons"><button class="btn secondary" onclick="addItem('toggle')">+ Toggle</button><button class="btn secondary" onclick="addItem('button')">+ Button</button></div>
<div class="buttons"><button class="btn secondary" onclick="addItem('text')">+ Text</button><button class="btn secondary" onclick="loadDesign()">↻ Reload</button></div>
<button class="publish" id="publish">PUBLISH TO LUA</button><div class="status" id="status"></div>
</div></section>
<section class="panel stage"><div class="fakegame"></div><div class="preview" id="preview"><div class="accent" id="pvAccent"></div><div class="pvhead" id="pvTitle"></div><div class="pvitems" id="pvItems"></div></div><div class="hint">Preview approximates the native Lua/UMG renderer.</div></section>
</div>
<script>
const ACTIONS=['NONE','TEST','REFRESH','ESP','ESPLine','EnemyESPWeapon','EnemyESPWeaponOnly','IAwarenessText','IAwarenessArrows','Radar','VehicleESP','ItemESP','GrenadeESP','AirdropESP','TombBoxESP'];
let design={}; let dragIndex=null;
const ids=['title','width','height','offset_x','offset_y','background','background_opacity','accent','text_color','row_color','on_color','off_color','title_size','font_size','row_height','gap','corner_radius'];
function esc(s){return String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function readFields(){for(const id of ids){const el=document.getElementById(id); design[id]=(el.type==='number')?Number(el.value):el.value}}
function renderItems(){const box=document.getElementById('items');box.innerHTML='';(design.items||[]).forEach((it,i)=>{const d=document.createElement('div');d.className='item';d.draggable=true;d.innerHTML=`<div class="drag">⋮⋮</div><input value="${esc(it.label)}" data-k="label"><select data-k="type">${['toggle','button','text'].map(x=>`<option ${it.type===x?'selected':''}>${x}</option>`).join('')}</select><select data-k="action">${ACTIONS.map(x=>`<option ${it.action===x?'selected':''}>${x}</option>`).join('')}</select><button class="del">×</button>`;d.querySelectorAll('input,select').forEach(e=>e.oninput=()=>{it[e.dataset.k]=e.value;updatePreview()});d.querySelector('.del').onclick=()=>{design.items.splice(i,1);renderItems();updatePreview()};d.ondragstart=()=>dragIndex=i;d.ondragover=e=>e.preventDefault();d.ondrop=e=>{e.preventDefault();if(dragIndex===null||dragIndex===i)return;const [m]=design.items.splice(dragIndex,1);design.items.splice(i,0,m);dragIndex=null;renderItems();updatePreview()};box.appendChild(d)})}
function addItem(type){design.items=design.items||[];design.items.push({type,label:type==='text'?'Text label':type==='button'?'Button':'New toggle',action:type==='text'?'NONE':'TEST'});renderItems();updatePreview()}
function updatePreview(){readFields();const p=document.getElementById('preview');p.style.width=(design.width||470)+'px';p.style.height=(design.height||420)+'px';p.style.background=hexAlpha(design.background||'#111318',design.background_opacity??.94);p.style.borderRadius=(design.corner_radius||0)+'px';p.style.color=design.text_color||'#fff';p.style.transform=`translate(${design.offset_x||0}px,${design.offset_y||0}px)`;document.getElementById('pvAccent').style.background=design.accent;const t=document.getElementById('pvTitle');t.textContent=design.title||'';t.style.fontSize=(design.title_size||24)+'px';const c=document.getElementById('pvItems');c.innerHTML='';for(const it of design.items||[]){const r=document.createElement('div');r.className='pvrow '+(it.type==='text'?'pvtext':'');r.style.height=(design.row_height||44)+'px';r.style.marginBottom=(design.gap||8)+'px';r.style.background=it.type==='text'?'transparent':(design.row_color||'#1d2028');r.style.borderRadius=Math.min(design.corner_radius||0,14)+'px';r.style.fontSize=(design.font_size||16)+'px';if(it.type==='toggle'){r.innerHTML=`<span>${esc(it.label)}</span><span class="pvtoggle">ON</span>`;r.querySelector('.pvtoggle').style.background=design.on_color||'#22c55e'}else if(it.type==='button'){r.classList.add('pvbutton');r.style.background=design.accent||'#ff3b30';r.innerHTML=`<span style="width:100%">${esc(it.label)}</span>`}else{r.innerHTML=`<span>${esc(it.label)}</span>`}c.appendChild(r)}}
function hexAlpha(hex,a){hex=(hex||'#000000').replace('#','');const n=parseInt(hex,16);return `rgba(${n>>16},${(n>>8)&255},${n&255},${a})`}
async function loadDesign(){const r=await fetch('/api/design');design=await r.json();for(const id of ids){const e=document.getElementById(id);e.value=design[id]??'';e.oninput=updatePreview}renderItems();updatePreview();setStatus('Loaded design v'+(design.version||1))}
async function publish(){readFields();const b=document.getElementById('publish');b.disabled=true;b.textContent='PUBLISHING...';try{const r=await fetch('/api/design',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(design)});const j=await r.json();design=j.design||design;setStatus('Published ✓  version '+design.version);document.getElementById('preview').classList.remove('flash');void document.getElementById('preview').offsetWidth;document.getElementById('preview').classList.add('flash')}catch(e){setStatus('Publish failed: '+e)}finally{b.disabled=false;b.textContent='PUBLISH TO LUA'}}
function setStatus(s){document.getElementById('status').textContent=s}document.getElementById('publish').onclick=publish;loadDesign();
</script></body></html>'''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
