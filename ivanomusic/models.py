#By Ivano

import os
import datetime
import json
import hashlib

from google.cloud import ndb
from google.cloud import datastore
from google.cloud import storage

from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import redirect

from ivanomusic.helper import Ivanomusic_presets
from ivanomusic.helper import Templates
from ivanomusic.helper import Ivano_date

class User(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    user_type = ndb.StringProperty()
    name = ndb.StringProperty()
    data_set = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class Genre(ndb.Model):
    data_set = ndb.StringProperty()
    music_type = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    
class Artist(ndb.Model):
    data_set = ndb.StringProperty()
    artist_name = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class Period(ndb.Model):
    data_set = ndb.StringProperty()
    period_name = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class Media(ndb.Model):
    data_set = ndb.StringProperty()
    media_type = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class Album(ndb.Model):
    data_set = ndb.StringProperty()
    genre = ndb.KeyProperty(kind = Genre)
    artist = ndb.KeyProperty(kind = Artist)
    period = ndb.KeyProperty(kind = Period)
    album_name = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class Position(ndb.Model):
    data_set = ndb.StringProperty()
    album = ndb.KeyProperty(kind = Album)
    media = ndb.KeyProperty(kind = Media)
    position = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

def Init():
    Ivanomusic_presets.today_date = Ivano_date("date")
    Ivanomusic_presets.today_time = Ivano_date("time")
    Ivanomusic_presets.msg_type = request.method
    Ivanomusic_presets.error_msg_1 = ""
    if "username" in session:
        if session["username"] != "":
            return 0
    return -1
    
