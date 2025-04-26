import spacy
from spacy.lang.fr.stop_words import STOP_WORDS
import string

# Charger le modèle linguistique français
nlp = spacy.load("fr_core_news_md")

def nettoyer_texte(texte):
    # Conversion en minuscules
    texte = texte.lower()
    # Suppression des ponctuations
    texte = texte.translate(str.maketrans('', '', string.punctuation))
    return texte

def tokenisation(texte):
    doc = nlp(texte)
    tokens = [token.text for token in doc if token.text not in STOP_WORDS and not token.is_punct]
    return tokens

def lemmatisation(tokens):
    doc = nlp(" ".join(tokens))
    lemmes = [token.lemma_ for token in doc]
    return lemmes

def extract_entities(texte):
    doc = nlp(texte)
    entities = []
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:  # GPE et LOC sont des labels pour les entités géographiques (villes, pays)
            entities.append(ent.text)
    return entities

def preprocessing(texte):
    texte_nettoye = nettoyer_texte(texte)
    tokens = tokenisation(texte_nettoye)
    lemmes = lemmatisation(tokens)
    
    # Extraire les entités nommées du texte
    entities = extract_entities(texte)
    
    # Retourner les lemmes et les entités
    return lemmes, entities
