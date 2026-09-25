from flask import Flask, render_template_string, request, jsonify, session
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret")

# Web-only control panel.
# States are kept in the Flask session. No game/runtime execution is performed.
DEFAULTS = {
    "enemy_visuals": False,
    "warning_line": False,
    "names": False,
    "distance": False,
    "health": False,
    "box3d": False,
    "skeleton": False,
    "weapon_text": False,
    "item_overlay": False,
    "vehicle_overlay": False,
    "grenade_warning": False,
    "airdrop_overlay": False,
    "tomb_overlay": False,
    "radar": False,
    "awareness_text": False,
}

HTML = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>CHETO Control</title>
<style>
:root{--bg:#080b12;--panel:#101622;--panel2:#151d2b;--line:#273247;--text:#eef3ff;--muted:#8f9bb3;--on:#25d366;--off:#e5484d;--accent:#7c5cff}
*{box-sizing:border-box} body{margin:0;background:radial-gradient(circle at top,#171d2d,#080b12 55%);font-family:Arial,sans-serif;color:var(--text);min-height:100vh;display:grid;place-items:center;padding:20px}
.shell{width:min(430px,100%);background:rgba(16,22,34,.96);border:1px solid var(--line);border-radius:24px;overflow:hidden;box-shadow:0 25px 80px #0008}
.head{padding:20px 20px 14px;border-bottom:1px solid var(--line)} .brand{font-weight:900;letter-spacing:2px}.sub{font-size:12px;color:var(--muted);margin-top:5px}
.tabs{display:flex;gap:8px;padding:12px;border-bottom:1px solid var(--line);overflow:auto}.tab{border:1px solid var(--line);background:#0b1019;color:var(--muted);padding:10px 14px;border-radius:12px;white-space:nowrap}.tab.active{background:var(--accent);color:white;border-color:transparent}
.page{display:none;padding:12px;max-height:68vh;overflow:auto}.page.active{display:block}
.row{display:flex;align-items:center;justify-content:space-between;gap:15px;padding:13px 12px;background:var(--panel2);border:1px solid #202b3d;border-radius:14px;margin-bottom:8px}.label{font-size:14px}.hint{font-size:11px;color:var(--muted);margin-top:3px}
.toggle{min-width:58px;border:0;border-radius:10px;padding:8px 10px;color:white;font-weight:800;background:var(--off)}.toggle.on{background:var(--on)}
.range{width:145px}.foot{padding:12px 16px;border-top:1px solid var(--line);font-size:11px;color:var(--muted);text-align:center}
</style>
</head>
<body>
<div class="shell">
  <div class="head"><div class="brand">CHETO // CONTROL</div><div class="sub">Web control interface</div></div>
  <div class="tabs">
    <button class="tab active" data-page="visual">Visual</button>
    <button class="tab" data-page="aim">Aim Settings</button>
    <button class="tab" data-page="other">Other</button>
  </div>

  <section id="visual" class="page active">
    {% for key,label in [
      ('enemy_visuals','Enemy Visuals'),('warning_line','Warning Line'),('names','Name'),
      ('distance','Distance'),('health','Health'),('box3d','3D Box'),('skeleton','Skeleton'),
      ('weapon_text','Weapon Text'),('item_overlay','Item Overlay'),('vehicle_overlay','Vehicle Overlay'),
      ('grenade_warning','Grenade Warning'),('airdrop_overlay','Airdrop Overlay'),
      ('tomb_overlay','Tomb Overlay'),('radar','Radar'),('awareness_text','Awareness Text')
    ] %}
    <div class="row"><div><div class="label">{{label}}</div><div class="hint">Web state only</div></div>
      <button class="toggle {{'on' if states.get(key) else ''}}" data-key="{{key}}">{{'ON' if states.get(key) else 'OFF'}}</button>
    </div>
    {% endfor %}
  </section>

  <section id="aim" class="page">
    <div class="row"><div><div class="label">Turn Rate</div><div class="hint" id="turnv">100</div></div><input class="range" type="range" min="100" max="720" value="100" oninput="turnv.textContent=this.value"></div>
    <div class="row"><div><div class="label">Field Of View</div><div class="hint" id="fovv">10</div></div><input class="range" type="range" min="10" max="500" value="10" oninput="fovv.textContent=this.value"></div>
    <div class="row"><div><div class="label">Circle Radius</div><div class="hint" id="rad">50</div></div><input class="range" type="range" min="50" max="875" value="50" oninput="rad.textContent=this.value"></div>
  </section>

  <section id="other" class="page">
    <div class="row"><div><div class="label">Configuration</div><div class="hint">This page can hold account/server settings.</div></div></div>
  </section>

  <div class="foot">Interface states are stored on the website only.</div>
</div>
<script>
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{
 document.querySelectorAll('.tab,.page').forEach(x=>x.classList.remove('active'));
 b.classList.add('active'); document.getElementById(b.dataset.page).classList.add('active');
});
document.querySelectorAll('.toggle').forEach(b=>b.onclick=async()=>{
 const r=await fetch('/api/toggle',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:b.dataset.key})});
 const j=await r.json(); b.classList.toggle('on',j.value); b.textContent=j.value?'ON':'OFF';
});
</script>
</body></html>
"""

@app.route("/")
def index():
    states = dict(DEFAULTS)
    states.update(session.get("states", {}))
    return render_template_string(HTML, states=states)

@app.post("/api/toggle")
def toggle():
    key = (request.get_json(silent=True) or {}).get("key")
    if key not in DEFAULTS:
        return jsonify(ok=False, error="unknown control"), 400
    states = dict(DEFAULTS)
    states.update(session.get("states", {}))
    states[key] = not bool(states[key])
    session["states"] = states
    return jsonify(ok=True, key=key, value=states[key])

@app.get("/api/state")
def state():
    states = dict(DEFAULTS)
    states.update(session.get("states", {}))
    return jsonify(states)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
