from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords_tfidf(description: str, max_keywords: int = 5) -> list[str]:
    vectorizer = TfidfVectorizer(max_features=max_keywords, stop_words=["и", "в", "на", "для"])
    tfidf_matrix = vectorizer.fit_transform([description])
    return vectorizer.get_feature_names_out()


'''from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

nltk.download("punkt")
nltk.download("stopwords")

def extract_keywords_simple(description: str, max_keywords: int = 5) -> list[str]:
    tokens = word_tokenize(description.lower())
    stop_words = set(stopwords.words("russian"))
    keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
    return keywords[:max_keywords]'''