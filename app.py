from flask import Flask, jsonify, request, Response
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request as URLRequest, urlopen
from urllib.error import HTTPError, URLError
import json
import os
import re
import threading

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "design_store.json"
LOCK = threading.Lock()
KEY_MANAGER_VERIFY_URL = os.getenv("KEY_MANAGER_VERIFY_URL", "https://key-manager-o3df.onrender.com/verify")

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

DEFAULT_LOGIN = {
    "version": 1,
    "title": "Press OK",
    "hint": "Activation Key",
    "ok_text": "OK",
    "width": 610,
    "height": 290,
    "offset_x": 0,
    "offset_y": 0,
    "backdrop": "#000000",
    "backdrop_opacity": 0.94,
    "panel": "#15171c",
    "panel_opacity": 0.98,
    "input": "#292c33",
    "input_opacity": 0.98,
    "text_color": "#ffffff",
    "hint_color": "#b4b7bf",
    "ok_color": "#1797ff",
    "separator_color": "#3d4149",
    "title_size": 28,
    "input_size": 19,
    "ok_size": 31,
    "corner_radius": 22,
    "input_radius": 17,
}

DEFAULT_MENU = {
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


def clamp(v, lo, hi, default):
    try:
        v = float(v)
    except Exception:
        return default
    return max(lo, min(hi, v))


def clean_hex(v, default):
    v = str(v or "").strip()
    return v.lower() if HEX_RE.match(v) else default


def clean_login(raw, previous_version=0):
    raw = raw if isinstance(raw, dict) else {}
    out = dict(DEFAULT_LOGIN)
    out["version"] = max(int(previous_version) + 1, 1)
    out["title"] = str(raw.get("title", out["title"]))[:48]
    out["hint"] = str(raw.get("hint", out["hint"]))[:48]
    out["ok_text"] = str(raw.get("ok_text", out["ok_text"]))[:24]
    out["width"] = int(clamp(raw.get("width"), 360, 820, out["width"]))
    out["height"] = int(clamp(raw.get("height"), 220, 520, out["height"]))
    out["offset_x"] = int(clamp(raw.get("offset_x"), -500, 500, 0))
    out["offset_y"] = int(clamp(raw.get("offset_y"), -500, 500, 0))
    for key in ("backdrop", "panel", "input", "text_color", "hint_color", "ok_color", "separator_color"):
        out[key] = clean_hex(raw.get(key), out[key])
    out["backdrop_opacity"] = round(clamp(raw.get("backdrop_opacity"), 0.0, 1.0, out["backdrop_opacity"]), 2)
    out["panel_opacity"] = round(clamp(raw.get("panel_opacity"), 0.15, 1.0, out["panel_opacity"]), 2)
    out["input_opacity"] = round(clamp(raw.get("input_opacity"), 0.15, 1.0, out["input_opacity"]), 2)
    out["title_size"] = int(clamp(raw.get("title_size"), 12, 48, out["title_size"]))
    out["input_size"] = int(clamp(raw.get("input_size"), 10, 34, out["input_size"]))
    out["ok_size"] = int(clamp(raw.get("ok_size"), 12, 48, out["ok_size"]))
    out["corner_radius"] = int(clamp(raw.get("corner_radius"), 0, 42, out["corner_radius"]))
    out["input_radius"] = int(clamp(raw.get("input_radius"), 0, 36, out["input_radius"]))
    return out


def clean_menu(raw, previous_version=0):
    raw = raw if isinstance(raw, dict) else {}
    out = dict(DEFAULT_MENU)
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
    for item in raw.get("items", [])[:24]:
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
    out["items"] = items or list(DEFAULT_MENU["items"])
    return out


def load_store():
    with LOCK:
        if DATA_FILE.exists():
            try:
                data = json.loads(DATA_FILE.read_text("utf-8"))
                if isinstance(data, dict):
                    # migrate the old single-menu design.json structure if needed
                    if "login" in data or "menu" in data:
                        return {
                            "login": data.get("login") if isinstance(data.get("login"), dict) else dict(DEFAULT_LOGIN),
                            "menu": data.get("menu") if isinstance(data.get("menu"), dict) else dict(DEFAULT_MENU),
                        }
                    if "items" in data:
                        return {"login": dict(DEFAULT_LOGIN), "menu": data}
            except Exception:
                pass
        return {"login": dict(DEFAULT_LOGIN), "menu": dict(DEFAULT_MENU)}


def save_store(data):
    with LOCK:
        tmp = DATA_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
        tmp.replace(DATA_FILE)


@app.get("/")
def editor():
    return Response(EDITOR_HTML, mimetype="text/html")


@app.route("/api/login-design", methods=["GET", "POST"])
def api_login_design():
    store = load_store()
    if request.method == "GET":
        return jsonify(store["login"])
    incoming = request.get_json(silent=True) or {}
    store["login"] = clean_login(incoming, store["login"].get("version", 0))
    save_store(store)
    return jsonify({"ok": True, "design": store["login"]})


@app.route("/api/menu-design", methods=["GET", "POST"])
@app.route("/api/design", methods=["GET", "POST"])
def api_menu_design():
    store = load_store()
    if request.method == "GET":
        return jsonify(store["menu"])
    incoming = request.get_json(silent=True) or {}
    store["menu"] = clean_menu(incoming, store["menu"].get("version", 0))
    save_store(store)
    return jsonify({"ok": True, "design": store["menu"]})


@app.route("/api/lua-login-design", methods=["GET", "POST"])
def lua_login_design():
    d = load_store()["login"]
    keys = [
        "version", "title", "hint", "ok_text", "width", "height", "offset_x", "offset_y",
        "backdrop", "backdrop_opacity", "panel", "panel_opacity", "input", "input_opacity",
        "text_color", "hint_color", "ok_color", "separator_color", "title_size", "input_size",
        "ok_size", "corner_radius", "input_radius",
    ]
    lines = ["CHETO_LOGIN_V1"]
    for k in keys:
        v = d.get(k)
        if k in {"title", "hint", "ok_text"}:
            v = quote(str(v or ""), safe="")
        lines.append(f"{k}={v}")
    return Response("\n".join(lines) + "\n", mimetype="text/plain")


@app.route("/api/lua-design", methods=["GET", "POST"])
def lua_menu_design():
    d = load_store()["menu"]
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


@app.post("/api/verify-key")
def verify_key():
    payload = request.get_json(silent=True) or {}
    key = str(payload.get("key", "")).strip().upper()
    device_id = str(payload.get("device_id", "")).strip()
    if not key:
        return jsonify(valid=False, reason="invalid_key"), 400
    if not device_id:
        return jsonify(valid=False, reason="device_id_unavailable"), 400

    body = json.dumps({"key": key, "device_id": device_id}).encode("utf-8")
    req = URLRequest(
        KEY_MANAGER_VERIFY_URL,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "cheto-web/1.0"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status = int(getattr(resp, "status", 200) or 200)
    except HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        status = int(e.code or 502)
    except (URLError, TimeoutError, OSError) as e:
        return jsonify(valid=False, reason="key_manager_unreachable", detail=str(e)[:120]), 502

    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            data = {"valid": False, "reason": "bad_response"}
    except Exception:
        data = {"valid": False, "reason": "bad_response"}

    # Normalize reasons so the Lua UI can show stable messages even if the key manager changes wording.
    reason = str(data.get("reason", "")).strip().lower()
    if data.get("valid") is True:
        data["valid"] = True
    elif reason in {"device_limit", "device_mismatch"}:
        data.update(valid=False, reason="device_limit")
    elif reason in {"inactive", "expired", "stopped", "disabled"}:
        data.update(valid=False, reason="expired")
    elif reason in {"invalid", "invalid_key", "not_found"}:
        data.update(valid=False, reason="invalid_key")
    elif reason == "server_offline":
        data.update(valid=False, reason="server_offline")
    elif reason == "rate_limited":
        data.update(valid=False, reason="rate_limited")
    elif data.get("valid") is not True:
        data["valid"] = False
        data["reason"] = reason or "invalid_key"

    return jsonify(data), status


@app.get("/health")
def health():
    store = load_store()
    return jsonify(ok=True, login_version=store["login"].get("version", 1), menu_version=store["menu"].get("version", 1))


EDITOR_HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IDc Studio GUI Builder</title>
<style>
:root{--bg:#07080c;--card:#101219;--line:#272b38;--txt:#f7f7fb;--muted:#8d94a7;--red:#ff453a;--blue:#1897ff}*{box-sizing:border-box}body{margin:0;min-height:100vh;color:var(--txt);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto;background:radial-gradient(circle at 12% 5%,#291217 0,transparent 27%),radial-gradient(circle at 90% 90%,#101936 0,transparent 28%),var(--bg)}body:before{content:"";position:fixed;inset:-35%;background:conic-gradient(from 0deg,transparent,#ff453a15,transparent,#168cff12,transparent);animation:spin 20s linear infinite;pointer-events:none}@keyframes spin{to{transform:rotate(360deg)}}.top{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;padding:14px 22px;background:#090a10dd;border-bottom:1px solid #20232e;backdrop-filter:blur(16px)}.brand{font-weight:900;letter-spacing:.4px}.tabs{display:flex;gap:8px;padding:5px;background:#11131b;border:1px solid #262a38;border-radius:14px}.tab{border:0;color:#9fa6b9;background:transparent;padding:9px 14px;border-radius:10px;font-weight:800;cursor:pointer}.tab.active{background:#232735;color:white;box-shadow:0 5px 18px #0005}.wrap{display:grid;grid-template-columns:405px minmax(430px,1fr);gap:20px;padding:20px;min-height:calc(100vh - 70px)}.panel{background:#0f1118ec;border:1px solid #252936;border-radius:22px;box-shadow:0 26px 80px #0008;overflow:hidden}.head{padding:18px 19px 13px;border-bottom:1px solid #232633}.head h2{font-size:18px;margin:0}.head p{color:var(--muted);font-size:12px;margin:6px 0 0}.controls{padding:16px;max-height:calc(100vh - 145px);overflow:auto}.section{font-size:11px;color:#a6adbe;font-weight:900;letter-spacing:1px;text-transform:uppercase;margin:15px 0 9px}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:9px}.field{margin-bottom:10px}.field label{display:block;color:#aeb4c3;font-size:10px;font-weight:800;letter-spacing:.6px;text-transform:uppercase;margin-bottom:6px}.field input,.field select{width:100%;background:#090b11;border:1px solid #2c3040;border-radius:11px;color:white;padding:10px 11px;outline:none}.field input:focus,.field select:focus{border-color:#ff5048;box-shadow:0 0 0 3px #ff453a13}.color input{height:40px;padding:4px}.items .item{display:grid;grid-template-columns:28px 1.25fr .8fr 1fr 33px;gap:6px;align-items:center;background:#151822;border:1px solid #2a2e3d;border-radius:12px;padding:7px;margin-bottom:7px}.item input,.item select{width:100%;min-width:0;background:#0b0d13;border:1px solid #303547;color:#fff;border-radius:8px;padding:7px}.drag{color:#767d92;text-align:center;cursor:grab}.del{height:31px;border:0;border-radius:8px;background:#2b1116;color:#ff6c66;cursor:pointer}.actions{display:grid;grid-template-columns:1fr 1fr;gap:8px}.btn,.publish{border:0;border-radius:12px;padding:11px 13px;font-weight:900;cursor:pointer}.btn{background:#1a1d28;color:#d9dce7;border:1px solid #303548}.publish{width:100%;margin-top:12px;color:#fff;background:linear-gradient(90deg,#ff453a,#ff7646);box-shadow:0 12px 30px #ff453a26}.status{min-height:18px;margin-top:8px;text-align:center;color:#9ca3b5;font-size:11px}.stage{position:relative;display:flex;align-items:center;justify-content:center;min-height:calc(100vh - 110px);overflow:hidden}.game{position:absolute;inset:0;background:linear-gradient(135deg,#142017,#15131a)}.game:after{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,transparent 0 89px,#ffffff04 90px),repeating-linear-gradient(0deg,transparent 0 89px,#ffffff04 90px)}.stage-label{position:absolute;top:18px;left:20px;z-index:3;color:#5d6578;font-size:10px;font-weight:900;letter-spacing:1.5px}.preview{position:relative;z-index:4}.login-backdrop{position:absolute;inset:0;z-index:2}.login-card{position:relative;z-index:5;display:flex;flex-direction:column;justify-content:flex-start;overflow:hidden;box-shadow:0 30px 85px #000b}.login-title{text-align:center;font-weight:700}.login-input{display:flex;align-items:center;border:1px solid #ffffff0d}.login-sep{height:1px}.login-ok{text-align:center;font-weight:500}.menu-card{position:relative;z-index:5;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 30px 85px #000b}.menu-accent{height:3px}.menu-head{font-weight:900}.menu-items{overflow:hidden}.pvrow{display:flex;align-items:center;justify-content:space-between}.pill{min-width:54px;text-align:center;font-size:11px;font-weight:900}.pvbutton{justify-content:center;font-weight:900}.hidden{display:none!important}@media(max-width:900px){.wrap{grid-template-columns:1fr}.controls{max-height:none}.stage{min-height:560px}.top{align-items:flex-start;gap:12px;flex-direction:column}}
</style></head><body>
<div class="top"><div><div class="brand">IDc Studio · Remote GUI Builder</div><div style="font-size:11px;color:#7f879a;margin-top:3px">Design here → publish → Lua pulls it online</div></div><div class="tabs"><button class="tab active" data-page="login">LOGIN DESIGN</button><button class="tab" data-page="menu">MENU / TABS</button></div></div>
<div class="wrap">
<section class="panel"><div class="head"><h2 id="editorTitle">Login designer</h2><p id="editorSub">This is the first screen shown in Lua before the menu.</p></div><div class="controls">
<div id="loginControls">
<div class="section">Text</div><div class="field"><label>Title</label><input id="l_title"></div><div class="grid2"><div class="field"><label>Input hint</label><input id="l_hint"></div><div class="field"><label>OK text</label><input id="l_ok_text"></div></div>
<div class="section">Size & position</div><div class="grid2"><div class="field"><label>Width</label><input id="l_width" type="number"></div><div class="field"><label>Height</label><input id="l_height" type="number"></div></div><div class="grid2"><div class="field"><label>Offset X</label><input id="l_offset_x" type="number"></div><div class="field"><label>Offset Y</label><input id="l_offset_y" type="number"></div></div>
<div class="section">Colors</div><div class="grid2 color"><div class="field"><label>Backdrop</label><input id="l_backdrop" type="color"></div><div class="field"><label>Panel</label><input id="l_panel" type="color"></div></div><div class="grid2 color"><div class="field"><label>Input</label><input id="l_input" type="color"></div><div class="field"><label>Text</label><input id="l_text_color" type="color"></div></div><div class="grid2 color"><div class="field"><label>Hint</label><input id="l_hint_color" type="color"></div><div class="field"><label>OK</label><input id="l_ok_color" type="color"></div></div><div class="grid2 color"><div class="field"><label>Separator</label><input id="l_separator_color" type="color"></div><div></div></div>
<div class="grid2"><div class="field"><label>Backdrop opacity</label><input id="l_backdrop_opacity" type="number" min="0" max="1" step=".01"></div><div class="field"><label>Panel opacity</label><input id="l_panel_opacity" type="number" min=".15" max="1" step=".01"></div></div><div class="grid2"><div class="field"><label>Input opacity</label><input id="l_input_opacity" type="number" min=".15" max="1" step=".01"></div><div class="field"><label>Corner radius</label><input id="l_corner_radius" type="number"></div></div>
<div class="section">Fonts</div><div class="grid2"><div class="field"><label>Title size</label><input id="l_title_size" type="number"></div><div class="field"><label>Input size</label><input id="l_input_size" type="number"></div></div><div class="grid2"><div class="field"><label>OK size</label><input id="l_ok_size" type="number"></div><div class="field"><label>Input radius</label><input id="l_input_radius" type="number"></div></div>
<button class="publish" id="publishLogin">PUBLISH LOGIN TO LUA</button><div class="status" id="loginStatus"></div>
</div>
<div id="menuControls" class="hidden">
<div class="section">Menu</div><div class="field"><label>Title</label><input id="m_title"></div><div class="grid2"><div class="field"><label>Width</label><input id="m_width" type="number"></div><div class="field"><label>Height</label><input id="m_height" type="number"></div></div><div class="grid2"><div class="field"><label>Offset X</label><input id="m_offset_x" type="number"></div><div class="field"><label>Offset Y</label><input id="m_offset_y" type="number"></div></div>
<div class="section">Colors</div><div class="grid2 color"><div class="field"><label>Background</label><input id="m_background" type="color"></div><div class="field"><label>Accent</label><input id="m_accent" type="color"></div></div><div class="grid2 color"><div class="field"><label>Text</label><input id="m_text_color" type="color"></div><div class="field"><label>Rows</label><input id="m_row_color" type="color"></div></div><div class="grid2 color"><div class="field"><label>ON color</label><input id="m_on_color" type="color"></div><div class="field"><label>OFF color</label><input id="m_off_color" type="color"></div></div><div class="grid2"><div class="field"><label>Opacity</label><input id="m_background_opacity" type="number" min=".15" max="1" step=".01"></div><div class="field"><label>Corner radius</label><input id="m_corner_radius" type="number"></div></div>
<div class="section">Typography & rows</div><div class="grid2"><div class="field"><label>Title size</label><input id="m_title_size" type="number"></div><div class="field"><label>Font size</label><input id="m_font_size" type="number"></div></div><div class="grid2"><div class="field"><label>Row height</label><input id="m_row_height" type="number"></div><div class="field"><label>Gap</label><input id="m_gap" type="number"></div></div>
<div class="section">Elements</div><div id="items" class="items"></div><div class="actions"><button class="btn" id="addToggle">+ Toggle</button><button class="btn" id="addButton">+ Button</button><button class="btn" id="addText">+ Text</button><button class="btn" id="resetMenu">Reset default</button></div><button class="publish" id="publishMenu">PUBLISH MENU TO LUA</button><div class="status" id="menuStatus"></div>
</div>
</div></section>
<section class="panel stage"><div class="game"></div><div class="stage-label" id="stageLabel">LOGIN PREVIEW</div><div id="loginBackdrop" class="login-backdrop"></div><div id="loginPreview" class="preview login-card"><div id="lpTitle" class="login-title"></div><div id="lpInput" class="login-input"></div><div id="lpSep" class="login-sep"></div><div id="lpOk" class="login-ok"></div></div><div id="menuPreview" class="preview menu-card hidden"><div id="mpAccent" class="menu-accent"></div><div id="mpTitle" class="menu-head"></div><div id="mpItems" class="menu-items"></div></div></section>
</div>
<script>
const ACTIONS=['NONE','TEST','REFRESH','ESP','ESPLine','EnemyESPWeapon','EnemyESPWeaponOnly','IAwarenessText','IAwarenessArrows','Radar','VehicleESP','ItemESP','GrenadeESP','AirdropESP','TombBoxESP'];
const LOGIN_KEYS=['title','hint','ok_text','width','height','offset_x','offset_y','backdrop','backdrop_opacity','panel','panel_opacity','input','input_opacity','text_color','hint_color','ok_color','separator_color','title_size','input_size','ok_size','corner_radius','input_radius'];
const MENU_KEYS=['title','width','height','offset_x','offset_y','background','background_opacity','accent','text_color','row_color','on_color','off_color','title_size','font_size','row_height','gap','corner_radius'];
let login={},menu={},page='login';
const $=id=>document.getElementById(id); const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function rgba(hex,a){hex=(hex||'#000000').replace('#','');const n=parseInt(hex,16)||0;return `rgba(${n>>16},${(n>>8)&255},${n&255},${a??1})`}
function readLogin(){for(const k of LOGIN_KEYS){const el=$('l_'+k);if(!el)continue;login[k]=el.type==='number'?Number(el.value):el.value}updateLoginPreview()}
function writeLogin(){for(const k of LOGIN_KEYS){const el=$('l_'+k);if(el)el.value=login[k]??''}updateLoginPreview()}
function updateLoginPreview(){const p=$('loginPreview');p.style.width=(login.width||610)+'px';p.style.height=(login.height||290)+'px';p.style.transform=`translate(${login.offset_x||0}px,${login.offset_y||0}px)`;p.style.background=rgba(login.panel||'#15171c',login.panel_opacity??.98);p.style.borderRadius=(login.corner_radius||22)+'px';$('loginBackdrop').style.background=rgba(login.backdrop||'#000',login.backdrop_opacity??.94);const title=$('lpTitle');title.textContent=login.title||'Press OK';title.style.color=login.text_color||'#fff';title.style.fontSize=(login.title_size||28)+'px';title.style.padding=`${Math.max(20,Math.round((login.height||290)*.09))}px 24px ${Math.max(16,Math.round((login.height||290)*.05))}px`;const input=$('lpInput');input.textContent=login.hint||'Activation Key';input.style.margin='0 28px';input.style.padding='0 22px';input.style.height=Math.max(58,Math.round((login.height||290)*.25))+'px';input.style.background=rgba(login.input||'#292c33',login.input_opacity??.98);input.style.color=login.hint_color||'#aaa';input.style.fontSize=(login.input_size||19)+'px';input.style.borderRadius=(login.input_radius||17)+'px';const sep=$('lpSep');sep.style.background=login.separator_color||'#3d4149';sep.style.marginTop=Math.max(20,Math.round((login.height||290)*.10))+'px';const ok=$('lpOk');ok.textContent=login.ok_text||'OK';ok.style.color=login.ok_color||'#1897ff';ok.style.fontSize=(login.ok_size||31)+'px';ok.style.padding=Math.max(14,Math.round((login.height||290)*.06))+'px 10px'}
function readMenu(){for(const k of MENU_KEYS){const el=$('m_'+k);if(!el)continue;menu[k]=el.type==='number'?Number(el.value):el.value}renderItems();updateMenuPreview()}
function writeMenu(){for(const k of MENU_KEYS){const el=$('m_'+k);if(el)el.value=menu[k]??''}renderItems();updateMenuPreview()}
function renderItems(){const box=$('items');box.innerHTML='';(menu.items||[]).forEach((it,i)=>{const row=document.createElement('div');row.className='item';row.draggable=true;const opts=ACTIONS.map(a=>`<option ${a===it.action?'selected':''}>${a}</option>`).join('');row.innerHTML=`<div class="drag">⋮⋮</div><input class="lbl" value="${esc(it.label)}"><select class="typ"><option ${it.type==='toggle'?'selected':''}>toggle</option><option ${it.type==='button'?'selected':''}>button</option><option ${it.type==='text'?'selected':''}>text</option></select><select class="act">${opts}</select><button class="del">×</button>`;row.querySelector('.lbl').oninput=e=>{menu.items[i].label=e.target.value;updateMenuPreview()};row.querySelector('.typ').onchange=e=>{menu.items[i].type=e.target.value;updateMenuPreview()};row.querySelector('.act').onchange=e=>{menu.items[i].action=e.target.value};row.querySelector('.del').onclick=()=>{menu.items.splice(i,1);renderItems();updateMenuPreview()};row.ondragstart=e=>e.dataTransfer.setData('text/plain',String(i));row.ondragover=e=>e.preventDefault();row.ondrop=e=>{e.preventDefault();const from=Number(e.dataTransfer.getData('text/plain'));if(Number.isInteger(from)&&from!==i){const x=menu.items.splice(from,1)[0];menu.items.splice(i,0,x);renderItems();updateMenuPreview()}};box.appendChild(row)})}
function updateMenuPreview(){const p=$('menuPreview');p.style.width=(menu.width||470)+'px';p.style.height=(menu.height||420)+'px';p.style.transform=`translate(${menu.offset_x||0}px,${menu.offset_y||0}px)`;p.style.background=rgba(menu.background||'#111318',menu.background_opacity??.94);p.style.borderRadius=(menu.corner_radius||20)+'px';p.style.color=menu.text_color||'#fff';$('mpAccent').style.background=menu.accent||'#ff453a';const title=$('mpTitle');title.textContent=menu.title||'IDc Studio';title.style.fontSize=(menu.title_size||24)+'px';title.style.padding='17px 20px 12px';const box=$('mpItems');box.innerHTML='';box.style.padding='4px 16px 16px';for(const it of menu.items||[]){const r=document.createElement('div');r.className='pvrow';r.style.height=(menu.row_height||44)+'px';r.style.marginBottom=(menu.gap||8)+'px';r.style.fontSize=(menu.font_size||16)+'px';r.style.padding='0 13px';r.style.borderRadius=Math.min(menu.corner_radius||0,14)+'px';r.style.background=it.type==='text'?'transparent':(it.type==='button'?(menu.accent||'#ff453a'):(menu.row_color||'#1d2028'));if(it.type==='toggle'){r.innerHTML=`<span>${esc(it.label)}</span><span class="pill">OFF</span>`;const pill=r.querySelector('.pill');pill.style.background=menu.off_color||'#ef4444';pill.style.padding='7px 9px';pill.style.borderRadius='9px'}else{r.innerHTML=`<span style="${it.type==='button'?'width:100%;text-align:center':''}">${esc(it.label)}</span>`}box.appendChild(r)}}
async function loadAll(){const [lr,mr]=await Promise.all([fetch('/api/login-design'),fetch('/api/menu-design')]);login=await lr.json();menu=await mr.json();writeLogin();writeMenu()}
async function publishLogin(){readLogin();const b=$('publishLogin');b.disabled=true;b.textContent='PUBLISHING...';try{const r=await fetch('/api/login-design',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(login)});const j=await r.json();login=j.design||login;writeLogin();$('loginStatus').textContent='Published ✓ version '+login.version}catch(e){$('loginStatus').textContent='Publish failed: '+e}finally{b.disabled=false;b.textContent='PUBLISH LOGIN TO LUA'}}
async function publishMenu(){readMenu();const b=$('publishMenu');b.disabled=true;b.textContent='PUBLISHING...';try{const r=await fetch('/api/menu-design',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(menu)});const j=await r.json();menu=j.design||menu;writeMenu();$('menuStatus').textContent='Published ✓ version '+menu.version}catch(e){$('menuStatus').textContent='Publish failed: '+e}finally{b.disabled=false;b.textContent='PUBLISH MENU TO LUA'}}
function setPage(p){page=p;document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x.dataset.page===p));$('loginControls').classList.toggle('hidden',p!=='login');$('menuControls').classList.toggle('hidden',p!=='menu');$('loginPreview').classList.toggle('hidden',p!=='login');$('loginBackdrop').classList.toggle('hidden',p!=='login');$('menuPreview').classList.toggle('hidden',p!=='menu');$('stageLabel').textContent=p==='login'?'LOGIN PREVIEW':'MENU PREVIEW';$('editorTitle').textContent=p==='login'?'Login designer':'Menu / tabs designer';$('editorSub').textContent=p==='login'?'This is the first screen shown in Lua before the menu.':'Design the native Lua menu that is pulled online.'}
document.querySelectorAll('.tab').forEach(x=>x.onclick=()=>setPage(x.dataset.page));for(const k of LOGIN_KEYS){const el=$('l_'+k);if(el)el.oninput=readLogin}for(const k of MENU_KEYS){const el=$('m_'+k);if(el)el.oninput=readMenu}$('publishLogin').onclick=publishLogin;$('publishMenu').onclick=publishMenu;$('addToggle').onclick=()=>{menu.items=menu.items||[];menu.items.push({type:'toggle',label:'New toggle',action:'NONE'});renderItems();updateMenuPreview()};$('addButton').onclick=()=>{menu.items=menu.items||[];menu.items.push({type:'button',label:'New button',action:'NONE'});renderItems();updateMenuPreview()};$('addText').onclick=()=>{menu.items=menu.items||[];menu.items.push({type:'text',label:'New text',action:'NONE'});renderItems();updateMenuPreview()};$('resetMenu').onclick=()=>location.reload();loadAll();
</script></body></html>'''


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
