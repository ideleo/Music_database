#By Ivano

import os
import datetime
import json
import hashlib

from google.cloud import ndb
from google.cloud import datastore
from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from google.cloud import storage

class Ivanomusic_presets():
    app_name            = "ivanomusic"
    today_date          = ""
    today_time          = ""
    msg_type            = ""
    error_msg_1         = ""


class Templates():
    music_menu          = "music_db.html"
    music_input         = "music_input.html"
    music_db_login      = "music_db_login.html"
    music_my_user       = "music_my_user.html"
    music_users         = "music_users.html"



def Ivano_date(option, data=""):
    local_datenow = datetime.datetime.now()
    local_datenow = local_datenow + datetime.timedelta(hours=1)
    
    local_date = str(local_datenow).split(" ")[0]
    local_time = str(local_datenow).split(" ")[1]
    local_date = local_date.split("-")[2] + "/" + local_date.split("-")[1] + "/" + local_date.split("-")[0]
    local_time = local_time.split(":")[0] + ":" + local_time.split(":")[1]

    if option == "date":
        return local_date
    if option == "time":
        return local_time

    if option == "check":
        try:
            x = datetime.datetime.strptime(data, "%d/%m/%Y")
            return "valid"
        except:
            return "invalid"
    return local_datenow

