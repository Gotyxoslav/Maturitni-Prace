import os
from flask import request, redirect, session, url_for
from backend.sql import get_data, add_data, del_data, update_data, get_joined_data
from backend.utils import generate_id, render_page

def init_manage(app):

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
            }, "id", playlist_id)
        else:
            update_data("MATURITA_HOL_PLAYLISTS", {
                "name": name,
                "description": description
            }, "id", playlist_id)

        return redirect(url_for("playlists", playlist_id=playlist_id))

    @app.route('/del-playlist', methods=["POST"])
    def del_playlist():
        id = request.args.get("id")

        filename = id + ".png"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], "playlists", filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        del_data("MATURITA_HOL_PLAYLISTS", {"id": id})
        del_data("MATURITA_HOL_PLAYLIST_SONGS", {"playlist_id": id})

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
                }, "id", user_id)
        else:
            update_data("MATURITA_HOL_USERS", {
                    "username": name,
                    "description": description
                }, "id", user_id)
        
        return redirect(url_for("profile", id=user_id))

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
                names = {u['id']: u['username'] for u in users} 

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

    @app.route('/edit-album', methods=["POST"])
    def edit_album():
        album_id = request.form.get("id")
        title = request.form.get("title")
        release = request.form.get("release")
        
        albumfile = request.files.get("albumfile")
        
        if albumfile and albumfile.filename != "" and albumfile.filename.endswith((".png", ".jpg", ".jpeg")):
            filename = album_id + ".png"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"] + "/albums", filename)
            albumfile.save(filepath)
            
            update_data("MATURITA_HOL_ALBUMS", {
                "title": title,
                "release_date": release,
                "albumfile": f"../static/data/albums/{filename}"
            }, "album_id", album_id)
        else:
            update_data("MATURITA_HOL_ALBUMS", {
                "title": title,
                "release_date": release
            }, "album_id", album_id)

        return redirect(url_for("manage_song"))

    @app.route('/del-album', methods=["POST"])
    def del_album():
        id = request.form.get("id")
        songs = get_data("MATURITA_HOL_SONGS")
        albums = get_data("MATURITA_HOL_ALBUMS")

        for song in songs:
            if "album" in song and song["album"] == id:
                filepath = os.path.join(song['songfile'])
                if os.path.exists(filepath):
                    os.remove(filepath)

        for album in albums:
            if "album_id" in album and album["album_id"] == id: 
                album_name = os.path.basename(album['albumfile']) # gets the pure filename without path
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], "albums", album_name)
                print(filepath)
                if os.path.exists(filepath):
                    print("found!")
                    os.remove(filepath)

        del_data("MATURITA_HOL_SONGS", {"album": id})
        del_data("MATURITA_HOL_ALBUMS", {"album_id": id})

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

    @app.route('/edit-song', methods=["POST"])
    def edit_song():
        song_id = request.form.get("id")
        title = request.form.get("title")
        album = request.form.get("album")
        
        songfile = request.files.get("songfile")
        
        if songfile and songfile.filename != "" and songfile.filename.endswith(".mp3"):
            filename = song_id + ".mp3"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"] + "/songs", filename)
            songfile.save(filepath)
            
            update_data("MATURITA_HOL_SONGS", {
                "title": title,
                "album": album,
                "songfile": f"songs/{filename}"
            }, "song_id", song_id)
        else:
            update_data("MATURITA_HOL_SONGS", {
                "title": title,
                "album": album
            }, "song_id", song_id)

        return redirect(url_for("manage_song"))

    @app.route('/del-song', methods=["POST"])
    def del_song():
        id = request.form.get("id")
        songs = get_data("MATURITA_HOL_SONGS")

        for song in songs:
            if "song_id" in song and song["song_id"] == id:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], song['songfile'])
                if os.path.exists(filepath):
                    os.remove(filepath)

        del_data("MATURITA_HOL_SONGS", {"song_id": id})

        return redirect(url_for("index"))