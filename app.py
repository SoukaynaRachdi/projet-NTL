from flask import Flask, render_template, request, jsonify
import pandas as pd
import spacy
import unicodedata
from langdetect import detect
from deep_translator import GoogleTranslator
from rapidfuzz import process, fuzz
import re

app = Flask(__name__)

# Fonction pour enlever les accents
def enlever_accents(texte):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texte)
        if unicodedata.category(c) != 'Mn'
    )

# Fonction pour traduire uniquement le texte (sans balises HTML)
def traduire_texte_sans_html(texte, langue_source, langue_cible):
    segments = re.split(r'(<[^>]+>)', texte)
    segments_traduits = []
    for segment in segments:
        if re.match(r'<[^>]+>', segment):
            segments_traduits.append(segment)
        else:
            if segment.strip():
                segment_traduit = GoogleTranslator(source=langue_source, target=langue_cible).translate(segment)
                segments_traduits.append(segment_traduit)
            else:
                segments_traduits.append(segment)
    return ''.join(segments_traduits)

# Charger le modèle SpaCy français
nlp = spacy.load("fr_core_news_md")

# Charger les données
fichier_csv1 = 'monuments_maroc.csv'
fichier_csv2 = 'ma.csv'
monument_df = pd.read_csv(fichier_csv1)
ma_df = pd.read_csv(fichier_csv2)

# Ajouter colonnes sans accents
ma_df['city_noaccent'] = ma_df['city'].apply(lambda x: enlever_accents(str(x).lower()))
monument_df['ville_noaccent'] = monument_df['ville'].apply(lambda x: enlever_accents(str(x).lower()))
monument_df['nom_noaccent'] = monument_df['nom'].apply(lambda x: enlever_accents(str(x).lower()))

# Créer listes pour matching
liste_villes = ma_df['city_noaccent'].dropna().unique().tolist()
liste_monuments = monument_df['nom_noaccent'].dropna().unique().tolist()

@app.route("/")
def index():
    return render_template("index.html")

# Détecter l’intention d’une question
def detect_intention(text):
    text = text.lower()
    if "monument" in text:
        return "monument"
    elif "population" in text:
        return "population"
    elif "ville" in text or "où" in text or "localisation" in text:
        return "ville"
    elif "description" in text or "information" in text or "parle-moi" in text or "présente" in text:
        return "description"
    else:
        return "general"

# Matching flou
def trouver_meilleure_correspondance(entite, liste_valeurs):
    result = process.extractOne(entite, liste_valeurs, scorer=fuzz.WRatio)
    if result:
        correspondance = result[0]
        score = result[1]
        if score >= 60:
            return correspondance
    return None

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    langue_message = detect(user_message)

    # Traduction du message arabe en français
    if langue_message == 'ar':
        user_message = GoogleTranslator(source='ar', target='fr').translate(user_message)

    doc = nlp(user_message)
    intention = detect_intention(user_message)

    # Extraire entité
    entite = None
    for ent in doc.ents:
        if ent.label_ in ["LOC", "PER", "MISC"]:
            entite = ent.text
            break
    if not entite:
        mots = [token.text for token in doc if not token.is_stop and not token.is_punct]
        entite = mots[-1] if mots else user_message.strip()

    entite_sans_accent = enlever_accents(entite.lower())
    response = "Désolé, je n'ai pas compris votre demande."

    if intention == "monument":
        if "maroc" in entite.lower():
            monuments = monument_df[['nom', 'ville', 'type']].dropna().drop_duplicates()
            response = "Voici une liste de monuments célèbres au Maroc :<br>"
            for _, row in monuments.iterrows():
                response += f"- {row['nom']} à {row['ville']} ({row['type']})<br>"
        else:
            meilleure_ville = trouver_meilleure_correspondance(entite_sans_accent, liste_villes)
            if meilleure_ville:
                monuments_ville = monument_df[monument_df['ville_noaccent'] == meilleure_ville].drop_duplicates()
                if not monuments_ville.empty:
                    response = f"<div class='monuments-container'>"
                    response += f"<h3>Voici quelques monuments situés à {monuments_ville.iloc[0]['ville']} :</h3>"
                    for _, row in monuments_ville.iterrows():
                        description = row["description"]
                        # Traduire si nécessaire
                        if langue_message != 'en':
                            try:
                                description = GoogleTranslator(source='en', target=langue_message).translate(description)
                            except:
                                pass
                        response += f'''
                            <div class="monument-cadre">
                                <img src="{row["image_monument_url"]}" alt="Image du monument" class="image-ville-monument">
                                <div class="monument-details">
                                    <p><strong>{row["nom"]} ({row["type"]})</strong></p>
                                    <p><strong>{description} ({row["type"]})</strong></p>
                                    <p><a href="{row["lien_wikipedia"]}" target="_blank">Wikipedia</a></p>
                                </div>
                            </div>
                        '''
                    response += "</div>"
                else:
                    response = "Je n'ai pas trouvé de monuments correspondant à votre demande."
    else:
        meilleure_ville = trouver_meilleure_correspondance(entite_sans_accent, liste_villes)

        if meilleure_ville:
            ville_info = ma_df[ma_df['city_noaccent'] == meilleure_ville].iloc[0]
            if intention == "population":
                response = f"La population de {ville_info['city']} est de {ville_info['population']} habitants."
            elif intention == "ville":
                response = f"{ville_info['city']} est une ville située en {ville_info['country']}."
            else:
                response = f"{ville_info['city']} est une ville du {ville_info['country']} avec une population de {ville_info['population']} habitants."

            image_ville_info = monument_df[monument_df['ville_noaccent'] == meilleure_ville].drop_duplicates()
            if not image_ville_info.empty:
                image_url = image_ville_info.iloc[0]['image_ville_url']
                response += f'<br><img src="{image_url}" alt="Image de la ville" class="image-ville-monument">'
        else:
            meilleure_monument = trouver_meilleure_correspondance(entite_sans_accent, liste_monuments)
            if meilleure_monument:
                monument_info = monument_df[monument_df['nom_noaccent'] == meilleure_monument].iloc[0]
                description = monument_info['description']
                if langue_message != 'en':
                    try:
                        description = GoogleTranslator(source='en', target=langue_message).translate(description)
                    except:
                        pass
                if intention == "ville":
                    response = f"Le monument {monument_info['nom']} est situé à {monument_info['ville']}."
                else:
                    response = (f"{monument_info['nom']} est un {monument_info['type']} situé à {monument_info['ville']}. "
                                f"{description} Pour en savoir plus : {monument_info['lien_wikipedia']}.")
                    response += f'<br><img src="{monument_info["image_monument_url"]}" alt="Image du monument" class="image-ville-monument">'

    # Traduction finale du message généré (structure HTML), sauf description déjà traduite
    if langue_message == 'ar':
        response = traduire_texte_sans_html(response, 'fr', 'ar')
    elif langue_message == 'en':
        response = traduire_texte_sans_html(response, 'fr', 'en')

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
