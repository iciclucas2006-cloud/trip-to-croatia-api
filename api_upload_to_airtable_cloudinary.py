from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import os
import tempfile
import requests
from datetime import datetime

import cloudinary
import cloudinary.uploader

# CONFIGURATION
AIRTABLE_API_KEY = "patSNphd12Ml6TU0M.9d11b7fca188924ea384c2c150026be25d83960823d947ad2557570f45a1eb03"
AIRTABLE_BASE_ID = "appDqUXYgkktrdoWw"
AIRTABLE_TABLE_NAME = "Table 1"
CLOUDINARY_CONFIG = {
    "cloud_name": "dsl6pqzqt",
    "api_key": "955746611986444",
    "api_secret": "rCNx2mWbKdd-FcMBngO9_OscXBE"
}
GOOGLE_GEOCODE_API_KEY = None  # ajoute une clé si tu veux du géocodage précis

# Init
cloudinary.config(**CLOUDINARY_CONFIG)
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "API Trip to Croatia opérationnelle"})

@app.route('/upload', methods=['POST'])
def upload():
    location = request.form.get("location")
    description = request.form.get("description")
    time = request.form.get("time")
    photo = request.files.get("photo")

    if not (location and description and time and photo):
        return jsonify({"error": "Champs manquants"}), 400

    # Sauvegarde temporaire
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = secure_filename(photo.filename)
        temp_path = os.path.join(tmpdir, filename)
        photo.save(temp_path)

        # Conversion HEIC → JPG si nécessaire
        if filename.lower().endswith(".heic"):
            jpg_path = os.path.join(tmpdir, filename + ".jpg")
            img = Image.open(temp_path)
            img.convert("RGB").save(jpg_path, "JPEG")
            temp_path = jpg_path

        # Upload Cloudinary
        upload_result = cloudinary.uploader.upload(temp_path)
        photo_url = upload_result["secure_url"]

    # Géolocalisation approximative
    latitude = None
    longitude = None
    try:
        geo_res = requests.get("https://nominatim.openstreetmap.org/search", params={
            "q": location,
            "format": "json"
        }, headers={"User-Agent": "trip-croatia/1.0"})
        geo_data = geo_res.json()
        if geo_data:
            latitude = float(geo_data[0]["lat"])
            longitude = float(geo_data[0]["lon"])
    except Exception as e:
        print("Erreur de géolocalisation :", e)

    # Envoi vers Airtable
    airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "fields": {
            "Lieu": location,
            "Description": description,
            "Heure": time,
            "Photo": [{"url": photo_url}]
        }
    }
    if latitude and longitude:
        data["fields"]["Latitude"] = latitude
        data["fields"]["Longitude"] = longitude

    response = requests.post(airtable_url, headers=headers, json=data)
    if response.status_code == 200:
        return jsonify({"message": "Étape ajoutée avec succès"})
    else:
        return jsonify({"error": "Erreur Airtable", "details": response.text}), 500
