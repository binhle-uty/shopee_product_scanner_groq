import re

def preprocess(sentence: str) -> str:
    "Preprocess a sentence to remove not word characters"
    sentence=str(sentence)
    filtered_words = re.sub('\W+',' ', sentence)
    return filtered_words