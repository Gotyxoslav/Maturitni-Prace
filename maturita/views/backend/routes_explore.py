from flask import session, redirect, url_for
from backend.sql import get_data, get_joined_data
from backend.utils import render_page

def init_explore(app):
    
    @app.route('/')
    def index():
        songs = get_data("MATURITA_HOL_SONGS")
        albums = get_data("MATURITA_HOL_ALBUMS")
        playlists = get_data("MATURITA_HOL_PLAYLISTS") 
        
        # makes a dictionary where each id coresponds to an username
        users = get_data("MATURITA_HOL_USERS") 
        names = {u["id"]: u["username"] for u in users}
        
        return render_page("index.html", songs=songs, albums=albums, playlists=playlists, names=names)

    @app.route('/library')
    def library():
        if "user" in session:
            user = session["user"]
            playlists = get_data("MATURITA_HOL_PLAYLISTS")
            return render_page("library.html", user=user, playlists=playlists)
        else:
            return redirect(url_for("login"))
        
    @app.route("/playlist/<playlist_id>")
    def playlists(playlist_id):
        playlists = get_data("MATURITA_HOL_PLAYLISTS")
        
        # Using .get() prevents the crash if no user is logged in
        user = session.get("user")

        users = get_data("MATURITA_HOL_USERS") 
        names = {u["id"]: u["username"] for u in users}
        
        # this loops through the playlists to find the matching id
        playlist = next((playlist for playlist in playlists if playlist['id'] == playlist_id), None)

        songs = get_joined_data(
            table1 = "MATURITA_HOL_SONGS", 
            table2 = "MATURITA_HOL_PLAYLIST_SONGS", 
            key1 = "song_id",
            key2 = "song_id",
            condition_column = "playlist_id", 
            condition_value = playlist_id 
        )

        return render_page("playlist.html", playlist=playlist, user=user, songs=songs, playlists=playlists, names=names)

    @app.route("/profile/<id>")
    def profile(id):
        users = get_data("MATURITA_HOL_USERS")
        playlists = get_data("MATURITA_HOL_PLAYLISTS")

        # looks through users to find ID
        user = next((user for user in users if user['id'] == id), None)
        return render_page("profile.html", user=user, playlists=playlists)

    @app.route('/explore')
    def explore():
        songs = get_data("MATURITA_HOL_SONGS")
        albums = get_data("MATURITA_HOL_ALBUMS")

        users = get_data("MATURITA_HOL_USERS") 
        names = {u["id"]: u["username"] for u in users}

        return render_page("explore.html", albums=albums, songs=songs, names=names)

    @app.route("/album/<id>")
    def albums(id):
        albums = get_data("MATURITA_HOL_ALBUMS")
        songs = get_data("MATURITA_HOL_SONGS")
        playlists = get_data("MATURITA_HOL_PLAYLISTS")
        
        user = session.get("user")

        users = get_data("MATURITA_HOL_USERS") 
        names = {u["id"]: u["username"] for u in users}

        # this loops through the albums to find the matching id
        album = next((album for album in albums if album['album_id'] == id), None)

        if album == None:
            return render_page("404.html") 

        return render_page("album.html", album=album, songs=songs, user=user, playlists=playlists, names=names)