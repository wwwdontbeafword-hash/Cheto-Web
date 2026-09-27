from flask import Flask, render_template_string, send_from_directory, jsonify, request
import os
import shutil
import json

app = Flask(__name__)
FILE_NAME = "game_patch_4.6.0.21572.pak"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# مسار المجلد الهدف (Android)
TARGET_PATH = "/storage/emulated/0/Android/data/com.pubg.krmobile/files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/Paks/puffer_temp/"

PAGE = r'''<!doctype html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CHETO · Korea Pack</title>
  <style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: linear-gradient(135deg, #1a1410 0%, #2d1f15 50%, #1a1410 100%);
  color: #f6e9da;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
}

.stars {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.star {
  position: absolute;
  width: 2px;
  height: 2px;
  background: #fff;
  border-radius: 50%;
  animation: twinkle 3s infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

.container {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 30px 20px;
}

header {
  text-align: center;
  margin-bottom: 50px;
  animation: slideDown 0.6s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.logo-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(145deg, #e8a557, #c67c3c);
  border-radius: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 50px;
  font-weight: bold;
  box-shadow: 0 20px 60px rgba(232, 165, 87, 0.3);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

h1 {
  font-size: 3.5em;
  font-weight: 700;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #f6e9da, #e8a557);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.1em;
  color: #bfa997;
  margin-bottom: 30px;
  letter-spacing: 2px;
}

.card {
  background: linear-gradient(145deg, rgba(40, 25, 18, 0.8), rgba(20, 12, 8, 0.8));
  border: 1px solid rgba(200, 130, 80, 0.2);
  border-radius: 30px;
  padding: 40px;
  backdrop-filter: blur(20px);
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.4);
  animation: slideUp 0.8s ease;
  transition: all 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card:hover {
  border-color: rgba(200, 130, 80, 0.4);
  box-shadow: 0 40px 100px rgba(0, 0, 0, 0.5);
}

.card h2 {
  font-size: 2em;
  margin-bottom: 15px;
  color: #f6e9da;
}

.card p {
  color: #bfa997;
  line-height: 1.8;
  margin-bottom: 30px;
  font-size: 1.05em;
}

.button-group {
  display: flex;
  gap: 15px;
  margin-top: 30px;
  flex-wrap: wrap;
}

button {
  flex: 1;
  min-width: 160px;
  padding: 18px 30px;
  border: none;
  border-radius: 15px;
  font-size: 1em;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.4s ease;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  position: relative;
  overflow: hidden;
}

button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  transition: left 0.5s ease;
}

button:hover::before {
  left: 100%;
}

.btn-download {
  background: linear-gradient(135deg, #d68a4b, #a85f32);
  color: white;
  box-shadow: 0 15px 40px rgba(214, 138, 75, 0.3);
}

.btn-download:hover {
  transform: translateY(-3px);
  box-shadow: 0 25px 60px rgba(214, 138, 75, 0.5);
}

.btn-delete {
  background: linear-gradient(135deg, #7a8d7e, #5a6b60);
  color: white;
  box-shadow: 0 15px 40px rgba(122, 141, 126, 0.2);
}

.btn-delete:hover {
  transform: translateY(-3px);
  box-shadow: 0 25px 60px rgba(122, 141, 126, 0.4);
}

button:active {
  transform: scale(0.97);
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(10, 6, 4, 0.9);
  backdrop-filter: blur(10px);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.overlay.active {
  display: flex;
}

.modal {
  background: linear-gradient(145deg, rgba(40, 25, 18, 0.95), rgba(20, 12, 8, 0.95));
  border: 1px solid rgba(200, 130, 80, 0.3);
  border-radius: 30px;
  padding: 50px;
  max-width: 500px;
  width: 90%;
  text-align: center;
  box-shadow: 0 50px 150px rgba(0, 0, 0, 0.8);
  animation: modalSlideIn 0.5s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(-30px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.progress-icon {
  font-size: 60px;
  margin-bottom: 20px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { 
    transform: scale(1);
    opacity: 1;
  }
  50% { 
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.progress-icon.success {
  animation: none;
  color: #90ee90;
  font-size: 70px;
}

.modal h3 {
  font-size: 1.8em;
  margin-bottom: 15px;
  color: #f6e9da;
}

.modal p {
  color: #bfa997;
  margin-bottom: 30px;
  font-size: 1em;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background: rgba(100, 70, 40, 0.5);
  border-radius: 10px;
  overflow: hidden;
  margin: 30px 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #d68a4b, #f0a04b);
  width: 0%;
  border-radius: 10px;
  transition: width 0.3s ease;
  box-shadow: 0 0 15px rgba(214, 138, 75, 0.5);
}

.progress-text {
  display: flex;
  justify-content: space-between;
  color: #bfa997;
  font-size: 0.9em;
  margin-top: 10px;
}

.success-message {
  display: none;
  text-align: center;
}

.success-message.show {
  display: block;
  animation: slideUp 0.5s ease;
}

.checkmark {
  width: 100px;
  height: 100px;
  margin: 0 auto 30px;
  border: 3px solid #90ee90;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 60px;
  animation: checkmarkDraw 0.6s ease;
}

@keyframes checkmarkDraw {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.success-message h3 {
  color: #90ee90;
  font-size: 2em;
  margin-bottom: 10px;
}

.success-message p {
  color: #c7b29f;
  margin-bottom: 30px;
}

.btn-close {
  background: linear-gradient(135deg, #90ee90, #76c776);
  color: #0a0604;
  padding: 15px 40px;
  font-size: 0.95em;
  margin-top: 20px;
}

.btn-close:hover {
  transform: translateY(-2px);
}

code {
  background: rgba(0,0,0,0.3);
  padding: 6px 10px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
  word-break: break-all;
  display: inline-block;
}

.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 2000;
  max-width: 400px;
}

.toast {
  background: linear-gradient(135deg, rgba(40, 25, 18, 0.95), rgba(20, 12, 8, 0.95));
  border: 1px solid rgba(200, 130, 80, 0.3);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 15px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
  animation: toastSlideIn 0.4s ease;
  color: #f6e9da;
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateX(400px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.toast b {
  display: block;
  margin-bottom: 5px;
  color: #f0a04b;
}

.toast span {
  font-size: 0.95em;
  color: #bfa997;
}

@media (max-width: 768px) {
  h1 {
    font-size: 2.5em;
  }
  
  .card {
    padding: 25px;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  button {
    min-width: auto;
  }
  
  .modal {
    padding: 30px;
  }
  
  .modal h3 {
    font-size: 1.5em;
  }
}
  </style>
</head>
<body>

<div class="stars" id="stars"></div>

<div class="container">
  <header>
    <div class="logo-icon">📦</div>
    <h1>KOREA Pack</h1>
    <p class="subtitle">Premium Download Experience</p>
  </header>

  <div class="card">
    <h2>📲 Game Patch 4.6.0</h2>
    <p>Experience seamless installation with our advanced download system. Fast, secure, and reliable.</p>
    <div class="button-group">
      <button class="btn-download" onclick="startDownload()">
        ⬇️ DOWNLOAD NOW
      </button>
      <button class="btn-delete" onclick="removeDownload()">
        🗑️ REMOVE DOWNLOAD
      </button>
    </div>
  </div>
</div>

<div class="overlay" id="overlay">
  <div class="modal">
    <div id="loading-content">
      <div class="progress-icon" id="icon">⬇️</div>
      <h3 id="title">Preparing Download</h3>
      <p id="status">Initializing...</p>
      <div class="progress-bar">
        <div class="progress-fill" id="progressFill"></div>
      </div>
      <div class="progress-text">
        <span id="percentage">0%</span>
        <span id="speed">Processing...</span>
      </div>
    </div>
    
    <div id="success-content" class="success-message">
      <div class="checkmark">✓</div>
      <h3>Installation Complete!</h3>
      <p>Your patch has been successfully installed to the game directory.</p>
      <button class="btn-close" onclick="closeModal()">CLOSE</button>
    </div>
  </div>
</div>

<div class="toast-container" id="toastContainer"></div>

<script>
// تهيئة النجوم
function createStars() {
  const starsContainer = document.getElementById('stars');
  for (let i = 0; i < 50; i++) {
    const star = document.createElement('div');
    star.className = 'star';
    star.style.left = Math.random() * 100 + '%';
    star.style.top = Math.random() * 100 + '%';
    star.style.animationDelay = Math.random() * 3 + 's';
    starsContainer.appendChild(star);
  }
}
createStars();

// إظهار الإشعارات
function showToast(title, message) {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<b>${title}</b><span>${message}</span>`;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'toastSlideIn 0.4s ease reverse';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

// عرض الـ Modal
function showModal() {
  document.getElementById('overlay').classList.add('active');
  document.getElementById('loading-content').style.display = 'block';
  document.getElementById('success-content').classList.remove('show');
}

// إغلاق الـ Modal
function closeModal() {
  document.getElementById('overlay').classList.remove('active');
}

// تحديث شريط التقدم
function updateProgress(percentage, status) {
  document.getElementById('progressFill').style.width = percentage + '%';
  document.getElementById('percentage').textContent = percentage + '%';
  document.getElementById('status').textContent = status;
}

// بدء التحميل
async function startDownload() {
  try {
    showModal();
    document.getElementById('title').textContent = 'Downloading Patch';
    document.getElementById('icon').textContent = '⬇️';
    updateProgress(0, 'Connecting to server...');
    
    // 1. تحميل الملف
    const response = await fetch('/download-patch');
    
    if (!response.ok) {
      throw new Error('Server error - file not found');
    }
    
    updateProgress(40, 'Preparing file...');
    
    const blob = await response.blob();
    
    if (blob.size === 0) {
      throw new Error('Downloaded file is empty - check if game_patch_4.6.0.21572.pak exists in server directory');
    }
    
    updateProgress(70, 'Starting download to your device...');
    
    // 2. تحميل الملف مباشرة للـ Browser Downloads
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'game_patch_4.6.0.21572.pak';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    updateProgress(100, 'Download complete!');
    
    setTimeout(() => {
      document.getElementById('loading-content').style.display = 'none';
      document.getElementById('success-content').innerHTML = `
        <div class="checkmark">✓</div>
        <h3>Download Complete!</h3>
        <p>File saved to: Downloads/game_patch_4.6.0.21572.pak</p>
        <p style="font-size: 0.9em; color: #a99583; margin-top: 15px;">
          📂 Move it to:<br/>
          <code style="background: rgba(0,0,0,0.3); padding: 8px; border-radius: 5px; display: block; margin-top: 8px; font-size: 0.85em; word-break: break-all;">
          /storage/emulated/0/Android/data/com.pubg.krmobile/files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/Paks/puffer_temp/
          </code>
        </p>
        <button class="btn-close" onclick="closeModal()">DONE</button>
      `;
      document.getElementById('success-content').classList.add('show');
      showToast('Download Ready', 'Move file to game directory manually');
    }, 500);
    
  } catch (error) {
    console.error('Error:', error);
    closeModal();
    showToast('Error', error.message || 'Unknown error occurred');
  }
}

// حذف التحميل
async function removeDownload() {
  try {
    showModal();
    document.getElementById('title').textContent = 'Remove Download';
    document.getElementById('icon').textContent = '🗑️';
    updateProgress(0, 'Preparing removal...');
    
    const response = await fetch('/remove-patch', {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error('Could not process removal');
    }
    
    updateProgress(100, 'Ready to remove');
    
    setTimeout(() => {
      document.getElementById('loading-content').style.display = 'none';
      document.getElementById('success-content').classList.add('show');
      document.getElementById('success-content').innerHTML = `
        <div class="checkmark">✓</div>
        <h3>Delete Instructions</h3>
        <p style="margin-top: 15px;">
          📁 Open <b>Files/Downloads</b> app<br/>
          🔍 Find: <code style="background: rgba(0,0,0,0.3); padding: 4px 8px; border-radius: 3px; display: inline-block;">game_patch_4.6.0.21572.pak</code><br/>
          🗑️ Long press → Delete
        </p>
        <button class="btn-close" onclick="closeModal()">CLOSE</button>
      `;
      showToast('Remove File', 'Delete from Downloads manually');
    }, 500);
    
  } catch (error) {
    console.error('Error:', error);
    closeModal();
    showToast('Error', error.message);
  }
}
</script>

</body>
</html>'''

@app.route('/')
def home():
    return render_template_string(PAGE)

@app.route('/download-patch')
def download_patch():
    """تحميل الملف من موقع السيرفر بشكل آمن"""
    try:
        file_path = os.path.join(BASE_DIR, FILE_NAME)
        
        # التحقق من وجود الملف
        if not os.path.exists(file_path):
            app.logger.error(f'File not found: {file_path}')
            return jsonify({'error': f'Patch file not found in {BASE_DIR}'}), 404
        
        # التحقق من أن الملف ليس فارغاً
        if os.path.getsize(file_path) == 0:
            return jsonify({'error': 'Patch file is empty'}), 400
        
        app.logger.info(f'Downloading patch: {file_path}')
        return send_from_directory(BASE_DIR, FILE_NAME, as_attachment=True, download_name=FILE_NAME)
    
    except Exception as e:
        app.logger.error(f'Download error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/remove-patch', methods=['DELETE'])
def remove_patch():
    """معالجة طلب حذف - رسالة توجيهية"""
    try:
        return jsonify({
            'success': True,
            'message': 'Please delete the file manually from Downloads',
            'path': 'Downloads/game_patch_4.6.0.21572.pak'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
