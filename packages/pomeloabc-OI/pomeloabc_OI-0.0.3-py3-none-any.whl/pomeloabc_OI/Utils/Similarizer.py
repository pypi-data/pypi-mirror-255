from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def text_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    corpus = [text1, text2]
    vectors = vectorizer.fit_transform(corpus)
    similarity = cosine_similarity(vectors)
    return round(similarity[0][1] * 100, 2)

def file_similarity(file1name, file2name):
    text1 = open("./{}".format(file1name), "r").read()
    text2 = open("./{}".format(file2name), "r").read()

    return text_similarity(text1, text2)