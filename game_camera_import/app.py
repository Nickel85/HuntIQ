from flask import Flask, render_template, request, redirect, url_for, flash
import os
from datetime import datetime
from PIL import Image
import exifread

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your_secret_key'

# Upload folder
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Extract metadata (EXIF) from the image if available
def get_metadata(image_path):
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
            metadata = {
                'DateTime': tags.get('EXIF DateTimeOriginal', 'N/A'),
                'CameraModel': tags.get('Image Model', 'N/A'),
                'GPS': tags.get('GPS GPSLatitude', 'N/A'),
            }
            return metadata
    except Exception as e:
        print(f"Error reading metadata: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract metadata
        metadata = get_metadata(file_path)

        flash('File successfully uploaded!', 'success')
        return render_template('index.html', filename=filename, metadata=metadata)
    else:
        flash('Invalid file format', 'error')
        return redirect(request.url)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
