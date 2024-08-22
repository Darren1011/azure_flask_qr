from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import requests
from time import sleep
from config import Config
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

app = Flask(__name__, static_folder='../qr-frontend/build')
CORS(app)  # Enable CORS for all routes

app.config.from_object(Config)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def upload_to_azure(file_path, container_name, blob_name):
    """Uploads a file to Azure Blob Storage and returns the public URL."""
    blob_service_client = BlobServiceClient.from_connection_string(app.config['AZURE_STORAGE_CONNECTION_STRING'])
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    return blob_client.url

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
            image_prompt = upload_to_azure(image_path, app.config['AZURE_CONTAINER_NAME'], filename)

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
            return jsonify(result)
        elif result["status"] == "failed":
            return jsonify(result), 400
        else:
            sleep(3)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)