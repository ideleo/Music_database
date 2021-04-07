from google.cloud import ndb
from google.cloud import datastore
from flask import Flask

from ivanomusic import models
from ivanomusic import backend
from ivanomusic import helper

app = Flask(__name__)
app.secret_key = "keyboard"

@app.route("/" , methods = ['GET', 'POST'])
def base_route():
    return backend.music_db_login()

@app.route("/music" , methods = ['GET', 'POST'])
def music():
    return backend.music()

@app.route("/music_input" , methods = ['GET', 'POST'])
def music_input():
    return backend.music_input()

@app.route("/music_db_login" , methods = ['GET', 'POST'])
def music_db_login():
    return backend.music_db_login()

@app.route("/music_my_user" , methods = ['GET', 'POST'])
def music_my_user():
    return backend.music_my_user()

@app.route("/music_users" , methods = ['GET', 'POST'])
def music_users():
    return backend.music_users()


#if __name__ == "__main__":
 #   app.run()

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]

