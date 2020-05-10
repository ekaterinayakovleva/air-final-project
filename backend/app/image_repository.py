import os

from pymongo import MongoClient

Image = dict


class ImageRepository:
    def __init__(self) -> None:
        self.db = MongoClient(os.getenv('MONGO_URL', 'mongodb://root:root@localhost:27017')).admin

    def describe(self, ids: [int]) -> [Image]:
        return list(self.db.images.find({'id': {'$in': ids}}))
