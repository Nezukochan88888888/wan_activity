import os
import json
import socket

# Configuration and File Contents
SETTINGS_DEFAULT = {
    "activity_active": False,
    "announcement": "Welcome to the Classroom Hub!",
    "media_type": "none", # 'pdf', 'video', or 'none'
    "media_filename": ""
}

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Portal - Classroom Hub</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .hero-section { background: #0d6efd; color: white; padding: 2rem 0; margin-bottom: 2rem; }
        .media-container { max-width: 900px; margin: 0 auto; }
        iframe, video { width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="hero-section text-center">
        <h1>Classroom Hub</h1>
        <p class="lead" id="announcement">Loading announcement...</p>
    </div>

    <div class="container text-center" id="setup-view">
        <div class="card p-4 shadow-sm">
            <h3>Select Your Group</h3>
            <div class="d-flex justify-content-center gap-3 mt-3">
                <button class="btn btn-outline-primary btn-lg" onclick="selectGroup(1)">Group 1</button>
                <button class="btn btn-outline-primary btn-lg" onclick="selectGroup(2)">Group 2</button>
                <button class="btn btn-outline-primary btn-lg" onclick="selectGroup(3)">Group 3</button>
                <button class="btn btn-outline-primary btn-lg" onclick="selectGroup(4)">Group 4</button>
            </div>
        </div>
    </div>

    <div class="container d-none" id="activity-view">
        <div class="alert alert-info text-center" id="waiting-msg">
            Waiting for teacher to start the activity...
        </div>
        <div id="media-content" class="media-container mt-4"></div>
    </div>

    <footer class="mt-5 text-center text-muted small">
        <p>Requires internet for initial CSS load, or save bootstrap.min.css to /static for 100% offline use.</p>
    </footer>

    <script>
        let selectedGroup = null;

        function selectGroup(num) {
            selectedGroup = num;
            document.getElementById('setup-view').classList.add('d-none');
            document.getElementById('activity-view').classList.remove('d-none');
            checkStatus();
        }

        async function checkStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                document.getElementById('announcement').innerText = data.announcement;

                const contentDiv = document.getElementById('media-content');
                const waitingMsg = document.getElementById('waiting-msg');

                if (data.activity_active) {
                    waitingMsg.classList.add('d-none');
                    if (data.media_type === 'pdf') {
                        contentDiv.innerHTML = `<iframe src="/static/uploads/${data.media_filename}" height="600px"></iframe>`;
                    } else if (data.media_type === 'video') {
                        contentDiv.innerHTML = `<video controls playsinline><source src="/static/uploads/${data.media_filename}" type="video/mp4"></video>`;
                    } else if (data.media_type === 'image') {
                        contentDiv.innerHTML = `<img src="/static/uploads/${data.media_filename}" class="img-fluid rounded shadow">`;
                    } else {
                        contentDiv.innerHTML = '<p class="text-center">No media available.</p>';
                    }
                } else {
                    waitingMsg.classList.remove('d-none');
                    contentDiv.innerHTML = '';
                }
            } catch (e) {
                console.error("Failed to fetch status", e);
            }
            setTimeout(checkStatus, 3000);
        }
    </script>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teacher Dashboard - Classroom Hub</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <span class="navbar-brand">Teacher Dashboard</span>
            <button class="btn btn-outline-danger btn-sm" onclick="logout()">Logout</button>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-6">
                <div class="card shadow-sm mb-4">
                    <div class="card-header bg-primary text-white">Activity Controls</div>
                    <div class="card-body">
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="activityToggle" onchange="updateSettings()">
                            <label class="form-check-label" for="activityToggle">Enable Student Activity View</label>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Teacher's Announcement</label>
                            <textarea id="announcementText" class="form-control" rows="3" onblur="updateSettings()"></textarea>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card shadow-sm mb-4">
                    <div class="card-header bg-secondary text-white">Media Management</div>
                    <div class="card-body">
                        <form id="uploadForm" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label class="form-label">Select PDF, MP4, or Image (JPG/PNG)</label>
                                <input type="file" name="file" class="form-control" id="fileInput" accept=".pdf,.mp4,.jpg,.jpeg,.png">
                            </div>
                            <button type="button" class="btn btn-success w-100" onclick="uploadFile()">Upload & Set Active</button>
                        </form>
                        <hr>
                        <p>Current Media: <strong id="currentMedia">None</strong></p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function loadSettings() {
            const res = await fetch('/api/status');
            const data = await res.json();
            document.getElementById('activityToggle').checked = data.activity_active;
            document.getElementById('announcementText').value = data.announcement;
            document.getElementById('currentMedia').innerText = data.media_filename || 'None';
        }

        async function updateSettings() {
            const activity_active = document.getElementById('activityToggle').checked;
            const announcement = document.getElementById('announcementText').value;
            
            await fetch('/admin/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ activity_active, announcement })
            });
        }

        async function uploadFile() {
            const formData = new FormData(document.getElementById('uploadForm'));
            const res = await fetch('/admin/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if(data.success) {
                alert('Uploaded successfully!');
                loadSettings();
            } else {
                alert('Upload failed: ' + data.message);
            }
        }

        function logout() {
            window.location.href = '/logout';
        }

        loadSettings();
    </script>
</body>
</html>
"""

APP_PY = r'''
import os
import json
import socket
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
from waitress import serve

app = Flask(__name__)
app.secret_key = 'super-secret-classroom-key'
ADMIN_PASSWORD = 'admin123'
UPLOAD_FOLDER = 'static/uploads'
SETTINGS_FILE = 'settings.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"activity_active": False, "announcement": "Welcome!", "media_type": "none", "media_filename": ""}
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

@app.route('/')
def student_portal():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(load_settings())

@app.route('/admin')
def admin_panel():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('admin.html')

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('password') == ADMIN_PASSWORD:
        session['logged_in'] = True
        return redirect(url_for('admin_panel'))
    return "Invalid Password", 401

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_panel'))

@app.route('/admin/update', methods=['POST'])
def update_settings():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    settings = load_settings()
    settings['activity_active'] = data.get('activity_active', settings['activity_active'])
    settings['announcement'] = data.get('announcement', settings['announcement'])
    save_settings(settings)
    return jsonify({"success": True})

@app.route('/admin/upload', methods=['POST'])
def upload_file():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 401
    if 'file' not in request.files: return jsonify({"success": False, "message": "No file"})
    
    file = request.files['file']
    if file.filename == '': return jsonify({"success": False, "message": "No selected file"})
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    settings = load_settings()
    settings['media_filename'] = filename
    if filename.lower().endswith('.pdf'):
        settings['media_type'] = 'pdf'
    elif filename.lower().endswith('.mp4'):
        settings['media_type'] = 'video'
    elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        settings['media_type'] = 'image'
    else:
        settings['media_type'] = 'none'
    
    save_settings(settings)
    return jsonify({"success": True, "filename": filename})

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == '__main__':
    lan_ip = get_lan_ip()
    port = 5000
    print("\n" + "="*50)
    print("      CLASSROOM HUB IS RUNNING")
    print(f"      Student URL: http://{lan_ip}:{port}")
    print(f"      Admin URL:   http://{lan_ip}:{port}/admin")
    print("="*50 + "\n")
    serve(app, host='0.0.0.0', port=port)
'''

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="d-flex align-items-center justify-content-center vh-100 bg-light">
    <div class="card p-4 shadow" style="width: 300px;">
        <h4 class="text-center">Teacher Login</h4>
        <form action="/login" method="post">
            <div class="mb-3">
                <input type="password" name="password" class="form-control" placeholder="Password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Login</button>
        </form>
    </div>
</body>
</html>
"""

def setup():
    print("--- Starting Classroom Hub Auto-Installer ---")
    
    # Create directories
    for folder in ['templates', 'static/uploads']:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created directory: {folder}")

    # Create files
    files_to_create = {
        'settings.json': json.dumps(SETTINGS_DEFAULT, indent=4),
        'templates/index.html': INDEX_HTML,
        'templates/admin.html': ADMIN_HTML,
        'templates/login.html': LOGIN_HTML,
        'app.py': APP_PY
    }

    for path, content in files_to_create.items():
        with open(path, 'w') as f:
            f.write(content)
        print(f"Created file: {path}")

    print("\nInstallation Complete!")
    print("To start the server, run: python app.py")
    print("Note: Ensure 'flask' and 'waitress' are installed: pip install flask waitress")

if __name__ == "__main__":
    setup()
