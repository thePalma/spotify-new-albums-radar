#!/usr/bin/env python3

import os
import spotipy

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
username = os.getenv('SPOTIFY_USERNAME')

scope = 'user-library-read user-library-modify playlist-modify-public playlist-modify-private playlist-read-private'

token = spotipy.util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)

sp = spotipy.Spotify(auth=token)

try:
    playlists:dict = sp.current_user_playlists(limit=50, offset=0)
    release_radar:dict = None

    for playlist in playlists['items']:
        if playlist['name'] == 'Release Radar':
            release_radar = sp.playlist(playlist['id'])
            break
        if playlist['name'] == 'New Album Releases':
            sp.user_playlist_unfollow(user=username, playlist_id=playlist['id'])

    if release_radar is None or release_radar['tracks']['total'] == 0:
        print('Release Radar playlist not found or empty')
        exit()

    new_album_releases = []

    for new_release in release_radar['tracks']['items']:
        if new_release['track']['album']['total_tracks'] == 1:
            continue
        new_album_releases.append(new_release['track']['album'])

    tracks_to_add = []

    for album in new_album_releases:
        album_tracks = sp.album_tracks(album_id=album['id'], limit=50, offset=0, market='US')
        for track in album_tracks['items']:
            tracks_to_add.append(track['uri'])

    splitted_track_to_add = divide_chunks(tracks_to_add, 100)
    new_playlist = sp.user_playlist_create(user=username, name='New Album Releases', public=False)

    for tracks_uri in splitted_track_to_add:
        sp.playlist_add_items(new_playlist['id'], tracks_uri)
except Exception as e:
    print(f'Error: {e}')
    exit()