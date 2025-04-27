from flask import Flask, render_template, request, jsonify
import pandas as pd
import spacy
import unicodedata
from langdetect import detect

app = Flask(__name__)

def enlever_accents(texte):
    """Supprimer les accents d'un texte."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texte)
        if unicodedata.category(c) != 'Mn'
    )

# Charger le modèle linguistique pour le français
nlp_fr = spacy.load("fr_core_news_md")
nlp_en = spacy.load("en_core_web_sm")
nlp_ar = spacy.load("xx_ent_wiki_sm")  # Modèle multilingue (inclut l'arabe)

# Charger les fichiers CSV
fichier_csv1 = '/workspaces/projet-NTL/monuments_maroc.csv'
fichier_csv2 = '/workspaces/projet-NTL/ma.csv'
monument_df = pd.read_csv(fichier_csv1)
ma_df = pd.read_csv(fichier_csv2)

ma_df['city_noaccent'] = ma_df['city'].apply(lambda x: enlever_accents(str(x).lower()))
monument_df['ville_noaccent'] = monument_df['ville'].apply(lambda x: enlever_accents(str(x).lower()))
monument_df['nom_noaccent'] = monument_df['nom'].apply(lambda x: enlever_accents(str(x).lower()))

@app.route("/")
def index():
    return render_template("index.html")

def detect_intention(text, lang):
    """ Détecter l'intention de l'utilisateur selon le texte et la langue. """
    text = text.lower().strip()  # Normaliser le texte (minuscule et suppression des espaces superflus)
    
    if lang == 'fr':
        if any(greeting in text for greeting in ["salut", "bonjour", "coucou", "bonsoir"]):  # Vérifier les salutations en français
            return "salutation"
        if "population" in text:
            return "population"
        elif "ville" in text or "où" in text or "localisation" in text:
            return "ville"
        elif "description" in text or "information" in text or "parle-moi" in text or "présente" in text:
            return "description"
    
    elif lang == 'en':
        if any(greeting in text for greeting in ["hello", "hi", "hey", "good morning", "good evening"]):  # Vérifier les salutations en anglais
            return "salutation"
        if "population" in text:
            return "population"
        elif "city" in text or "location" in text:
            return "city"
        elif "description" in text or "info" in text or "tell me" in text:
            return "description"
    
    elif lang == 'ar':
        if any(greeting in text for greeting in ["مرحبا", "السلام عليكم", "صباح الخير", "مساء الخير"]):  # Vérifier les salutations en arabe
            return "salutation"
        if "عدد السكان" in text or "السكان" in text:
            return "population"
        elif "مدينة" in text or "أين" in text or "الموقع" in text:
            return "ville"
        elif "وصف" in text or "معلومات" in text:
            return "description"
    
    return "general"


def detect_language(text):
    """ Détecter la langue du texte de l'utilisateur. """
    return detect(text)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    lang = detect_language(user_message)  # Détecter la langue du message de l'utilisateur
    if lang == 'fr':
        doc = nlp_fr(user_message)
    elif lang == 'en':
        doc = nlp_en(user_message)
    elif lang == 'ar':
        doc = nlp_ar(user_message)
    else:
        lang = 'fr'
        doc = nlp_fr(user_message)

    # Détecter l'intention
    intention = detect_intention(user_message, lang)

    # Si l'intention est une salutation, répondre avec un message approprié
    if intention == "salutation":
        if lang == 'fr':
            response = "Bonjour ! Comment puis-je vous aider aujourd'hui ?"
        elif lang == 'en':
            response = "Hello! How can I assist you today?"
        elif lang == 'ar':
            response = "مرحبا! كيف يمكنني مساعدتك اليوم؟"
        return jsonify({"response": response})

    # Chercher une entité reconnue (ville ou monument)
    entite = None
    for ent in doc.ents:
        if ent.label_ == "LOC" or ent.label_ == "PER" or ent.label_ == "MISC":
            entite = ent.text
            break

    if not entite:
        mots = [token.text for token in doc if not token.is_stop and not token.is_punct]
        entite = mots[-1] if mots else user_message.strip()
    entite_sans_accent = enlever_accents(entite.lower())

    # Chercher dans la base des villes
    ville_info = ma_df[ma_df['city_noaccent'].str.contains(entite_sans_accent, na=False)]

    if not ville_info.empty:
        ville = ville_info.iloc[0]

        if intention == "population":
            response = f"La population de {ville['city']} est de {ville['population']} habitants." if lang == 'fr' else \
                       f"The population of {ville['city']} is {ville['population']} people." if lang == 'en' else \
                       f"عدد سكان {ville['city']} هو {ville['population']} نسمة."  # Arabic

        elif intention == "ville":
            response = f"{ville['city']} est une ville située en {ville['country']}." if lang == 'fr' else \
                       f"{ville['city']} is a city located in {ville['country']}." if lang == 'en' else \
                       f"{ville['city']} هي مدينة تقع في {ville['country']}."  # Arabic
        else:
            response = f"{ville['city']} est une ville du {ville['country']} avec une population de {ville['population']} habitants." if lang == 'fr' else \
                       f"{ville['city']} is a city in {ville['country']} with a population of {ville['population']} people." if lang == 'en' else \
                       f"{ville['city']} هي مدينة في {ville['country']} ويبلغ عدد سكانها {ville['population']} نسمة."  # Arabic

        # Ajouter l'image de la ville si dispo dans monuments
        monument_df['ville_noaccent'] = monument_df['ville'].apply(lambda x: enlever_accents(str(x).lower()))
        image_ville_info = monument_df[monument_df['ville_noaccent'].str.contains(entite_sans_accent, na=False)]
        if not image_ville_info.empty:
            image_url = image_ville_info.iloc[0]['image_ville_url']
            response += f'<br><img src="{image_url}" alt="Image de la ville" width="400" style="padding-right: 20px;">'

    else:
        # Sinon chercher dans la base des monuments
        monument_info = monument_df[monument_df['nom_noaccent'].str.contains(entite_sans_accent, na=False)]

        if not monument_info.empty:
            monument = monument_info.iloc[0]

            if intention == "ville":
                response = f"Le monument {monument['nom']} est situé à {monument['ville']}. Veux-tu plus d'informations ?" if lang == 'fr' else \
                           f"The monument {monument['nom']} is located in {monument['ville']}. Do you want more info?" if lang == 'en' else \
                           f"التمثال {monument['nom']} يقع في {monument['ville']}. هل تريد المزيد من المعلومات؟"  # Arabic
            else:
                response = (f"{monument['nom']} est un {monument['type']} situé à {monument['ville']}. "
                            f"{monument['description']} Pour en savoir plus : {monument['lien_wikipedia']}." if lang == 'fr' else \
                           f"{monument['nom']} is a {monument['type']} located in {monument['ville']}. "
                           f"{monument['description']} For more info: {monument['lien_wikipedia']}." if lang == 'en' else \
                           f"{monument['nom']} هو {monument['type']} يقع في {monument['ville']}. "
                           f"{monument['description']} لمزيد من المعلومات: {monument['lien_wikipedia']}." )  # Arabic

                response += f'<br><img src="{monument["image_monument_url"]}" alt="Image du monument" width="300">'

        else:
            response = "Je n'ai pas trouvé d'informations correspondantes. Pouvez-vous reformuler votre question ?" if lang == 'fr' else \
                       "I couldn't find matching information. Can you rephrase your question?" if lang == 'en' else \
                       "لم أتمكن من العثور على معلومات متطابقة. هل يمكنك إعادة صياغة سؤالك؟"  # Arabic

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
