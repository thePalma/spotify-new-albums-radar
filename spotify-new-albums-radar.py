#!/usr/bin/env python3

import os
import spotipy

# Useful function to split a list into chunks of n elements
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

# Load spotify environment variables
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
username = os.getenv('SPOTIFY_USERNAME')

# Login to the Spotify API
scope = 'user-library-read user-library-modify playlist-modify-public playlist-modify-private playlist-read-private'
token = spotipy.util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
sp = spotipy.Spotify(auth=token)

try:
    playlists:dict = sp.current_user_playlists(limit=50, offset=0)
    release_radar:dict = None

    # Find my Relead Radar playlist
    for playlist in playlists['items']:
        if playlist['name'] == 'Release Radar':
            release_radar = sp.playlist(playlist['id'])
            break
        if playlist['name'] == 'New Album Releases':
            # Delete the old New Album Releases playlist if it exists
            sp.user_playlist_unfollow(user=username, playlist_id=playlist['id'])

    if release_radar is None or release_radar['tracks']['total'] == 0:
        print('Release Radar playlist not found or empty')
        exit()

    new_album_releases = []

    for new_release in release_radar['tracks']['items']:
        # Assume that if the album has only one track, it's a single
        if new_release['track']['album']['total_tracks'] == 1:
            continue
        new_album_releases.append(new_release['track']['album'])

    if len(new_album_releases) == 0:
        print('No new album releases found')
        exit()

    # Remove duplicates from the list of new album releases
    new_album_releases = list({album['id']: album for album in new_album_releases}.values())

    # Print the new album releases
    print(f'{len(new_album_releases)} new albums released this week:\n')
    i = 1
    for album in new_album_releases:
        print(f'{i}:\t{album["artists"][0]["name"]} released "{album["name"]}" on {album["release_date"]}\n')
        i += 1

    tracks_to_add = []

    # Get all the tracks from the new album releases and save the URIs in a list
    for album in new_album_releases:
        album_tracks = sp.album_tracks(album_id=album['id'], limit=50, offset=0, market='US')
        for track in album_tracks['items']:
            tracks_to_add.append(track['uri'])

    # Split the list of tracks into chunks of 100 elements
    # Spotify API only allows to add 100 tracks at a time
    splitted_track_to_add = divide_chunks(tracks_to_add, 100)
    print('Creating New Album Releases playlist...')
    new_playlist = sp.user_playlist_create(user=username, name='New Album Releases', public=False)

    # Add the tracks to the new playlist
    print(f'Adding {len(tracks_to_add)} tracks to the playlist...')
    for tracks_uri in splitted_track_to_add:
        sp.playlist_add_items(new_playlist['id'], tracks_uri)
except Exception as e:
    print(f'Error: {e}')
    exit()