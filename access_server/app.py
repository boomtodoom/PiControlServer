import os
import yaml
from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
from flask_basicauth import BasicAuth

import credentials

UPLOAD_FOLDER = 'uploads'
CONFIG_FILE = 'config.yaml'
SCRIPTS_FOLDER = 'scripts'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set up a username and password for client authentication
app.config['BASIC_AUTH_USERNAME'] = credentials.auth_username
app.config['BASIC_AUTH_PASSWORD'] = credentials.auth_password
basic_auth = BasicAuth(app)

# Home page
@app.route('/')
def index():
    return '''
    <h1>Home</h1>
    <a href="/file-management">File Management</a>
    <br>
    <a href="/config-management">Config Management</a>
    <br>
    <a href="/script-management">Script Management</a>
    '''

# File management page
@app.route('/file-management')
def file_management():
    return '''
    <h1>File Management</h1>
    <a href="/upload-page">Upload File</a>
    <br>
    <a href="/uploads">View Uploaded Files</a>
    '''

# Upload page
@app.route('/upload-page')
def upload_page():
    return '''
    <h1>Upload File or Folder</h1>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="files" multiple webkitdirectory>
        <input type="submit" value="Upload">
    </form>
    '''



# Config management page
@app.route('/config-management')
def config_management():
    return '''
    <h1>Config Management</h1>
    <a href="/config">Edit Config</a>
    '''

# Script management page
@app.route('/script-management')
def script_management():
    return '''
    <h1>Script Management</h1>
    <a href="/run-script">Run Script</a>
    <br>
    <a href="/upload-script-page">Upload Script</a>
    '''

# Upload script page
@app.route('/upload-script-page')
def upload_script_page():
    return '''
    <h1>Upload Script</h1>
    <form method="POST" action="/upload-script" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
    '''

# Upload endpoint
@app.route('/upload', methods=['POST'])
@basic_auth.required
def upload_file():
    if 'files' not in request.files:
        return 'No file part'

    files = request.files.getlist('files')

    if not files:
        return 'No files selected'

    for file in files:
        if file.filename == '':
            return 'No selected file'
        # Ensure directory structure is preserved if folders are uploaded
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

    return 'Files uploaded successfully!'


# Serve uploaded files
@app.route('/uploads', methods=['GET'])
@basic_auth.required
def uploads():
    uploads = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template_string('''
        <h1>Uploaded Files</h1>
        <ul>
            {% for upload in uploads %}
            <li><a href="/uploads/{{ upload }}">{{ upload }}</a></li>
            {% endfor %}
        </ul>
        ''', uploads=uploads)

@app.route('/uploads/<filename>', methods=['GET'])
@basic_auth.required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# View and edit config
@app.route('/config', methods=['GET', 'POST'])
@basic_auth.required
def config():
    if request.method == 'POST':
        config_data = request.form['config']
        with open(CONFIG_FILE, 'w') as config_file:
            config_file.write(config_data)
        return 'Config updated!'
    else:
        # Display current config
        with open(CONFIG_FILE, 'r') as config_file:
            config_data = config_file.read()
        return render_template_string('''
            <h1>Edit Config</h1>
            <form method="POST">
                <textarea name="config" rows="10" cols="30">{{config}}</textarea><br>
                <input type="submit" value="Save">
            </form>
            ''', config=config_data)

# Run specific scripts
@app.route('/run-script', methods=['GET', 'POST'])
@basic_auth.required
def run_script():
    if request.method == 'POST':
        script_name = request.form['script_name']
        script_path = os.path.join(SCRIPTS_FOLDER, script_name)
        if os.path.exists(script_path):
            os.system(f'bash {script_path}')
            return f'Script {script_name} executed!'
        else:
            return 'Script not found!'
    else:
        # List available scripts
        scripts = os.listdir(SCRIPTS_FOLDER)
        return render_template_string('''
            <h1>Run Script</h1>
            <form method="POST">
                <select name="script_name">
                    {% for script in scripts %}
                    <option value="{{ script }}">{{ script }}</option>
                    {% endfor %}
                </select><br>
                <input type="submit" value="Run Script">
            </form>
            ''', scripts=scripts)

# Upload scripts
@app.route('/upload-script', methods=['POST'])
@basic_auth.required
def upload_script():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    file.save(os.path.join(SCRIPTS_FOLDER, file.filename))
    return f'Script {file.filename} uploaded successfully!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
