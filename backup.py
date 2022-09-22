import requests
import json
import os
import base64
import datetime
import sqlite3


def base64_encode(client_id, client_secret):
    return base64.b64encode(f"{client_id}:{client_secret}".encode('utf-8')).decode("utf-8") 

def get_access_token():
    url = "https://accounts.spotify.com/api/token"
    creds = base64_encode(os.environ['SPOTIFY_CLIENT_ID'], os.environ['SPOTIFY_CLIENT_SECRET'])
    payload='grant_type=client_credentials'
    headers = {
        'Authorization': f'Basic {creds}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()['access_token']

def get_access_token_headers(access_token):
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }


def get_user_playlist(access_token_headers):
    url = f"https://api.spotify.com/v1/users/{os.environ['USER_ID']}/playlists"
    response = requests.request("GET", url, headers=access_token_headers, data="")
    return response.json()


def get_playlist_data(access_token_headers, playlist_id, next=None):
    if next:
        url = next
    else:
        field_filter = "?fields=tracks.items(track(name,album(name),id,artists(name),uri)),tracks.next"
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}" + field_filter
    
    response = requests.request("GET", url, headers=access_token_headers, data={})
    data = response.json()
    if data:
        if data.get('tracks', {}).get('items'):
            return data['tracks']['items'], data['tracks']['next']
        else:
            return data['items'], data['next']
    else:
        print(f"no data returned for playlist_id {playlist_id}")


def write_data_to_file(filename, data_dict):
    with open(filename, 'w') as f:
     json.dump(data_dict, f)


def create_table(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS TRACK
         (id integer primary key autoincrement,
         album_name           TEXT    NOT NULL,
         track_name           TEXT    NOT NULL,
         playlist_name        TEXT NOT NULL,
         spotify_id           TEXT,
         spotify_uri          TEXT);''')
    return


def load_data(tracks, today_date):
    conn = sqlite3.connect(f'spotify_backup_{today_date}.db')
    cur = conn.cursor()
    create_table(conn)
    for track in tracks:
        cur.execute(
            f"INSERT INTO TRACK (album_name,track_name,playlist_name,spotify_id,spotify_uri) VALUES (?, ?, ?, ?, ?)", 
            (
                track["album_name"], 
                track["track_name"], 
                track["playlist_name"], 
                track["spotify_id"],
                track["spotify_uri"]
            )
        )
        conn.commit()
    conn.close()


tracks = []
# loop through all playlists and get the tracks
token_header = get_access_token_headers(get_access_token())
playlists_data = get_user_playlist(access_token_headers=get_access_token_headers(token_header))
for playlist in playlists_data['items']:
    print(f"Getting tracks for playlist: {playlist['name']}")
    next = None
    while(True):
        playlist_tracks, next = get_playlist_data( get_access_token_headers(token_header), playlist['id'], next)
        for playlist_track in playlist_tracks:
            tracks.append(
                {
                    "playlist_name": playlist['name'], 
                    "album_name": playlist_track['track']['album']['name'], 
                    "track_name": playlist_track['track']['name'],
                    "spotify_id": playlist_track['track']['id'],
                    "spotify_uri": playlist_track['track']['uri']
                }
            )
        if not next:
            break

today_date = str(datetime.date.today())
# write_data_to_file(f"playlist_backup_{today_date}.json", all_data)
load_data(tracks, today_date)