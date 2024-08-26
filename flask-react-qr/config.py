import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import qrcode
from PIL import Image

# Load environment variables from .env file
load_dotenv()

class Config:
    GOOEY_API_KEY = os.getenv('GOOEY_API_KEY')
    UPLOAD_FOLDER = 'uploads'
    AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_CONTAINER_NAME = os.getenv('AZURE_CONTAINER_NAME')

def upload_to_azure_blob(file_path, container_name, blob_name):
    """Uploads a file to Azure Blob Storage and returns the public URL."""
    blob_service_client = BlobServiceClient.from_connection_string(Config.AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    return blob_client.url

def generate_qr_code(data, file_path):
    """Generates a QR code and saves it to the specified file path."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img.save(file_path)
    return file_path