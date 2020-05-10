import pickle
from collections import Counter

import nltk
import numpy as np
import math
from joblib import load
from numpy import linalg as la

from sklearn.metrics.pairwise import cosine_similarity

# noinspection PyUnresolvedReferences
from index_repository import IndexRepository


def norm_vectors(data):
    return np.asarray([a / la.norm(a) for a in data.copy()])


class Inference:
    def __init__(self, pca_path, tdm_path, t2id_path) -> None:
        self.pca = load(pca_path)
        with open(tdm_path, 'rb') as f:
            self.tdm = norm_vectors(pickle.load(f))
        self.t2id = load(t2id_path)
        self.index_repo = IndexRepository()
        self.stemmer = nltk.PorterStemmer()

    def process_query(self, raw_query: str) -> [int]:
        vec = self.__query_vec(raw_query)
        if vec is None:
            return []
        q_vec = norm_vectors(self.pca.transform(vec))
        closest = self.__find_k_closest(q_vec)
        return list(map(lambda x: x[0], closest))

    def __find_k_closest(self, query, k=5):
        c = cosine_similarity(query.reshape(-1, self.pca.n_components), self.tdm)
        cosi = [(it, self.tdm[it], c[0, it]) for it in range(len(c[0]))]
        cosi.sort(key=lambda tup: tup[2], reverse=True)
        return cosi[:k]

    def __query_vec(self, raw_query):
        query = Counter(self.__preprocess(raw_query))
        vector = np.zeros((1, len(self.t2id)), dtype=float)
        n_docs = self.index_repo.docs_count()

        touched = False
        for q in query:
            data = self.index_repo.find(q)
            if not data:
                continue
            touched = True
            vector[0, self.t2id[q]] = query[q] * math.log10(n_docs / len(data['data'][1:]))
        return vector if touched else None

    def __preprocess(self, text):
        return [self.stemmer.stem(word.lower()) for word in nltk.word_tokenize(text) if word.isalpha()]
