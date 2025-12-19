
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
    default_settings = {
        "activity_active": False, 
        "announcement": "Welcome to the Classroom Hub!",
        "groups": {
            "1": {"instructions": "Wait for instructions...", "references": []},
            "2": {"instructions": "Wait for instructions...", "references": []},
            "3": {"instructions": "Wait for instructions...", "references": []},
            "4": {"instructions": "Wait for instructions...", "references": []}
        }
    }
    if not os.path.exists(SETTINGS_FILE):
        return default_settings
    try:
        with open(SETTINGS_FILE, 'r') as f:
            data = json.load(f)
            # Migration check: if 'groups' missing (from single-mode), reset or merge
            if 'groups' not in data: 
                return default_settings 
            return data
    except:
        return default_settings

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

@app.route('/')
def student_portal():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    group_id = request.args.get('group_id')
    settings = load_settings()
    
    response = {
        "activity_active": settings.get('activity_active', False),
        "announcement": settings.get('announcement', "")
    }

    if group_id and group_id in settings['groups']:
        response['group_data'] = settings['groups'][group_id]
    
    return jsonify(response)

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
    
    # Global toggles
    if 'activity_active' in data:
        settings['activity_active'] = data['activity_active']
    if 'announcement' in data:
        settings['announcement'] = data['announcement']

    # Group specific updates
    group_id = data.get('group_id')
    if group_id and group_id in settings['groups']:
        if 'instructions' in data:
            settings['groups'][group_id]['instructions'] = data['instructions']

    save_settings(settings)
    return jsonify({"success": True})

@app.route('/admin/upload', methods=['POST'])
def upload_file():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 401
    file = request.files.get('file')
    group_id = request.form.get('group_id')
    
    if not file or file.filename == '': return jsonify({"success": False, "message": "No file"})
    if not group_id: return jsonify({"success": False, "message": "No group ID"})

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Determine type
    ftype = 'file'
    lower = filename.lower()
    if lower.endswith('.pdf'): ftype = 'pdf'
    elif lower.endswith(('.mp4', '.webm')): ftype = 'video'
    elif lower.endswith(('.jpg', '.jpeg', '.png', '.gif')): ftype = 'image'
    elif lower.endswith(('.md', '.markdown')): ftype = 'markdown'
    elif lower.endswith('.docx'): ftype = 'docx'

    settings = load_settings()
    if group_id in settings['groups']:
        # Remove existing ref with same name to avoid duplicates
        settings['groups'][group_id]['references'] = [r for r in settings['groups'][group_id]['references'] if r['filename'] != filename]
        
        new_ref = {
            "name": filename,
            "filename": filename,
            "type": ftype
        }
        settings['groups'][group_id]['references'].append(new_ref)
        save_settings(settings)
        return jsonify({"success": True})
    
    return jsonify({"success": False, "message": "Invalid Group"})

@app.route('/admin/save_markdown', methods=['POST'])
def save_markdown():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    group_id = data.get('group_id')
    title = data.get('title', 'note')
    content = data.get('content', '')
    
    if not group_id: return jsonify({"success": False, "message": "No group ID"})

    filename = secure_filename(title)
    if not filename.lower().endswith('.md'):
        filename += '.md'
        
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'w', encoding='utf-8') as f:
        f.write(content)
        
    settings = load_settings()
    if group_id in settings['groups']:
        # Deduplicate
        settings['groups'][group_id]['references'] = [r for r in settings['groups'][group_id]['references'] if r['filename'] != filename]
        
        new_ref = {
            "name": title if not title.endswith('.md') else title[:-3],
            "filename": filename,
            "type": 'markdown'
        }
        settings['groups'][group_id]['references'].append(new_ref)
        save_settings(settings)
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "Invalid Group"})

@app.route('/admin/get_markdown')
def get_markdown():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 401
    filename = request.args.get('filename')
    if not filename: return jsonify({"success": False, "message": "No filename"})
    
    filename = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        return jsonify({"success": False, "message": "File not found"})
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    return jsonify({"success": True, "content": content})

@app.route('/admin/delete_reference', methods=['POST'])
def delete_reference():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    group_id = data.get('group_id')
    filename = data.get('filename')
    
    settings = load_settings()
    if group_id in settings['groups']:
        settings['groups'][group_id]['references'] = [r for r in settings['groups'][group_id]['references'] if r['filename'] != filename]
        save_settings(settings)
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/admin/upload_image', methods=['POST'])
def upload_image():
    if not session.get('logged_in'): return jsonify({"error": "Unauthorized"}), 401
    if 'image' not in request.files: return jsonify({"error": "No file"}), 400
    
    file = request.files['image']
    if file.filename == '': return jsonify({"error": "No filename"}), 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    return jsonify({"data": {"filePath": f"/static/uploads/{filename}"}})

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
