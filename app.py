from flask import Flask, render_template, request, jsonify
import pandas as pd
import spacy

app = Flask(__name__) 

# Charger le modèle linguistique françai
nlp = spacy.load("fr_core_news_md")

# Charger les fichiers CSV
fichier_csv1 = '/workspaces/projet-NTL/monuments_maroc.csv'
fichier_csv2 = '/workspaces/projet-NTL/ma.csv'
monument_df = pd.read_csv(fichier_csv1)
ma_df = pd.read_csv(fichier_csv2)

@app.route("/")
def index():
    return render_template("index.html")

def detect_intention(text):
    """ Détecter si l'utilisateur demande la population, la ville ou des détails. """
    text = text.lower()
    if "population" in text:
        return "population"
    elif "ville" in text or "où" in text or "localisation" in text:
        return "ville"
    elif "description" in text or "information" in text or "parle-moi" in text or "présente" in text:
        return "description"
    else:
        return "general"

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    doc = nlp(user_message)

    # Détecter l'intention
    intention = detect_intention(user_message)

    # Chercher une entité reconnue (ville ou monument)
    entite = None
    for ent in doc.ents:
        if ent.label_ == "LOC" or ent.label_ == "PER" or ent.label_ == "MISC":
            entite = ent.text
            break

    if not entite:
        mots = [token.text for token in doc if not token.is_stop and not token.is_punct]
        entite = mots[-1] if mots else user_message.strip()

    # Chercher dans la base des villes
    ville_info = ma_df[ma_df['city'].str.contains(entite, case=False, na=False)]

    if not ville_info.empty:
        ville = ville_info.iloc[0]

        if intention == "population":
            response = f"La population de {ville['city']} est de {ville['population']} habitants."
        elif intention == "ville":
            response = f"{ville['city']} est une ville située en {ville['country']}."
        else:
            response = f"{ville['city']} est une ville du {ville['country']} avec une population de {ville['population']} habitants."

        # Ajouter l'image de la ville si dispo dans monuments
        image_ville_info = monument_df[monument_df['ville'].str.contains(entite, case=False, na=False)]
        if not image_ville_info.empty:
            image_url = image_ville_info.iloc[0]['image_ville_url']
            response += f'<br><img src="{image_url}" alt="Image de la ville" width="400" style="padding-right: 20px;">'



    else:
        # Sinon chercher dans la base des monuments
        monument_info = monument_df[monument_df['nom'].str.contains(entite, case=False, na=False)]

        if not monument_info.empty:
            monument = monument_info.iloc[0]

            if intention == "ville":
                response = f"Le monument {monument['nom']} est situé à {monument['ville']}. Veux-tu plus d'informations ?"
            else:
                response = (f"{monument['nom']} est un {monument['type']} situé à {monument['ville']}. "
                            f"{monument['description']} Pour en savoir plus : {monument['lien_wikipedia']}.")

                response += f'<br><img src="{monument["image_monument_url"]}" alt="Image du monument" width="300">'

        else:
            response = "Je n'ai pas trouvé d'informations correspondantes. Pouvez-vous reformuler votre question ?"

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
 