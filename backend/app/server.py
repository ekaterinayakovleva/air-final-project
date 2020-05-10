#!/usr/bin/env python
import flask
from flask import Flask, request, jsonify

# noinspection PyUnresolvedReferences
from inference import Inference

# noinspection PyUnresolvedReferences
from image_repository import ImageRepository
from minio import Minio
from flask_cors import CORS
from waitress import serve
import os
import socket

app = Flask(__name__)
CORS(app)

inference = Inference(
    pca_path=os.getenv("PCA_PATH", '/fs/pca.p'),
    tdm_path=os.getenv("TDM_PATH", '/fs/tdm.p'),
    t2id_path=os.getenv("T2ID_PATH", '/fs/t2id.p')
)

image_repo = ImageRepository()

minio = Minio(os.getenv('MINIO_URL', 'localhost:9000'),
              access_key='minio',
              secret_key='minio123',
              secure=False)


def build_response(body, status):
    r = flask.make_response(body, status)
    r.headers['X-server-hostname'] = socket.gethostname()
    return r


@app.route("/", methods=['GET'])
def home():
    query = request.args.get('query')
    if query is None:
        return build_response('', 400)

    ids = inference.process_query(query)
    if len(ids) == 0:
        return build_response('', 404)

    body = jsonify([{
        'description': image['description'],
        'url': minio.presigned_get_object('images', image['name'])
    } for image in image_repo.describe(ids)])

    return build_response(body, 200)


if os.getenv("PROD", False):
    serve(app, host='0.0.0.0', port=8080)
else:
    app.run(debug=True)
