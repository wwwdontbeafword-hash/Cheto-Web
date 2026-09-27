from flask import Flask, jsonify, render_template_string
from datetime import datetime, timezone

app = Flask(__name__)
state = {"test": False, "seq": 0, "updated_at": None}

PAGE = """<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CHETo Bridge Test</title><style>
*{box-sizing:border-box}body{margin:0;background:#080b12;color:white;font-family:Arial;min-height:100vh;display:grid;place-items:center}
.card{width:min(92vw,430px);padding:28px;border:1px solid #293244;border-radius:22px;background:#101622;text-align:center}
.muted{color:#9ba7ba}.status{margin:22px 0;padding:16px;border-radius:14px;background:#090d14;font-weight:bold}
.ok{color:#6dff9a}.off{color:#ff7474}button{width:100%;padding:15px;border:0;border-radius:13px;font-size:17px;font-weight:bold}
.small{font-size:12px;color:#778398;margin-top:15px}</style></head><body><div class="card">
<h1>CHETo Bridge Test</h1><div class="muted">اختبار واجهة الويب والسيرفر</div>
<div id="status" class="status off">TEST = OFF</div><button onclick="toggleTest()">TEST LUA</button>
<div id="seq" class="small">Sequence: 0</div></div><script>
async function refresh(){let r=await fetch('/api/state',{cache:'no-store'}),s=await r.json(),e=document.getElementById('status');
e.textContent='TEST = '+(s.test?'ON':'OFF');e.className='status '+(s.test?'ok':'off');document.getElementById('seq').textContent='Sequence: '+s.seq}
async function toggleTest(){await fetch('/api/test',{method:'POST'});await refresh()}refresh();setInterval(refresh,1500);
</script></body></html>"""

@app.get("/")
def index(): return render_template_string(PAGE)

@app.post("/api/test")
def test():
    state["test"] = not state["test"]
    state["seq"] += 1
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    return jsonify(state)

@app.get("/api/state")
def get_state(): return jsonify(state)

@app.get("/health")
def health(): return jsonify(ok=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
