import uuid
from flask import request, render_template

def generate_id():
    return str(uuid.uuid4())

def render_page(page_name, **kwargs):
    if request.headers.get("HX-Request"):
        return render_template(page_name, **kwargs) # **kwargs is generally for any number of Keyword Arguments (so like songs=songs)
    else:
        return render_template("base.html", page_name=page_name, **kwargs)

def init_errors(app):
    @app.errorhandler(404) 
    def not_found(e): 
        return render_page("404.html")