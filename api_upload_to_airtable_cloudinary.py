
from flask import Flask, request, jsonify
import requests
import os
from PIL import Image
from io import BytesIO
import base64
import cloudinary
import cloudinary.uploader

# Configuration de Cloudinary
cloudinary.config(
  cloud_name = "dsl6pqzqt",
  api_key = "955746611986444",
  api_secret = "rCNx2mWbKdd-FcMBngO9_OscXBE"
)

# Configuration Airtable
AIRTABLE_TOKEN = "patSNphd12Ml6TU0M.9d11b7fca188924ea384c2c150026be25d83960823d947ad2557570f45a1eb03"
AIRTABLE_BASE_ID = "appDqUXYgkktrdoWw"
AIRTABLE_TABLE_ID = "tblWZ46gqRnAnf2bd"

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        lieu = request.form.get('lieu')
        description = request.form.get('description')
        heure = request.form.get('heure')
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')
        image = request.files.get('photo')

        if not image:
            return jsonify({'error': 'Pas de fichier reçu'}), 400

        # Convertir HEIC → JPG si nécessaire
        if image.filename.lower().endswith('.heic'):
            from pillow_heif import register_heif_opener
            register_heif_opener()
            img = Image.open(image)
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            buffer.seek(0)
            upload_result = cloudinary.uploader.upload(buffer, resource_type="image")
        else:
            upload_result = cloudinary.uploader.upload(image, resource_type="image")

        photo_url = upload_result['secure_url']

        # Envoi à Airtable
        airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "fields": {
                "Lieu": lieu,
                "Description": description,
                "Heure": heure,
                "Latitude": float(lat),
                "Longitude": float(lng),
                "Photo": [{"url": photo_url}]
            }
        }

        resp = requests.post(airtable_url, headers=headers, json=payload)
        if resp.status_code == 200:
            return jsonify({'status': 'success', 'photo_url': photo_url}), 200
        else:
            return jsonify({'error': 'Airtable API error', 'details': resp.json()}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
