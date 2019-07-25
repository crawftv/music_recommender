from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
from annoy import AnnoyIndex
from decouple import config
import certifi

app = Flask(__name__)
b = AnnoyIndex(200)
b.load("songs.ann")


@app.route("/")
def root():
    return render_template("root.html")


@app.route("/search", methods=["GET"])
def search():
    search = request.values["search"]
    playlist = make_playlist(search)
    return render_template("search.html", playlist=playlist)


def make_playlist(search):
    es = Elasticsearch(
        config("ELASTIC_SEARCH_DOMAIN"),
        use_ssl=True,
        verify_certs=True,
        ca_certs=certifi.where(),
    )
    es_query = es.search(
        index="song-index", body={"query": {"match": {"song-identifier": search}}}
    )["hits"]["hits"][0]["_source"]["annoy-id"]

    q = [
        {
            "song-identifier": i["_source"]["song-identifier"],
            "annoy-id": i["_source"]["annoy-id"],
        }
        for i in es.search(
            index="song-index", body={"query": {"match": {"song-identifier": search}}}
        )["hits"]["hits"]
    ]
    annoy_query = b.get_nns_by_item(q[0]["annoy-id"], 10)

    playlist = list(
        map(
            lambda x: es.get(index="song-index", doc_type="song-doc", id=x)["_source"][
                "song-identifier"
            ],
            annoy_query,
        )
    )
    playlist = [
        {"identifier": i, "url": "https://genius.com/" + i + "-lyrics"}
        for i in playlist
    ]

    return playlist


if __name__ == "__main__":
    app.run(host="0.0.0.0")
