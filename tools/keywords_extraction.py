import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords_tfidf(description: str, max_keywords: int = 3, ngram_range: tuple = (2, 2)) -> list[str]:
    # Создаем объект TfidfVectorizer с поддержкой чисел и n-грамм
    description = description.replace('/', ' ').replace('-', ' ')
    vectorizer = TfidfVectorizer(
        stop_words=["и", "в", "на", "для"],  # Игнорируем стоп-слова
        ngram_range=ngram_range,           # Указываем диапазон для n-грамм
        token_pattern=r"(?u)\b\w+\b"       # Настройка для включения чисел
    )
    
    # Преобразуем текст в матрицу TF-IDF
    tfidf_matrix = vectorizer.fit_transform([description])
    
    # Получаем список слов/словосочетаний и их весов
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray()[0]  # Вектор весов для текста
    
    # Сортируем по убыванию веса
    sorted_indices = np.argsort(tfidf_scores)[::-1]  # Индексы в порядке убывания
    sorted_keywords = [feature_names[i] for i in sorted_indices if tfidf_scores[i] > 0]
    
    # Возвращаем топ-N ключевых слов или словосочетаний
    return sorted_keywords[:max_keywords]

"""from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

nltk.download("punkt")
nltk.download("stopwords")

def extract_keywords_simple(description: str, max_keywords: int = 5) -> list[str]:
    tokens = word_tokenize(description.lower())
    stop_words = set(stopwords.words("russian"))
    keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
    return keywords[:max_keywords]"""
