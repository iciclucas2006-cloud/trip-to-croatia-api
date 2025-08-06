import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

AIRTABLE_TOKEN = "patSNphd12Ml6TU0M"
BASE_ID = "UXYgkktrdoWw"
TABLE_ID = "tblWZ46gqRnAnf2bd"

@app.route("/")
def home():
    return "API Trip to Croatia opérationnelle"

@app.route("/upload", methods=["POST"])
def upload():
    try:
        name = request.form.get("name")
        lieu = request.form.get("lieu")
        description = request.form.get("description")
        heure = request.form.get("heure")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        airtable_url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
        headers = {
            "Authorization": f"Bearer {AIRTABLE_TOKEN}",
            "Content-Type": "application/json"
        }

        fields = {
            "Name": name,
            "Lieu": lieu,
            "Description": description,
            "Heure": heure,
            "Latitude": float(latitude),
            "Longitude": float(longitude)
        }

        data = {"fields": fields}
        resp = requests.post(airtable_url, headers=headers, json=data)

        if resp.status_code != 200:
            print("🛑 ERREUR AIRTABLE :", resp.status_code)
            print("💬 Message :", resp.text)
            return jsonify({"error": "Erreur Airtable", "details": resp.text}), 400

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)