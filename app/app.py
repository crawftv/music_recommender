from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
from annoy import AnnoyIndex
import boto3
from decouple import config
def create_app():
    app = Flask(__name__)

    b = AnnoyIndex(200) 
    b.load("../songs.ann")
    
    	   
 
    @app.route('/')
    def root():
        return render_template('root.html')

    @app.route('/search', methods = ["GET"])
    def search():
        search = request.values["search"]
        return make_playlist(search)

    return app

def make_playlist(search):
    query = es.search(
        index="song-index", body={"query": {"match": {"song-identifier": search}}}
    )["hits"]["hits"][0]["_source"]["annoy-id"]
    query = b.get_nns_by_item(q[0]["annoy-id"], 10)
    return list(
        map(
            lambda x: es.get(index="song-index", doc_type="song-doc", id=x)["_source"][
                "song-identifier"
            ],
            query,
        )
    )
