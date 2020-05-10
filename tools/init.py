#!/usr/bin/env python
import math
import os
import pickle
import time

from joblib import dump
from minio import Minio
from pymongo import MongoClient
import pandas as pd
import nltk

import numpy as np
from numpy import linalg as la
from sklearn.decomposition import PCA

nltk.download('punkt', quiet=True)


class Indexer:
    COLL_FREQ = "collection_frequency"

    def __init__(self):
        self.N = 0
        self.doc_urls = {}
        self.index = {}
        self.doc_lengths = {}
        self.stemmer = nltk.PorterStemmer()
        self.stopwords = set(nltk.corpus.stopwords.words('english'))

    def index_doc(self, doc, doc_id):
        ts = [word for word in nltk.word_tokenize(doc)]
        ts = [word for word in ts if word.isalpha()]
        ts = [self.stemmer.stem(word.lower()) for word in ts]

        self.populate_ii(doc_id, ts)
        self.doc_lengths[doc_id] = len(ts)
        self.N += 1

    def populate_ii(self, doc_id, ts):
        for t in ts:
            if self.index.get(t) is None:
                self.index[t] = {}
                self.index[t][self.COLL_FREQ] = 0

            doc_freq = self.index.get(t).get(doc_id)
            if doc_freq is None:
                self.index.get(t)[doc_id] = 0
            self.index.get(t)[doc_id] = self.index.get(t)[doc_id] + 1
            self.index.get(t)[self.COLL_FREQ] = self.index.get(t)[self.COLL_FREQ] + 1


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def norm_vectors(A):
    return np.asarray([a / la.norm(a) for a in A.copy()])


SEM_ART = os.environ['SEM_ART_PATH']
dfs = [pd.read_csv(filename, sep='\t', index_col=None, header=0, encoding='cp1252') for filename in
       list(map(lambda x: SEM_ART + x, ['semart_test.csv', 'semart_train.csv', 'semart_val.csv']))]

frame = pd.concat(dfs, axis=0, ignore_index=True)
indexer = Indexer()
for i, doc in frame.iterrows():
    indexer.index_doc(doc['DESCRIPTION'], i)

index = {t: list(d.items()) for t, d in indexer.index.items()}

mongo_url = os.getenv('MONGO_URL', 'mongodb://root:root@localhost:27017')
db = MongoClient(mongo_url).admin

if os.environ.get('MONGO_INSERT_INDEX'):
    print('updating index to mongo: {}'.format(mongo_url))
    db.index.delete_many({})

    for chunk in chunks(list(index.items()), 1000):
        db.index.insert_many([{'t': d[0], 'data': d[1]} for d in chunk])
        print("inserted {} index entries".format(len(chunk)))

    db.index.insert_one({'id': 'N', 'N': indexer.N})
else:
    print('\nSkipping index insert')

if os.environ.get('MONGO_INSERT_IMAGES'):
    print('updating images to mongo: {}'.format(mongo_url))
    db.images.delete_many({})

    for chunk in chunks(list(frame.iterrows()), 1000):
        db.images.insert_many([{
            'id': d[0],
            'description': d[1]['DESCRIPTION'],
            'name': d[1]['IMAGE_FILE']
        } for d in chunk])

        print("inserted {} image data".format(len(chunk)))
else:
    print('\nSkipping images data insert')

if os.environ.get('MINIO_UPLOAD'):
    start = time.time()
    client = Minio('localhost:9000',
                   access_key='minio',
                   secret_key='minio123',
                   secure=False)

    if not client.bucket_exists('images'):
        client.make_bucket('images')

    for filename in os.listdir(SEM_ART + 'images'):
        client.fput_object('images', filename, SEM_ART + 'images/' + filename)

    print('Minio upload took: {}'.format(time.time() - start))
else:
    print('\nSkipping images upload')

if os.environ.get('TDM'):
    docs_count = indexer.N
    doc_lengths = indexer.doc_lengths

    id2term = {t_id: term for t_id, term in enumerate(index.keys())}
    pca = PCA(n_components=1000)

    print("creating TDM")
    tdm = np.zeros((docs_count, len(index)), dtype=float)

    for t_id, term in id2term.items():
        postings = index[term][1:]
        idf = math.log10(docs_count / len(postings))
        for p in postings:
            tdm[p[0], t_id] = p[1]
        tdm[:, t_id] *= idf

    for i in range(tdm.shape[0]):
        tdm[i, :] /= doc_lengths[i] + 0.0001

    print("TDM has been created")
    tdm_t = pca.fit_transform(tdm)
    print("PCA has been fitted")

    with open('../local/fs/tdm.p', 'wb') as f:
        pickle.dump(tdm_t, f)
        print("TDM persisted")

    print("persisting PCA")
    dump(pca, '../local/fs/pca.p')
    print("PCA has been persisted")

    print("persisting T2ID")
    dump({term: t_id for t_id, term in id2term.items()}, '../local/fs/t2id.p')
    print("T2ID has been persisted")
else:
    print('\nSkipping TDM creation')
