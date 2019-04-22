from flask import Flask, render_template, request
import pickle
from fuzzywuzzy import process
from annoy import AnnoyIndex


def create_app():
    app = Flask(__name__)
    filename = "songs_df"
    infile = open(filename,"rb")
    songs1 = pickle.load(infile)
    infile.close()
    u = AnnoyIndex(300)
    u.load('app/songs.ann')


    @app.route('/')
    def root():

        return render_template('root.html')
    @app.route('/search', methods = ["GET"])

    def search():
        search = request.values["search"]
        search = process.extractOne(search, songs1["song_artist"])[2]
        playlist = u.get_nns_by_item(search,10)
        playlist = [ songs1["url"][i] for i in playlist]
        return  render_template("search.html",playlist=playlist)

    return app
