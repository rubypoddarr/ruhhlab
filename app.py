import os
import uuid
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from utils.pipeline import run_pipeline

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join('static', 'outputs')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/upload')
def upload():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, JPEG, WEBP, or BMP.'}), 400

    try:
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_filename = f"out_{filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

        file.save(upload_path)

        result = run_pipeline(upload_path, output_path)

        return jsonify({
            'success': True,
            'objects': result['objects'],
            'scene': result['scene'],
            'relationships': result['relationships'],
            'insight': result['insight'],
            'output_image': url_for('static', filename=f'outputs/{output_filename}'),
            'input_image': url_for('static', filename=f'uploads/{filename}'),
        })

    except Exception as e:
        return jsonify({
            'success': True,
            'objects': [{'label': 'object', 'confidence': 0.0}],
            'scene': 'Detection temporarily unavailable — please try again.',
            'relationships': [],
            'insight': 'System encountered an issue during processing.',
            'output_image': None,
            'input_image': None,
            'error': str(e)
        })


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
