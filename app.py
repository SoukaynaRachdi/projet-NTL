from flask import Flask, render_template, request, jsonify
import pandas as pd
import spacy
from nlp_processing import preprocessing  # Importation du module de prétraitement

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
    
    # Prétraiter le message de l'utilisateur
    lemmes, entities = preprocessing(user_message)
    
    # Si des entités sont extraites, on essaie de trouver une ville dans ces entités
    ville = None
    for entity in entities:
        if "GPE" in nlp(entity).ents or "LOC" in nlp(entity).ents:  # Vérifie que c'est une entité géographique
            ville = entity
            break

    if ville:
        # Recherche des informations sur la ville dans ma_df
        ville_info = ma_df[ma_df['city'].str.contains(ville, case=False, na=False)]
        if not ville_info.empty:
            # Construire une réponse avec les informations disponibles
            response = f"La ville de {ville} est située en {ville_info['country'].iloc[0]} avec une population de {ville_info['population'].iloc[0]} habitants."
        else:
            response = f"Je n'ai pas trouvé d'informations sur la ville de {ville}."
    else:
        response = "Je n'ai pas compris le nom de la ville. Pouvez-vous reformuler votre question ?"

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
