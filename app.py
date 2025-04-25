import pandas as pd

# Charger les données
ma_df = pd.read_csv('ma.csv')
monument_df = pd.read_csv('monument.csv')

# Exemple : afficher les premières lignes des données
print(ma_df.head())
print(monument_df.head())
import spacy

# Charger le modèle linguistique français
nlp = spacy.load("fr_core_news_md")

# Exemple : analyser un texte
doc = nlp("Où se trouve la ville de Marrakech ?")
for ent in doc.ents:
    print(ent.text, ent.label_)
from flask import Flask, render_template, request, jsonify
import pandas as pd
import spacy

app = Flask(__name__)

# Charger les données
ma_df = pd.read_csv('ma.csv')
monument_df = pd.read_csv('monument.csv')

# Charger le modèle linguistique français
nlp = spacy.load("fr_core_news_md")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    doc = nlp(user_message)

    # Rechercher une ville dans le message
    ville = None
    for ent in doc.ents:
        if ent.label_ == "GPE":  # GPE correspond à une entité géopolitique (ville, pays, etc.)
            ville = ent.text
            break

    if ville:
        # Rechercher des informations sur la ville
        ville_info = ma_df[ma_df['city'].str.contains(ville, case=False, na=False)]
        if not ville_info.empty:
            # Construire une réponse basée sur les informations de la ville
            response = f"La ville de {ville} est située en {ville_info['country'].iloc[0]} avec une population de {ville_info['population'].iloc[0]} habitants."
        else:
            response = f"Je n'ai pas trouvé d'informations sur la ville de {ville}."
    else:
        response = "Je n'ai pas compris le nom de la ville. Pouvez-vous reformuler votre question ?"

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
