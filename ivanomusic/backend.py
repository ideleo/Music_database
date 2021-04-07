#import section

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

from ivanomusic.models import User
from ivanomusic.models import Genre
from ivanomusic.models import Artist
from ivanomusic.models import Period
from ivanomusic.models import Media
from ivanomusic.models import Album
from ivanomusic.models import Position
from ivanomusic.models import Init

from ivanomusic.helper import Ivanomusic_presets
from ivanomusic.helper import Templates
from ivanomusic.helper import Ivano_date


def music_db_login():
    Init()
    session["username"] = ""
    session["data_set"] = ""
    session["user_type"] = ""
    session["name"] = ""
    session["user_id"] = ""
    session["screen"] = "login"
    if Ivanomusic_presets.msg_type == "GET":
        return render_template(Templates.music_db_login,
                               ivanomusic_presets = Ivanomusic_presets
                               )
    local_username = request.values.get("username").lower()
    local_password = request.values.get("password")

    with ndb.Client().context():
        local_count = 0
        local_login = False
        for entry in User.query().fetch(1):
            local_count = 1
        if local_count == 0:
            if local_username == "admin":
                if local_password == "password":
                   local_login = True
                   session["username"] = "admin"
                   session["data_set"] = ""
                   session["user_type"] = "sys_admin"
                   session["name"] = "admin"
        else:
            for user in User.query(User.username == local_username).fetch():
                if user.password == hashlib.sha512(local_password.encode()).hexdigest():
                    local_login = True
                    session["username"] = user.username
                    session["data_set"] = user.data_set
                    session["user_type"] = user.user_type
                    session["name"] = user.name
                    session["user_id"] = user.key.id()
        if local_login == True:
            if session["user_type"] == "sys_admin":
                return redirect("/music_users")
            else:
                return redirect("/music?list=all")


        my_line = {"username" : local_username, "password" : local_password}      
        Ivanomusic_presets.error_msg_1 = "Invalid Username and/or password"
        return render_template(Templates.music_db_login,
                               ivanomusic_presets = Ivanomusic_presets,
                               my_line = my_line
                               )
                


        
        


def music_input():
    if Init() == -1:
        return redirect("/music_db_login")
    if Ivanomusic_presets.msg_type == "GET":
        return render_template(Templates.music_input,
                               ivanomusic_presets = Ivanomusic_presets
                               )
    local_album_name = request.values.get("album_name")
    local_music_type = request.values.get("music_type")
    local_artist_name = request.values.get("artist_name")
    local_period_name = request.values.get("period_name")
    local_media_type = request.values.get("media_type")
    local_position = request.values.get("position")
    local_edit = request.values.get("edit")
    local_edit_key = request.values.get("edit_key")
    

    with ndb.Client().context():
        if local_edit != None:
            if local_edit == "genre":
                genre = Genre.get_by_id(int(local_edit_key))
                if genre.music_type != local_music_type:
                    genre2 = None
                    for entry in Genre.query().filter(Genre.data_set == session["data_set"]).filter(Genre.music_type == local_music_type).fetch():
                        genre2 = entry
                    if genre2 == None:
                        genre.music_type = local_music_type
                        genre.put()
                    else:
                        for album in Album.query().filter(Album.data_set == session["data_set"]).filter(Album.genre == genre.key).fetch():
                            album.genre = genre2.key
                            album.put()
                        genre.key.delete()
                return redirect("/music?list=genre")
            if local_edit == "artist":
                artist = Artist.get_by_id(int(local_edit_key))
                if artist.artist_name != local_artist_name:
                    artist2 = None
                    for entry in Artist.query().filter(Artist.data_set == session["data_set"]).filter(Artist.artist_name == local_artist_name).fetch():
                        artist2 = entry
                    if artist2 == None:
                        artist.artist_name = local_artist_name
                        artist.put()
                    else:
                        for album in Album.query().filter(Album.data_set == session["data_set"]).filter(Album.artist == artist.key).fetch():
                            album.artist = artist2.key
                            album.put()
                        artist.key.delete()
                return redirect("/music?list=artist")
            if local_edit == "period":
                period = Period.get_by_id(int(local_edit_key))
                if period.period_name != local_period_name:
                    period2 = None
                    for entry in Period.query().filter(Period.data_set == session["data_set"]).filter(Period.period_name == local_period_name).fetch():
                        period2 = entry
                    if period2 == None:
                        period.period_name = local_period_name
                        period.put()
                    else:
                        for album in Album.query().filter(Album.data_set == session["data_set"]).filter(Album.period == period.key).fetch():
                            album.period = period2.key
                            album.put()
                        period.key.delete()
                return redirect("/music?list=period")
            if local_edit == "album":
                album = Album.get_by_id(int(local_edit_key))
                if album.album_name != local_album_name:
                    album2 = None
                    for entry in Album.query().filter(Album.data_set == session["data_set"]).filter(Album.album_name == local_album_name).fetch():
                        album2 = entry
                    if album2 == None:
                        album.album_name = local_album_name
                    else:
                        Ivanomusic_presets.error_msg_1 = "Album name already exists"
                        return render_template(Templates.music_input,
                                   ivanomusic_presets = Ivanomusic_presets,
                                   edit = local_edit,
                                   edit_key = local_edit_key,
                                   edit_entry = album,
                                   position = Position.query().fetch()
                                   ) 
                artist = album.artist.get()
                if artist.artist_name != local_artist_name:
                    artist = None
                    for entry in Artist.query().filter(Artist.data_set == session["data_set"]).filter(Artist.artist_name == local_artist_name).fetch():
                        artist = entry
                    if artist == None:
                        artist = Artist()
                        artist.data_set = session["data_set"]
                        artist.artist_name = local_artist_name
                        artist.put()
                album.artist = artist.key
                genre = album.genre.get()
                if genre.music_type != local_music_type:
                    genre = None
                    for entry in Genre.query().filter(Genre.data_set == session["data_set"]).filter(Genre.music_type == local_music_type).fetch():
                        genre = entry
                    if genre == None:
                        genre = Genre()
                        genre.data_set = session["data_set"]
                        genre.music_type = local_music_type
                        genre.put()
                album.genre = genre.key
                period = album.period.get()
                if period.period_name != local_period_name:
                    period = None
                    for entry in Period.query().filter(Period.data_set == session["data_set"]).filter(Period.period_name == local_period_name).fetch():
                        period = entry
                    if period == None:
                        period = Period()
                        period.data_set = session["data_set"]
                        period.period_name = local_period_name
                        period.put()
                album.period = period.key
                local_position_list = []
                for entry in local_position.strip().strip(",").split(','):
                    local_position_list.append(entry.strip(' '))
                local_media_type_list = []
                for entry in local_media_type.strip().strip(",").split(','):
                    local_media_type_list.append(entry.strip(' '))
                if len(local_position_list) != len(local_media_type_list):
                    Ivanomusic_presets.error_msg_1 = "You must enter the same number of entries in position and media"
                    return render_template(Templates.music_input,
                                   ivanomusic_presets = Ivanomusic_presets,
                                   edit = local_edit,
                                   edit_key = local_edit_key,
                                   edit_entry = album,
                                   position = Position.query().fetch()
                                   )
                
                local_position_work = []
                local_count = 0
                for position in Position.query().filter(Position.data_set == session["data_set"]).filter(Position.album == album.key).fetch():
                    if position.position in local_position_list:
                        local_position_work.append(position.position)
                        local_count = local_position_list.index(position.position)
                        local_position_media = position.media.get()
                        if local_position_media.media_type != local_media_type_list[local_count]:
                            media2 = None
                            for entry in Media.query().filter(Media.data_set == session["data_set"]).filter(Media.media_type == local_media_type_list[local_count]).fetch():
                                media2 = entry
                            if media2 == None:
                                media2 = Media()
                                media2.data_set = session["data_set"]
                                media2.media_type = local_media_type_list[local_count]
                                media2.put()
                            position.media = media2.key
                            position.put()
                    else:
                        position.key.delete()
                for local_position_entry in local_position_list:
                    if local_position_entry not in local_position_work:
                        position2 = None
                        for entry2 in Position.query().filter(Position.data_set == session["data_set"]).filter(Position.position == local_position_entry).fetch():
                            position2 = entry2
                        if position2 == None:
                            position2 = Position()
                            position2.data_set = session["data_set"]
                            position2.position = local_position_entry
                        position2.album = album.key
                        local_media_type_entry = local_media_type_list[local_position_list.index(local_position_entry)]
                        media2 = None
                        for entry in Media.query().filter(Media.data_set == session["data_set"]).filter(Media.media_type == local_media_type_entry).fetch():
                            media2 = entry
                        if media2 == None:
                            media2 = Media()
                            media2.data_set = session["data_set"]
                            media2.media_type = local_media_type_entry
                            media2.put()
                        position2.media = media2.key
                        position2.put()
                album.put()
                return redirect("/music?list=album")

            if local_edit == "media":
                media = Media.get_by_id(int(local_edit_key))
                if media.media_type != local_media_type:
                    media2 = None
                    for entry in Media.query().filter(Media.data_set == session["data_set"]).filter(Media.media_type == local_media_type).fetch():
                        media2 = entry
                    if media2 == None:
                        media.media_type = local_media_type
                        media.put()
                    else:
                        for position in Position.query().filter(Position.data_set == session["data_set"]).filter(Position.media == media.key).fetch():
                            position.media = media2.key
                            position.put()
                        media.key.delete()                
                return redirect("/music?list=media")

            if local_edit == "position":
                position = Position.get_by_id(int(local_edit_key))
                if position.position != local_position:
                    position2 = None
                    for entry in Position.query().filter(Position.data_set == session["data_set"]).filter(Position.position == local_position).fetch():
                        position2 = entry
                    if position2 == None:
                        position.position = local_position
                media = position.media.get()
                if media.media_type != local_media_type:
                    media2 = None
                    for entry in Media.query().filter(Media.data_set == session["data_set"]).filter(Media.media_type == local_media_type).fetch():
                        media2 = entry
                    if media2 == None:
                        media2 = Media()
                        media2.data_set = session["data_set"]
                        media2.media_type = local_media_type
                        media2.put()
                    position.media = media2.key
                album = position.album.get()
                if album.album_name != local_album_name:
                    album2 = None
                    for entry in Album.query().filter(Album.data_set == session["data_set"]).filter(Album.album_name == local_album_name).fetch():
                        album2 = entry
                    if album2 == None:
                        Ivanomusic_presets.error_msg_1 = "Album must exists - Use Input"
                        return render_template(Templates.music_input,
                                   ivanomusic_presets = Ivanomusic_presets,
                                   edit = local_edit,
                                   edit_key = local_edit_key,
                                   edit_entry = position
                                   )
                    position.album = album2.key                    
                position.put()
                return redirect("/music?list=position")



 

#Input  
        genre = None
        for music_type in Genre.query().filter(Genre.data_set == session["data_set"]).filter(Genre.music_type == local_music_type).fetch():
            genre = music_type
        if genre == None:
            genre = Genre()
            genre.data_set = session["data_set"]
            genre.music_type = local_music_type
            genre.put()
        artist = None
        for entry in Artist.query().filter(Artist.data_set == session["data_set"]).filter(Artist.artist_name == local_artist_name).fetch():
            artist = entry
        if artist == None:
            artist = Artist()
            artist.data_set = session["data_set"]
            artist.artist_name = local_artist_name
            artist.put()
        period = None
        for entry in Period.query().filter(Period.data_set == session["data_set"]).filter(Period.period_name == local_period_name).fetch():
            period = entry
        if period == None:
            period = Period()
            period.data_set = session["data_set"]
            period.period_name = local_period_name
            period.put()
        media = None
        for entry in Media.query().filter(Media.data_set == session["data_set"]).filter(Media.media_type == local_media_type).fetch():
            media = entry
        if media == None:
            media = Media()
            media.data_set = session["data_set"]
            media.media_type = local_media_type
            media.put()
        album = None
        for entry in Album.query().filter(Album.data_set == session["data_set"]).filter(Album.album_name == local_album_name).fetch():
            album = entry
        if album == None:
            album = Album()
            album.data_set = session["data_set"]
            album.genre = genre.key
            album.artist = artist.key
            album.period = period.key
            album.album_name = local_album_name
            album.put()
        position = None
        for entry in Position.query().filter(Position.data_set == session["data_set"]).filter(Position.position == local_position).fetch():
            position = entry
        if position == None:
            position = Position()
            position.data_set = session["data_set"]
        position.album = album.key
        position.media = media.key
        position.position = local_position
        position.put()
        return redirect("/music?list=all")

#Initialization
def music():
    if Init() == -1:
        return redirect("/music_db_login")      
    local_album_name = request.args.get("album_name")
    local_music_type = request.args.get("music_type")
    local_artist_name = request.args.get("artist_name")
    local_period_name = request.args.get("period_name")
    local_media_type = request.args.get("media_type")
    local_position = request.args.get("position")
    local_list = request.args.get("list")
    local_delete = request.args.get("delete")
    local_delete_type = request.args.get("delete_type")
    local_delete_key = request.args.get("delete_key")
    local_edit = request.args.get("edit")
    local_edit_key = request.args.get("edit_key")
    if "https" not in request.url:
        local_url = request.url.replace("http","https")
        return redirect(local_url)

#search section 
    with ndb.Client().context():
                   
        if request.args.get("search") != None:
            local_search = request.args.get("search")
            local_list = request.args.get("local_list")
            local_list = "position"
            return render_template(Templates.music_menu,
                                    ivanomusic_presets = Ivanomusic_presets, 
                                    genre = Genre.query(Genre.data_set == session["data_set"]).fetch(),
                                    artist = Artist.query(Artist.data_set == session["data_set"]).fetch(),
                                    period = Period.query(Period.data_set == session["data_set"]).fetch(),
                                    media = Media.query(Media.data_set == session["data_set"]).fetch(),
                                    position = Position.query(Position.data_set == session["data_set"]).fetch(),
                                    album = Album.query(Album.data_set == session["data_set"]).fetch(),
                                    local_list = local_list,
                                    search = local_search
                                   )
        
#delete section
        if local_delete_type != None:
            if local_delete_type == "genre":
                genre = Genre.get_by_id(int(local_delete_key))
                for album in Album.query(Album.genre == genre.key):
                    for position in Position.query(Position.album == album.key):
                        position.key.delete()                       
                    album.key.delete()
                genre.key.delete()
                return redirect("/music?list=genre")    
            if local_delete_type == "artist":
                artist = Artist.get_by_id(int(local_delete_key))
                for album in Album.query(Album.artist == artist.key):
                    for position in Position.query(Position.album == album.key):
                        position.key.delete()                       
                    album.key.delete()
                artist.key.delete()
                return redirect("/music?list=artist")
            if local_delete_type == "period":
                period = Period.get_by_id(int(local_delete_key))
                for album in Album.query(Album.period == period.key):
                    for position in Position.query(Position.album == album.key):
                        position.key.delete()                       
                    album.key.delete()
                period.key.delete()
                return redirect("/music?list=period")
        
            if local_delete_type == "media":
                media = Media.get_by_id(int(local_delete_key))
                for position in Position.query(Position.media == media.key):
                    position.key.delete()
                media.key.delete()
                return redirect("/music?list=media")
        
            if local_delete_type == "album":
                album = Album.get_by_id(int(local_delete_key))
                for position in Position.query(Position.album == album.key):
                    position.key.delete()
                album.key.delete()
                return redirect("/music?list=album")
            if local_delete_type == "position":
                position = Position.get_by_id(int(local_delete_key))
                position.key.delete()
                return redirect("/music?list=position")

#edit section
        if local_edit != None:
            if local_edit == "genre":
                edit_entry = Genre.get_by_id(int(local_edit_key))
            if local_edit == "artist":
                edit_entry = Artist.get_by_id(int(local_edit_key))
            if local_edit == "period":
                edit_entry = Period.get_by_id(int(local_edit_key))
            if local_edit == "album":
                edit_entry = Album.get_by_id(int(local_edit_key))
            if local_edit == "media":
                edit_entry = Media.get_by_id(int(local_edit_key))
            if local_edit == "position":
                edit_entry = Position.get_by_id(int(local_edit_key))
            return render_template(Templates.music_input,
                                   ivanomusic_presets = Ivanomusic_presets,
                                   edit = local_edit,
                                   edit_key = local_edit_key,
                                   edit_entry = edit_entry,
                                   position = Position.query().fetch()
                                   )

#list section
        
        if local_list != None:
            if local_list == "all":
                local_list = "genre"
            return render_template(Templates.music_menu,
                                   ivanomusic_presets = Ivanomusic_presets, 
                                   genre = Genre.query(Genre.data_set == session["data_set"]).fetch(),
                                   artist = Artist.query(Artist.data_set == session["data_set"]).fetch(),
                                   period = Period.query(Period.data_set == session["data_set"]).fetch(),
                                   media = Media.query(Media.data_set == session["data_set"]).fetch(),
                                   position = Position.query(Position.data_set == session["data_set"]).fetch(),
                                   album = Album.query(Album.data_set == session["data_set"]).fetch(),
                                   local_list = local_list
                                  )
        if local_list == "genre":
            local_text = "Genre <br/>"
            local_count = 0
            for genre in Genre.query().fetch():
                local_text = local_text + genre.music_type + str(Album.query(Album.genre == genre.key).count()) + "<br/>"
                for album in Album.query(Album.genre == genre.key):
                    local_text = local_text + " - " + album.album_name + "<br/>"
                    for position in Position.query(Position.album == album.key):
                        local_text = local_text + " ---- " + position.media.get().media_type + " - " + position.position + "<br/>"
                        local_count += 1
            return render_template("music_db.html",
                                  ivanomusic_presets = Ivanomusic_presets, 
                                  genre = Genre.query().fetch(),
                                  )
        if local_list == "artist":
            local_text = "Artist <br/>"
            local_count = 0
            for artist in Artist.query().fetch():
                local_text = local_text + artist.artist_name + "<br/>"
                for album in Album.query(Album.artist == artist.key):
                    local_text = local_text + " - " + album.album_name + "<br/>"
                    for position in Position.query(Position.album == album.key):
                        local_text = local_text + " ---- " + position.media.get().media_type + " - " + position.position + "<br/>"
                        local_count += 1
            return render_template("music_db.html",
                                   ivanomusic_presets = Ivanomusic_presets,
                                   artist = Artist.query().fetch(),
                                   )            
        if local_list == "period":
            local_text = "Period <br/>"
            local_count = 0
            for period in Period.query().fetch():
                local_text = local_text + period.period_name + "<br/>"
                for album in Album.query(Album.period == period.key):
                    local_text = local_text + " - " + album.album_name + "<br/>"
                    for position in Position.query(Position.album == album.key):
                        local_text = local_text + " ---- " + position.media.get().media_type + " - " + position.position + "<br/>"
                        local_count += 1
            return render_template("music_db.html",
                                   ivanomusic_presets = Ivanomusic_presets,
                                   period = Period.query().fetch(),
                                   )
        if local_list == "media":
            local_text = "Media <br/>"
            local_count = 0
            for media in Media.query().fetch():
                local_text = local_text + media.media_type + "<br/>"
                for position in Position.query(Position.media == media.key):
                    album = position.album.get()
                    genre = album.genre.get()
                    artist = album.artist.get()
                    period = album.period.get()
                    local_text = local_text + " - " + position.position + " - " + album.album_name + " - " + genre.music_type + " - " + artist.artist_name + " - " + period.period_name + "<br/>"
                    local_count += 1
            return render_template("music_db.html",
                                   ivanomusic_presets = Ivanomusic_presets,
                                   media = Media.query().fetch(),
                                   ) 
        if local_list == "position":
            local_text = "Position <br/>"
            local_count = 0
            for position in Position.query().order(Position.position).fetch():
                album = position.album.get()
                genre = album.genre.get()
                artist = album.artist.get()
                period = album.period.get()
                media = position.media.get()
                local_text = local_text + position.position + " - " + media.media_type + " - " + album.album_name + " - " + genre.music_type + " - " +artist.artist_name + " - " + period.period_name + "<br/>"
                local_count += 1
            return render_template("music_db.html",
                                   ivanomusic_presets = Ivanomusic_presets,
                                   position = Position.query().fetch(),
                                   ) 
        if local_list == "album":
            local_text = "Album <br/>"
            local_count = 0
            for album in Album.query().order(Album.album_name).fetch():
                artist = album.artist.get()
                genre = album.genre.get()
                period = album.period.get()
                if Position.query(Position.album == album.key).count() == 0:
                    local_text = local_text + album.album_name + "<br/>"
            local_text = local_text + "<br/>"
            for album in Album.query().order(Album.album_name).fetch():
                artist = album.artist.get()
                genre = album.genre.get()
                period = album.period.get()
                for position in Position.query(Position.album == album.key):
                    media = position.media.get()
                    local_text = local_text + album.album_name + " - " + media.media_type + " - " + position.position + "<br/>"
            return render_template("music_db.html",
                                   ivanomusic_presets = Ivanomusic_presets,
                                   album = Album.query().fetch(),
                                   )
        return redirect("/music?list=all")

def music_users():
    with ndb.Client().context():
        if Init() == -1:
            return redirect("/music_db_login")
        if Ivanomusic_presets.msg_type == "GET":
            local_count = 0
            user = None
            local_edit = request.args.get("edit")
            local_delete = request.args.get("delete")
            if local_delete != None:
                user = User.get_by_id(int(local_delete))
                user.key.delete()
                return redirect("music_users")
            users = User.query().fetch()
            for entry in User.query().fetch(1):
                local_count = 1
            if local_count == 1:
                if session["user_type"] == "sys_admin":
                    users = User.query().filter(User.user_type.IN(["sys_admin","admin"])).fetch()
                if session["user_type"] == "admin":
                    users = User.query(User.data_set == session["data_set"]).fetch()
                if local_edit != None:
                    user = User.get_by_id(int(local_edit))
            return render_template(Templates.music_users,
                                   ivanomusic_presets = Ivanomusic_presets,
                                   session = session,
                                   users = users,
                                   user = user
                                   )
        local_username = request.values.get("username").lower()
        local_password = request.values.get("password")
        local_name = request.values.get("name")
        local_user_type = request.values.get("user_type")
        local_key = request.values.get("key")
        

        if local_key != "":
            user = User.get_by_id(int(local_key))
            if user.username != local_username:
                Ivanomusic_presets.error_msg_1 = "Username cannot be changed"
                for entry in User.query().fetch(1):
                    local_count = 1
                if local_count == 1:
                    if session["user_type"] == "sys_admin":
                        users = User.query().filter(User.user_type.IN(["sys_admin","admin"])).fetch()
                    if session["user_type"] == "admin":
                        users = User.query(User.data_set == session["data_set"]).fetch()
                return render_template(Templates.music_users,
                                       ivanomusic_presets = Ivanomusic_presets,
                                       session = session,
                                       users = users,
                                       user = None
                                       )     
        else:
            user_exist = False
            for entry in User.query(User.username == local_username).fetch():
                user_exist = True
            if user_exist == True:
                Ivanomusic_presets.error_msg_1 = "User already exist"
                users = User.query().fetch()
                for entry in User.query().fetch(1):
                    local_count = 1
                if local_count == 1:
                    if session["user_type"] == "sys_admin":
                        users = User.query().filter(User.user_type.IN(["sys_admin","admin"])).fetch()
                    if session["user_type"] == "admin":
                        users = User.query(User.data_set == session["data_set"]).fetch()
                return render_template(Templates.music_users,
                                       ivanomusic_presets = Ivanomusic_presets,
                                       session = session,
                                       users = users,
                                       user = None
                                       )
                 
            user = User()
            if session["user_type"] == "sys_admin":
                if local_user_type == "admin":
                    user.data_set = local_username
                if local_user_type == "sys_admin":
                    user.data_set = ""
            if session["user_type"] == "admin":
                user.data_set = session["data_set"]
            user.username = local_username

        if local_password != None:
            user.password = hashlib.sha512(local_password.encode()).hexdigest()
        user.name = local_name
        user.user_type = local_user_type
        user.put()
        return redirect("/music_users")



def music_my_user():
    with ndb.Client().context():
        if Init() == -1:
            return redirect("/music_db_login")
        if Ivanomusic_presets.msg_type == "GET":
            user = User.get_by_id(int(session["user_id"]))
            return render_template(Templates.music_my_user,
                                   ivanomusic_presets = Ivanomusic_presets,
                                   session = session,
                                   user = user
                                   )
        local_current_password = request.values.get("current_password")
        local_new_password = request.values.get("new_password")
        local_confirm_password = request.values.get("confirm_password")
        user = User.get_by_id(int(session["user_id"]))
        if local_new_password != "":
            if local_new_password != local_confirm_password:
                Ivanomusic_presets.error_msg_1 = "New and confirm password are not the same"
            else:
                if user.password != hashlib.sha512(local_current_password.encode()).hexdigest():
                    Ivanomusic_presets.error_msg_1 = "Invalid current password"
                else:
                    user.password = hashlib.sha512(local_new_password.encode()).hexdigest()
                    user.put()
                    return redirect("/music?list=all")
            return render_template(Templates.music_my_user,
                                   ivanomusic_presets = Ivanomusic_presets,
                                   session = session,
                                   user = user
                                   )
        return redirect("/music?list=all")
                    



