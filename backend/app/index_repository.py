import os
from typing import Optional

from pymongo import MongoClient


class IndexRepository:
    def __init__(self) -> None:
        self.db = MongoClient(os.getenv('MONGO_URL', 'mongodb://root:root@localhost:27017')).admin
        self.n_docs = 0

    def find(self, t: str) -> Optional[dict]:
        cursor = self.db.index.find({'t': t})
        return cursor[0] if cursor.count() != 0 else None

    def docs_count(self) -> int:
        if self.n_docs == 0:
            cursor = self.db.index.find({'id': 'N'})
            if cursor.count() != 0:
                self.n_docs = cursor[0]['N']

        return self.n_docs
