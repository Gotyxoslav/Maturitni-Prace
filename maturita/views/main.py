from flask import Flask, request, render_template, redirect, session, url_for, make_response, jsonify, abort
import uuid
import os
import json

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from sql import get_data, add_data, del_data, update_data, get_joined_data

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "data")

app = Flask(__name__)
app.config["SECRET_KEY"] = "123456789"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "tajnyklic"

ph = PasswordHasher()

def generate_id():
    return str(uuid.uuid4())

def render_page(page_name, **kwargs):
    if request.headers.get("HX-Request"):
        return render_template(page_name, **kwargs) # if I get it right, **kwargs is generally for any number Keyword Arguments (so like songs=songs)
    else:
        return render_template("base.html", page_name=page_name, **kwargs)
    


@app.route('/')
def index():
    songs = get_data("MATURITA_HOL_SONGS")
    return render_page("index.html", songs=songs)

# --- Explore ---
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
    user = session["user"]

    # makes a dictionary where each id coresponds to an username
    users = get_data("MATURITA_HOL_USERS") 
    names = {u["id"]: u["username"] for u in users}
    
    #tohle projede playlisty aby to našlo to id
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


@app.route('/make-playlist', methods=["POST"])
def make_playlist():
    name = request.form.get("name")
    author = session.get("user")
    description = request.form.get("description")

    playlist_id = generate_id()

    if name == "" or name.isspace():
        name = "My playlist"

    playlistfile = request.files.get("playlistfile")
    if playlistfile and playlistfile.filename.endswith((".png", ".jpg",".jpeg")):
        filename = playlist_id + ".png"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"] + "/playlists", filename)
        playlistfile.save(filepath)

        add_data("MATURITA_HOL_PLAYLISTS", {
            "id": playlist_id,
            "author": author,
            "name": name,
            "description": description,
            "playlistfile": f"../static/data/playlists/{filename}"
        })

    else:
        add_data("MATURITA_HOL_PLAYLISTS", {
            "id": playlist_id,
            "author": author,
            "name": name,
            "description": description
        })

    return redirect(url_for("library"))

@app.route('/update-playlist', methods=["POST"])
def update_playlist():
    playlist_id = request.form.get("playlist")
    name = request.form.get("name")
    description = request.form.get("description")

    if not name or name.isspace():
        name = "My playlist"

    playlistfile = request.files.get("playlistfile")

    if playlistfile and playlistfile.filename != "" and playlistfile.filename.endswith((".png", ".jpg",".jpeg")):
        filename = playlist_id + ".png"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], "playlists", filename)
        playlistfile.save(filepath)

        update_data("MATURITA_HOL_PLAYLISTS", {
            "name": name,
            "description": description,
            "playlistfile": f"../static/data/playlists/{filename}"
        }, playlist_id)
        
    else:
        update_data("MATURITA_HOL_PLAYLISTS", {
            "name": name,
            "description": description
        }, playlist_id)

    return redirect(url_for("playlists", playlist_id=playlist_id))

@app.route('/del-playlist', methods=["POST"])
def del_playlist():
    id = request.args.get("id")

    filename = id + ".png"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], "playlists", filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    del_data("MATURITA_HOL_PLAYLISTS", {
        "id": id
    })

    del_data("MATURITA_HOL_PLAYLIST_SONGS", {
        "playlist_id": id
    })

    return redirect(url_for("library"))

@app.route('/add-to-playlist', methods=["POST"])
def add_to_playlist():
    playlist_id = request.form.get("playlist")
    song_id = request.form.get("song")

    song_playlists = get_data("MATURITA_HOL_PLAYLIST_SONGS")

    placement = 1 # Finds the highest placement number currently in use
    for relation in song_playlists:
        if relation.get("playlist_id") == playlist_id:
            if relation.get("placement", 0) >= placement:
                placement = relation.get("placement") + 1

    add_data("MATURITA_HOL_PLAYLIST_SONGS", {
        "playlist_id": playlist_id,
        "song_id": song_id,
        "placement": placement
    })

    return redirect(request.referrer)

@app.route('/del-from-playlist', methods=["POST"])
def del_from_playlist():
    id = request.args.get("id")
    placement = int(request.args.get("placement"))

    playlist_songs = get_joined_data(
        "MATURITA_HOL_PLAYLIST_SONGS", 
        "MATURITA_HOL_SONGS", 
        "song_id", 
        "song_id", 
        "playlist_id", 
        id
    )

    # sorts playlist by placement
    playlist_songs = sorted(playlist_songs, key=lambda x: x.get("placement", 0))

    del_data("MATURITA_HOL_PLAYLIST_SONGS", {"playlist_id": id})

    new_placement = 1
    
    for song in playlist_songs:
        # if it's the song we deleted, it ignores it
        if int(song["placement"]) == placement:
            continue 
        
        # Otherwise, save it back with the new placement
        add_data("MATURITA_HOL_PLAYLIST_SONGS", {
            "playlist_id": id,
            "song_id": song["song_id"],
            "placement": new_placement
        })
        new_placement += 1

    return redirect(url_for("playlists", playlist_id=id))

# --- Profile ---
@app.route("/profile/<id>")
def profile(id):
    users = get_data("MATURITA_HOL_USERS")

    #looks through users to find ID
    user = next((user for user in users if user['id'] == id), None)
    return render_page("profile.html", user=user)

@app.route("/update-profile", methods=["POST"])
def update_profile():
    user_id = request.form.get("user")
    name = request.form.get("name")
    description = request.form.get("description")

    pfpfile = request.files.get("pfp")

    if name == "" or name.isspace():
        name = "User123"

    if pfpfile:
        filename = user_id + ".png"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"] + "/pfp", filename)
        pfpfile.save(filepath)

        update_data("MATURITA_HOL_USERS", {
                "username": name,
                "pfp": f"../static/data/pfp/{filename}",
                "description": description
            }, user_id)
    else:
        update_data("MATURITA_HOL_USERS", {
                "username": name,
                "description": description
            }, user_id)
    
    return redirect(url_for("profile", id=user_id))

# --- Explore ---
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
    user = session["user"]

    users = get_data("MATURITA_HOL_USERS") 
    names = {u["id"]: u["username"] for u in users}

    #tohle projede alba aby to našlo to id
    album = next((album for album in albums if album['album_id'] == id), None)

    if album == None:
        return render_page("404.html") 

    return render_page("album.html", album=album, songs=songs, user=user, playlists=playlists, names=names)



# --- Song Management ---

@app.route('/manage-song')
def manage_song():
    if "user" in session:
        role = session["role"]
    
        if role == 1 or role == 2:
            albums = get_data("MATURITA_HOL_ALBUMS")
            albums = sorted(albums, key=lambda x: x["title"])

            songs = get_data("MATURITA_HOL_SONGS")
            songs = sorted(songs, key=lambda x: x["title"])

            users = get_data("MATURITA_HOL_USERS")
            names = {u['id']: u['username'] for u in users} # makes a dictionary where it gives id to username (so like {"sa5d4w5f2a": "user14", "frge5f1ss5f": "musicguy5"})

            return render_page("add_music.html", albums=albums, names=names, songs=songs)
        
    else:
        return redirect(url_for("index"))

@app.route('/add-album', methods=["POST"])
def add_album():
    title = request.form.get("title")
    author = session.get("user")
    release = request.form.get("release")

    albumfile = request.files["albumfile"]
    if albumfile.filename.endswith((".png", ".jpg",".jpeg")):
        album_id = generate_id()
        filename = album_id + ".png"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"] + "/albums", filename)
        albumfile.save(filepath)

        add_data("MATURITA_HOL_ALBUMS", {
            "album_id": album_id,
            "title": title,
            "author": author,
            "release_date": release,
            "albumfile": f"../static/data/albums/{filename}"
        })

        return redirect(url_for("index"))
    else:
        return redirect(url_for("manage_song"), error="Incorrect album file, use .png, .jpg or .jpeg")
    
@app.route('/del-album', methods=["POST"])
def del_album():
    id = request.form.get("id")
    songs = get_data("MATURITA_HOL_SONGS")
    albums = get_data("MATURITA_HOL_ALBUMS")

    for song in songs:
        if "album" in song and song["album"] == id:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], song['songfile'])
            if os.path.exists(filepath):
                os.remove(filepath)

    for album in albums:
        if "album_id" in album and album["album_id"] == id: # if "album_id" in album just checks if album_id even exists
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], album['albumfile'])
            if os.path.exists(filepath):
                os.remove(filepath)

    del_data("MATURITA_HOL_SONGS", {
        "album": id
    })
    del_data("MATURITA_HOL_ALBUMS", {
        "album_id": id
    })

    return redirect(url_for("index"))

@app.route('/add-song', methods=["POST"])
def add_song():
    title = request.form.get("title")
    author = session.get("user")
    album = request.form.get("album")

    songfile = request.files["songfile"]
    if songfile.filename.endswith(".mp3"):
        song_id = generate_id()

        filename = song_id + ".mp3"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"] + "/songs", filename)
        songfile.save(filepath)
        
        add_data("MATURITA_HOL_SONGS", {
            "song_id": song_id,
            "title": title,
            "author": author,
            "album": album,
            "songfile": f"songs/{filename}"
        })

        return redirect(url_for("index"))
    else:
        return redirect(url_for("manage_song"), error="Incorrect audio file, use .mp3")
    
@app.route('/del-song', methods=["POST"])
def del_song():
    id = request.form.get("id")
    songs = get_data("MATURITA_HOL_SONGS")

    for song in songs:
        if "song_id" in song and song["song_id"] == id:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], song['songfile'])
            if os.path.exists(filepath):
                os.remove(filepath)

    del_data("MATURITA_HOL_SONGS", {
        "song_id": id
    })

    return redirect(url_for("index"))

# --- Login ---

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        id = generate_id()

        users = get_data("MATURITA_HOL_USERS")
        for u in users:
            if u["email"] == email:
                return redirect(url_for("login"))

        add_data("MATURITA_HOL_USERS", {
            "username": username,
            "email": email,
            "password": ph.hash(password),
            "id": id
        })
        return redirect(url_for("login"))

    return render_page("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        users = get_data("MATURITA_HOL_USERS")
        for u in users:
            if u["email"] == email:
                try:
                    if ph.verify(u["password"], password):
                        session["user"] = u["id"]
                        session["role"] = u["role"]
                        return redirect(url_for("index"))
                except VerifyMismatchError: # without this, it would spit out an error
                    pass

        return render_page("login.html", error="Incorrect e-mail or password")

    return render_page("login.html")

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "user" in session:
        session.pop("user", None)
        session.pop("role", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)