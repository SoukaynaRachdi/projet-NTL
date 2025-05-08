from flask import Flask, render_template, request, jsonify
import pandas as pd
import spacy
import unicodedata
from langdetect import detect
from deep_translator import GoogleTranslator
from rapidfuzz import process, fuzz
import re
from flask import session
from flask_session import Session
import os



app = Flask(__name__)

# Configurer la clé secrète pour signer les sessions
app.secret_key = os.urandom(24)  # Génère une clé secrète aléatoire de 24 octets
# Configuration pour utiliser le stockage des sessions sur le système de fichiers
app.config['SESSION_TYPE'] = 'filesystem'  # Stocker les sessions sur le disque
Session(app)


def suggestion_proactive(intention, entite, langue):
    suggestion = ""
    if intention == "ville" and entite:
        suggestion = f"Souhaitez-vous découvrir les monuments de {entite} ?"
    elif intention == "monument" and entite:
        type_monument = monument_df[monument_df['nom_noaccent'] == enlever_accents(entite.lower())]['type']
        if not type_monument.empty:
            type_ = type_monument.values[0]
            suggestion = f"Souhaitez-vous voir d'autres monuments du type {type_} ?"

    if langue == 'ar':
        suggestion = GoogleTranslator(source='fr', target='ar').translate(suggestion)
    elif langue == 'en':
        suggestion = GoogleTranslator(source='fr', target='en').translate(suggestion)

    # Enregistrer le contexte dans la session
    session['suggested_intention'] = intention
    session['suggested_entite'] = entite
    return suggestion

def is_affirmative(text):
    text = text.lower()
    affirmations = ["oui", "yes", "montre moi", "ok, c'est parti", "d'accord", "show me"]
    return any(phrase in text for phrase in affirmations)

def is_negative(text):
    text = text.lower()
    negatives = ["non", "no", "pas", "ne veux pas"]
    return any(phrase in text for phrase in negatives)

def get_response(intention, entite, langue_message):
    response = ""
    if intention == "monument" and entite:
        monuments = monument_df[monument_df['ville_noaccent'] == enlever_accents(entite.lower())].drop_duplicates()
        if not monuments.empty:
            response = f"Voici quelques monuments situés à {entite} :<br>"
            for _, row in monuments.iterrows():
                description = row["description"]
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
                            <p>{description}</p>
                            <p><a href="{row["lien_wikipedia"]}" target="_blank">Wikipedia</a></p>
                        </div>
                    </div>
                '''
        else:
            response = "Je n'ai pas trouvé de monuments correspondant à votre demande."
    else:
        response = "Désolé, je n'ai pas pu répondre à votre demande."

    return response


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

      # 🔁 Gérer les réponses "oui" ou "non" en priorité
    if is_affirmative(user_message):
        suggested_intention = session.get('suggested_intention')
        suggested_entite = session.get('suggested_entite')

        print(f"Intention suggérée : {suggested_intention}")
        print(f"Entité suggérée : {suggested_entite}")

        response = ""

        if suggested_intention == "monument":
            response = f"Voici quelques monuments célèbres de {suggested_entite} : [liste ici]."

        elif suggested_intention == "monument_details":
            response = f"Voici plus de détails sur un monument de {suggested_entite} : [détails ici]."

        elif suggested_intention == "ville":
            # Appel à la fonction principale pour retourner les monuments de la ville
            response = get_response("monument", suggested_entite, langue_message)

        # Nettoyage du contexte
        session.pop('suggested_intention', None)
        session.pop('suggested_entite', None)

        # Si get_response retourne déjà une réponse JSON
        if isinstance(response, dict):
            return jsonify(response)

        # Traduction de la réponse si besoin
        if langue_message == 'ar':
            response = traduire_texte_sans_html(response, 'fr', 'ar')
        elif langue_message == 'en':
            response = traduire_texte_sans_html(response, 'fr', 'en')

        return jsonify({"response": response})

    elif is_negative(user_message):
        response = "D'accord, n'hésitez pas à poser une autre question."

        if langue_message == 'ar':
            response = traduire_texte_sans_html(response, 'fr', 'ar')
        elif langue_message == 'en':
            response = traduire_texte_sans_html(response, 'fr', 'en')

        return jsonify({"response": response})


    
   

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
             # Enregistrer l'intention et l'entité pour référence dans la session
             
            session['suggested_intention'] = 'monument_details'
            session['suggested_entite'] = entite

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
                suggestion = suggestion_proactive("ville", entite, langue_message)
                response += f"<br>{suggestion}"


            else:
                response = f"{ville_info['city']} est une ville du {ville_info['country']} avec une population de {ville_info['population']} habitants."
                suggestion = suggestion_proactive("ville", entite, langue_message)
                response += f"<br>{suggestion}"

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

