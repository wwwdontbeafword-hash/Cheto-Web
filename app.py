from flask import Flask, request, session, redirect, render_template_string
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cheto-web-test-change-me")

PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Cheto Web Test</title>
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;width:100%;height:100%;overflow:hidden;font-family:Arial,Helvetica,sans-serif;background:#050507;color:#fff}
body{display:grid;place-items:center}
.bg{position:fixed;inset:0;background:
radial-gradient(circle at 50% 42%,rgba(255,89,178,.12),transparent 31%),
radial-gradient(circle at 15% 15%,rgba(131,83,255,.09),transparent 25%),#050507}
.bg:before{content:"";position:absolute;inset:-25%;background:conic-gradient(from 180deg,transparent,rgba(255,104,190,.07),transparent 28%);animation:spin 12s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.card{position:relative;width:min(610px,86vw);border-radius:35px;padding:46px 46px 34px;background:linear-gradient(145deg,rgba(216,166,198,.91),rgba(185,139,176,.88));box-shadow:0 30px 90px #000b,0 0 55px rgba(255,92,180,.12);border:1px solid rgba(255,255,255,.12);backdrop-filter:blur(22px);animation:enter .7s cubic-bezier(.16,.86,.24,1)}
@keyframes enter{from{opacity:0;transform:translateY(24px) scale(.95);filter:blur(8px)}}
.card:after{content:"";position:absolute;inset:0;border-radius:35px;pointer-events:none;background:linear-gradient(110deg,transparent 25%,rgba(255,255,255,.12) 48%,transparent 70%);transform:translateX(-100%);animation:shine 4s ease-in-out infinite}
@keyframes shine{0%,58%{transform:translateX(-120%)}80%,100%{transform:translateX(120%)}}
h1{margin:0 0 48px;text-align:center;font-size:38px;font-weight:500;color:#4f3c4d;text-shadow:0 1px 1px rgba(255,255,255,.25)}
.inputWrap{position:relative;margin-bottom:32px}
input{width:100%;height:78px;border:0;outline:none;border-radius:19px;padding:0 23px;background:rgba(255,244,252,.93);color:#4d3b4b;font-size:25px;box-shadow:inset 0 0 0 1px rgba(79,45,70,.10),0 8px 25px rgba(88,35,70,.08);transition:.25s}
input:focus{transform:translateY(-2px);box-shadow:inset 0 0 0 2px rgba(117,77,108,.23),0 12px 32px rgba(88,35,70,.14)}
input::placeholder{color:#c5a8bd}
button{display:block;margin:auto;width:180px;height:72px;border:0;border-radius:20px;background:transparent;color:#7356cd;font-size:36px;font-weight:500;cursor:pointer;transition:.2s;text-shadow:0 0 15px rgba(104,69,210,.22)}
button:hover{transform:scale(1.06);color:#6644d7}button:active{transform:scale(.96)}
.sep{height:1px;background:rgba(61,43,58,.24);margin:0 -46px 12px}
.err{text-align:center;color:#6d2436;font-weight:800;margin:-22px 0 16px;animation:shake .3s ease}@keyframes shake{25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}
.testBox{position:relative;width:min(520px,84vw);height:220px;border-radius:30px;display:grid;place-items:center;background:linear-gradient(145deg,#5f1017,#26070a);border:2px solid #ff3144;box-shadow:0 0 30px #ff304944,0 28px 80px #000b;animation:testIn .65s cubic-bezier(.16,.9,.2,1)}
@keyframes testIn{from{opacity:0;transform:scale(.72) rotate(-2deg)}70%{transform:scale(1.03)}to{transform:scale(1)}}
.testBox:before{content:"";position:absolute;inset:-2px;border-radius:30px;background:linear-gradient(90deg,transparent,#ff5968,transparent);filter:blur(10px);opacity:.45;animation:pulse 1.8s ease-in-out infinite}@keyframes pulse{50%{opacity:.9}}
.testBox strong{position:relative;font-size:52px;letter-spacing:4px;color:#ff5261;text-shadow:0 0 18px #ff2f44}
.small{position:absolute;bottom:18px;font-size:11px;color:#ff9ca4;letter-spacing:2px}
@media(max-width:650px){.card{padding:34px 26px 24px;border-radius:28px}.sep{margin-left:-26px;margin-right:-26px}h1{font-size:29px;margin-bottom:34px}input{height:64px;font-size:20px}button{height:60px;font-size:31px}}
</style>
</head>
<body>
<div class="bg"></div>
{% if logged_in %}
  <div class="testBox"><strong>TEST ON</strong><div class="small">WEB UI ACTIVE</div></div>
{% else %}
  <form class="card" method="post" autocomplete="off">
    <h1>Key required</h1>
    {% if error %}<div class="err">{{ error }}</div>{% endif %}
    <div class="inputWrap"><input name="key" placeholder="Activation Key" autofocus required></div>
    <div class="sep"></div>
    <button type="submit">OK</button>
  </form>
{% endif %}
</body>
</html>'''

@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        key = (request.form.get('key') or '').strip()
        # Test build: any non-empty key is accepted so we only test the embedded website.
        if key:
            session['logged_in'] = True
            session['key'] = key
            return redirect('/')
        error = 'Invalid Key'
    return render_template_string(PAGE, logged_in=bool(session.get('logged_in')), error=error)

@app.route('/reset')
def reset():
    session.clear()
    return redirect('/')

@app.route('/health')
def health():
    return {'ok': True}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '10000')))
