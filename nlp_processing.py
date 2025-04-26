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

def preprocessing(texte):
    texte_nettoye = nettoyer_texte(texte)
    tokens = tokenisation(texte_nettoye)
    lemmes = lemmatisation(tokens)
    return lemmes

def extract_city(texte):
    doc = nlp(texte)
    for ent in doc.ents:
        if ent.label_ == "LOC" or ent.label_ == "GPE":
            return ent.text
    return None
