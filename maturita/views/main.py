import os
from flask import Flask

from backend.routes_auth import init_auth
from backend.routes_explore import init_explore
from backend.routes_manage import init_manage

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "data")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "8f92j65d4fsfoiuilsfdsd533"

# adds app cuz without it, it won't work, the files don't know what app is and something like "@app.route('/login')" will result in python saying that app is not defined
init_auth(app) # all pages related to authentication (login, register, logout)
init_explore(app) # all pages related to displaying data to the user (library, playlist, albums, ...)
init_manage(app) # all pages related to modifying database and saving data (delete playlist, add song, edit album, ...)

if __name__ == "__main__":
    app.run(debug=True)