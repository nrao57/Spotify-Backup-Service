import requests
import json
import os
import base64


def base64_encode(client_id, client_secret):
    return base64.b64encode(f"{client_id}:{client_secret}".encode('utf-8'))

def get_access_token():
    url = "https://accounts.spotify.com/api/token"

    payload='grant_type=client_credentials'
    headers = {
        'Authorization': 'Basic ' + base64_encode(os.environ['SPOTIFY_CLIENT_ID'], os.environ['SPOTIFY_CLIENT_SECRET']),
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()['access_token']

def get_access_token_headers(access_token):
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }


def get_user_playlist(access_token_headers):
    url = f"https://api.spotify.com/v1/users/{os.environ['USER_ID']}/playlists"
    response = requests.request("GET", url, headers=access_token_headers, data="")
    return response.json()


def get_playlist_data(access_token_headers, playlist_id, next=None):
    if next:
        url = next
    else:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}?fields=tracks.items(track(name,album(name),id,artists(name))),tracks.next"
    
    response = requests.request("GET", url, headers=access_token_headers, data={})
    data = response.json()
    return data, data['tracks']['next']


all_data = {}
# loop through all playlists and get the tracks
token_header = get_access_token_headers(get_access_token())
playlists_data = get_user_playlist(access_token_headers=get_access_token_headers(token_header))
for playlist in playlists_data['items']:
    next = None
    while(True):
        playlist_data, next = get_playlist_data( get_access_token_headers(token_header), playlist['id'], next)
        all_data[playlist['name']] = playlist_data
        if not next:
            break
    
print(all_data)