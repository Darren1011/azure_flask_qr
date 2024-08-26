from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import requests
from time import sleep
from config import Config, upload_to_azure_blob

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config.from_object(Config)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-qr', methods=['POST'])
def generate_qr():
    text_prompt = request.form.get('text_prompt')
    qr_code_data = request.form.get('qr_code_data')
    image_prompt = None

    if 'image_prompt' in request.files:
        image_file = request.files['image_prompt']
        if image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_prompt = upload_to_azure_blob(image_path, app.config['AZURE_CONTAINER_NAME'], filename)

    payload = {
        "functions": [{"url": "https://gooey.ai/functions/", "trigger": "pre"}],
        "variables": {"apples": 8},
        "qr_code_data": qr_code_data,
        "use_url_shortener": False,
        "text_prompt": text_prompt,
        "negative_prompt": "ugly, disfigured, low quality, blurry, nsfw,",
        "image_prompt": image_prompt,
        "image_prompt_scale": 0.5,
        "controlnet_conditioning_scale": [0.45, 0.4],
    }

    response = requests.post(
        "https://api.gooey.ai/v3/art-qr-code/async/",
        headers={
            "Authorization": "Bearer " + app.config['GOOEY_API_KEY'],
        },
        json=payload,
    )

    if not response.ok:
        print(f"Error: {response.status_code}, {response.content}")
        return jsonify({"error": "Failed to generate QR code"}), 500

    status_url = response.headers["Location"]
    while True:
        response = requests.get(
            status_url, headers={"Authorization": "Bearer " + app.config['GOOEY_API_KEY']}
        )
        if not response.ok:
            print(f"Error: {response.status_code}, {response.content}")
            return jsonify({"error": "Failed to get QR code status"}), 500
        result = response.json()
        if result["status"] == "completed":
            return render_template('result.html', qr_code_url=result["output"]["output_images"][0])
        elif result["status"] == "failed":
            return jsonify(result), 400
        else:
            sleep(3)

if __name__ == '__main__':
    app.run(debug=True, port=8000)