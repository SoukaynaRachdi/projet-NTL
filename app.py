from flask import Flask, render_template, request, jsonify
import pandas as pd
import spacy

app = Flask(__name__)

# Charger le modèle linguistique français
nlp = spacy.load("fr_core_news_md")

# Charger les fichiers CSV
fichier_csv1 = '/workspaces/projet-NTL/monuments_maroc.csv'
fichier_csv2 = '/workspaces/projet-NTL/ma.csv'
monument_df = pd.read_csv(fichier_csv1)
ma_df = pd.read_csv(fichier_csv2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    
    # Utiliser spaCy pour essayer de détecter une entité
    doc = nlp(user_message)

    ville = None
    for ent in doc.ents:
        if ent.label_ == "LOC":
            ville = ent.text
            break

    # ✅ Si spaCy n'a rien trouvé, prendre directement ce que l'utilisateur a écrit
    if not ville:
        ville = user_message.strip()

    # Chercher d'abord dans la base des villes
    ville_info = ma_df[ma_df['city'].str.contains(ville, case=False, na=False)]

    if not ville_info.empty:
        response = f"La ville de {ville} est située en {ville_info['country'].iloc[0]} avec une population de {ville_info['population'].iloc[0]} habitants."
    else:
        # Si ce n'est pas une ville, on cherche dans les monuments
        monument_info = monument_df[monument_df['nom'].str.contains(ville, case=False, na=False)]

        if not monument_info.empty:
            info = monument_info.iloc[0]
            response = f"{info['nom']} est un {info['type']} situé à {info['ville']}. {info['description']} Pour en savoir plus : {info['lien_wikipedia']}."
        else:
            response = "Je n'ai pas trouvé d'informations correspondantes. Pouvez-vous reformuler votre question ?"

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
