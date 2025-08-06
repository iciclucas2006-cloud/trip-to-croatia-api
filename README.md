
# Trip to Croatia – API Flask

## Objectif

Ce projet :

- Reçoit les données d’un formulaire HTML externe
- Géolocalise via adresse ou GPS
- Envoie les données vers Airtable
- Upload les photos sur Cloudinary

## Déploiement Render

1. Crée un repo GitHub avec ces fichiers
2. Va sur https://dashboard.render.com
3. “New +” → Web Service
4. Config :
   - Type : Web service
   - Build command : *(laisser vide)*
   - Start command : `python app.py`

## Utilisation

1. Ouvre `formulaire.html`
2. Remplis
3. Envoie → va vers ton API Flask → Airtable + Cloudinary
