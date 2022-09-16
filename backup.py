import requests
import json
import os

url = "https://accounts.spotify.com/api/token"

payload='grant_type=client_credentials'
headers = {
  'Authorization': 'Basic ' + os.environ['SPOTIFY_AUTH_CREDENTIALS'],
  'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.request("POST", url, headers=headers, data=payload)
access_token = response.json()['access_token']

url = f"https://api.spotify.com/v1/users/{os.environ['USER_ID']}/playlists"

payload = ""
access_token_headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + access_token
}

response = requests.request("GET", url, headers=access_token_headers, data=payload)
playlists_data = response.json()


def get_playlist_data(playlist_id, next=None):
    if next:
        url = next
    else:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}?fields=tracks.items(track(name,album(name),id,artists(name))),tracks.next"
    
    response = requests.request("GET", url, headers=access_token_headers, data={})
    data = response.json()
    return data, data['tracks']['next']


all_data = {}
# loop through all playlists and get the tracks
for playlist in playlists_data['items']:
    next = None
    while(True):
        playlist_data, next = get_playlist_data(playlist['id'], next)
        all_data[playlist['name']] = playlist_data
        if not next:
            break
    
print(all_data)