
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Airtable config
AIRTABLE_TOKEN = "patSNphd12Ml6TU0M"
BASE_ID = "UXYgkktrdoWw"
TABLE_ID = "tblWZ46gqRnAnf2bd"

# Cloudinary config
CLOUDINARY_CLOUD = "dsl6pqzqt"
CLOUDINARY_API_KEY = "955746611986444"
CLOUDINARY_API_SECRET = "rCNx2mWbKdd-FcMBngO9_OscXBE"
CLOUDINARY_UPLOAD_PRESET = "default_preset"

@app.route("/upload", methods=["POST"])
def upload():
    try:
        lieu = request.form.get("lieu")
        description = request.form.get("description")
        heure = request.form.get("heure")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        photo = request.files.get("photo")

        photo_url = None
        if photo:
            files = {"file": (secure_filename(photo.filename), photo.stream, photo.mimetype)}
            data = { "upload_preset": CLOUDINARY_UPLOAD_PRESET }
            r = requests.post(f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD}/image/upload", data=data, files=files, auth=(CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET))
            if r.status_code == 200:
                photo_url = r.json().get("secure_url")
            else:
                return jsonify({"error": "Échec upload Cloudinary"}), 400

        airtable_url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_TOKEN}",
            "Content-Type": "application/json"
        }
        fields = {
            "Lieu": lieu,
            "Description": description,
            "Heure": heure,
            "Latitude": float(latitude),
            "Longitude": float(longitude),
        }
        if photo_url:
            fields["Photo"] = [{"url": photo_url}]

        data = {"fields": fields}
        resp = requests.post(airtable_url, headers=headers, json=data)

        if resp.status_code != 200:
            return jsonify({"error": "Erreur Airtable", "details": resp.text}), 400

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ← Render injecte automatiquement la variable PORT
    app.run(host="0.0.0.0", port=port, debug=True)
