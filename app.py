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
*{box-sizing:border-box}html,body{margin:0;min-height:100%;font-family:"Arial Narrow",Arial,sans-serif;background:#20252b;color:#eee}body{display:flex;align-items:center;justify-content:center;padding:14px;background:linear-gradient(135deg,#38434b,#20252b 55%,#4b4037)}
.menu{width:min(780px,96vw);background:rgba(8,8,8,.72);border:1px solid rgba(255,255,255,.18);box-shadow:0 4px 18px #0008;overflow:hidden}.topline{height:7px;background:#090909;position:relative}.topline:after{content:"";position:absolute;right:3.8%;top:0;width:4px;height:100%;background:#f22}.title{height:35px;padding:8px 9px;border-bottom:1px solid #151515;font-size:14px;color:#d8d8d8;text-shadow:1px 1px #000}.tabs{display:flex;border-bottom:1px solid #050505;background:rgba(0,0,0,.22)}.tab{flex:1;background:transparent;color:#ddd;border:0;border-right:1px solid #181818;padding:9px 5px;font-weight:700;font-size:13px}.tab.active{background:rgba(255,255,255,.07);color:#fff}.page{display:none;max-height:67vh;overflow-y:auto;scrollbar-width:thin;scrollbar-color:#777 #171717}.page.active{display:block}.row{min-height:45px;display:flex;align-items:center;justify-content:space-between;padding:0 9px;border-bottom:1px solid #171717;background:rgba(20,20,20,.12);font-weight:700;font-size:15px;text-shadow:1px 1px 1px #000}.row:hover{background:rgba(255,255,255,.035)}.label{white-space:nowrap}.toggle{width:9px;height:35px;padding:0;border:0;background:#e52424;box-shadow:0 0 2px #000;overflow:hidden;text-indent:-999px}.toggle.on{background:#15e43a}.sliderwrap{display:flex;align-items:center;gap:10px;min-width:50%}.range{width:100%;accent-color:#ffea00;height:4px}.value{min-width:42px;text-align:right;font-size:14px}.action{cursor:pointer}.action:active{background:rgba(255,255,255,.09)}.footerrow{min-height:43px;display:flex;align-items:center;padding:0 9px;border-bottom:1px solid #171717;font-size:15px;font-weight:700;cursor:pointer}.foot{height:8px;background:#111}
@media(max-width:600px){.menu{width:98vw}.row{font-size:13px;min-height:42px}.sliderwrap{min-width:45%}.title{font-size:13px}}
</style>
</head>
<body>
<div class="menu">
 <div class="topline"></div>
 <div class="title">Radar & ESP Settings</div>
 <div class="tabs"><button class="tab active" data-page="visual">ESP</button><button class="tab" data-page="aim">Aimbot</button><button class="tab" data-page="other">Other</button></div>
 <section id="visual" class="page active">
 {% for key,label in [
 ('enemy_visuals','Enemy ESP'),('warning_line','Warning Line'),('names','Name'),('distance','Distance'),('health','Health'),('box3d','3D Box'),('skeleton','Skeleton ESP'),('weapon_text','Enemy ESP Weapon'),('item_overlay','Item ESP'),('vehicle_overlay','Vehicle ESP'),('grenade_warning','Grenade ESP'),('airdrop_overlay','Radar AirDrop'),('tomb_overlay','Radar TombBox'),('radar','Radar Vehicles'),('awareness_text','iAwareness Text') ] %}
 <div class="row"><span class="label">{{label}}</span><button class="toggle {{'on' if states.get(key) else ''}}" data-key="{{key}}">{{'ON' if states.get(key) else 'OFF'}}</button></div>
 {% endfor %}
 <div class="row"><span class="label">Size Font Radar</span><div class="sliderwrap"><input class="range" type="range" min="8" max="30" step=".1" value="15.1" oninput="fontv.textContent=Number(this.value).toFixed(1)"><span id="fontv" class="value">15.1</span></div></div>
 <div class="row"><span class="label">Size Bone Radar</span><div class="sliderwrap"><input class="range" type="range" min="1" max="5" step=".1" value="2" oninput="bonev.textContent=Number(this.value).toFixed(1)"><span id="bonev" class="value">2.0</span></div></div>
 <div class="footerrow action" onclick="document.querySelector('[data-page=other]').click()">Back</div><div class="footerrow action" onclick="document.querySelector('.menu').style.display='none'">Close Menu</div>
 </section>
 <section id="aim" class="page">
 <div class="row"><span>Turn Rate</span><div class="sliderwrap"><input class="range" type="range" min="100" max="720" value="100" oninput="turnv.textContent=this.value"><span id="turnv" class="value">100</span></div></div>
 <div class="row"><span>Field Of View</span><div class="sliderwrap"><input class="range" type="range" min="10" max="500" value="10" oninput="fovv.textContent=this.value"><span id="fovv" class="value">10</span></div></div>
 <div class="row"><span>Aimbot Circle Radius</span><div class="sliderwrap"><input class="range" type="range" min="50" max="875" value="50" oninput="radv.textContent=this.value"><span id="radv" class="value">50</span></div></div>
 <div class="footerrow action" onclick="document.querySelector('[data-page=visual]').click()">Back</div><div class="footerrow action" onclick="document.querySelector('.menu').style.display='none'">Close Menu</div>
 </section>
 <section id="other" class="page"><div class="row"><span>Configuration</span><span class="value">WEB</span></div><div class="footerrow action" onclick="document.querySelector('[data-page=visual]').click()">Back</div><div class="footerrow action" onclick="document.querySelector('.menu').style.display='none'">Close Menu</div></section>
 <div class="foot"></div>
</div>
<script>
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tab,.page').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.getElementById(b.dataset.page).classList.add('active')});
document.querySelectorAll('.toggle').forEach(b=>b.onclick=async()=>{const r=await fetch('/api/toggle',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:b.dataset.key})});const j=await r.json();b.classList.toggle('on',j.value);b.textContent=j.value?'ON':'OFF'});
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
