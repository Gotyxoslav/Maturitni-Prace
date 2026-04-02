from flask import request, redirect, session, url_for
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from backend.sql import get_data, add_data
from backend.utils import generate_id, render_page

ph = PasswordHasher()

def init_auth(app):
    
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