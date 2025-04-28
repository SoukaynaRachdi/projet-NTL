from flask import Flask, render_template, request, jsonify
import pandas as pd
import spacy
import unicodedata
from langdetect import detect
from deep_translator import GoogleTranslator
from rapidfuzz import process, fuzz  # Fuzzy Matching

app = Flask(__name__)

def enlever_accents(texte):
    """Supprimer les accents d'un texte."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texte)
        if unicodedata.category(c) != 'Mn'
    )

# Charger modèle linguistique français
nlp = spacy.load("fr_core_news_md")

# Charger les fichiers CSV
fichier_csv1 = '/workspaces/projet-NTL/monuments_maroc.csv'
fichier_csv2 = '/workspaces/projet-NTL/ma.csv'
monument_df = pd.read_csv(fichier_csv1)
ma_df = pd.read_csv(fichier_csv2)

# Ajouter colonnes sans accents
ma_df['city_noaccent'] = ma_df['city'].apply(lambda x: enlever_accents(str(x).lower()))
monument_df['ville_noaccent'] = monument_df['ville'].apply(lambda x: enlever_accents(str(x).lower()))
monument_df['nom_noaccent'] = monument_df['nom'].apply(lambda x: enlever_accents(str(x).lower()))

# Créer les listes pour fuzzy matching
liste_villes = ma_df['city_noaccent'].dropna().unique().tolist()
liste_monuments = monument_df['nom_noaccent'].dropna().unique().tolist()

@app.route("/")
def index():
    return render_template("index.html")

def detect_intention(text):
    """Détecter l'intention de la question."""
    text = text.lower()
    if "population" in text:
        return "population"
    elif "ville" in text or "où" in text or "localisation" in text:
        return "ville"
    elif "description" in text or "information" in text or "parle-moi" in text or "présente" in text:
        return "description"
    else:
        return "general"

def trouver_meilleure_correspondance(entite, liste_valeurs):
    """Trouver la meilleure correspondance floue."""
    result = process.extractOne(entite, liste_valeurs, scorer=fuzz.WRatio)
    
    if result:
        correspondance = result[0]  # Correspondance
        score = result[1]  # Score
        if score >= 60:  # Seuil plus bas pour tolérer plus d'erreurs
            return correspondance
    return None

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    doc = nlp(user_message)

    # Détection de la langue
    langue_message = detect(user_message)

    # Détection d'intention
    intention = detect_intention(user_message)

    # Chercher l'entité dans le message
    entite = None
    for ent in doc.ents:
        if ent.label_ in ["LOC", "PER", "MISC"]:
            entite = ent.text
            break

    if not entite:
        mots = [token.text for token in doc if not token.is_stop and not token.is_punct]
        entite = mots[-1] if mots else user_message.strip()

    # Supprimer les accents de l'entité
    entite_sans_accent = enlever_accents(entite.lower())

    # Trouver la meilleure correspondance parmi les villes
    meilleure_ville = trouver_meilleure_correspondance(entite_sans_accent, liste_villes)

    if meilleure_ville:
        ville_info = ma_df[ma_df['city_noaccent'] == meilleure_ville].iloc[0]

        if intention == "population":
            response = f"La population de {ville_info['city']} est de {ville_info['population']} habitants."
        elif intention == "ville":
            response = f"{ville_info['city']} est une ville située en {ville_info['country']}."
        else:
            response = f"{ville_info['city']} est une ville du {ville_info['country']} avec une population de {ville_info['population']} habitants."

        # Ajouter image de la ville si existe
        image_ville_info = monument_df[monument_df['ville_noaccent'] == meilleure_ville]
        if not image_ville_info.empty:
            image_url = image_ville_info.iloc[0]['image_ville_url']
            response += f'<br><img src="{image_url}" alt="Image de la ville" width="400" style="padding-right: 20px;">'

    else:
        # Chercher dans les monuments si aucune ville n'est trouvée
        meilleure_monument = trouver_meilleure_correspondance(entite_sans_accent, liste_monuments)

        if meilleure_monument:
            monument_info = monument_df[monument_df['nom_noaccent'] == meilleure_monument].iloc[0]

            if intention == "ville":
                response = f"Le monument {monument_info['nom']} est situé à {monument_info['ville']}. Veux-tu plus d'informations ?"
            else:
                response = (f"{monument_info['nom']} est un {monument_info['type']} situé à {monument_info['ville']}. "
                            f"{monument_info['description']} Pour en savoir plus : {monument_info['lien_wikipedia']}.")
                response += f'<br><img src="{monument_info["image_monument_url"]}" alt="Image du monument" width="300">'
        else:
            response = "Je n'ai pas trouvé d'informations correspondantes. Peut-être vouliez-vous dire 'Fes' ou 'Casablanca' ?"

    # Traduire la réponse si nécessaire
    if langue_message == 'ar':
        response = GoogleTranslator(source='fr', target='ar').translate(response)
    elif langue_message == 'en':
        response = GoogleTranslator(source='fr', target='en').translate(response)

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
