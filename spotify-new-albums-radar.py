#!/usr/bin/env python3

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Useful function to split a list into chunks of n elements
def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

# Load environment variables
def load_env_variables():
    return {
        'client_id': os.getenv('SPOTIPY_CLIENT_ID'),
        'client_secret': os.getenv('SPOTIPY_CLIENT_SECRET'),
        'redirect_uri': os.getenv('SPOTIPY_REDIRECT_URI'),
        'username': os.getenv('SPOTIFY_USERNAME')
    }

# Authenticate with Spotify API
def authenticate_spotify(env_vars):
    scope = 'user-library-read user-library-modify playlist-modify-public playlist-modify-private playlist-read-private'
    auth_manager = SpotifyOAuth(
        client_id=env_vars['client_id'],
        client_secret=env_vars['client_secret'],
        redirect_uri=env_vars['redirect_uri'],
        scope=scope,
    )
    return spotipy.Spotify(auth_manager=auth_manager)

def get_playlists(sp):
    return sp.current_user_playlists(limit=50, offset=0)

def find_playlist(playlists, name, sp):
    for playlist in playlists['items']:
        if playlist['name'] == name:
            return sp.playlist(playlist['id'])
    return None

def delete_playlist(sp, username, playlist_id):
    sp.user_playlist_unfollow(user=username, playlist_id=playlist_id)

def create_playlist(sp, username, name):
    return sp.user_playlist_create(user=username, name=name, public=False)

def get_album_tracks(sp, album_id):
    return sp.album_tracks(album_id=album_id, limit=50, offset=0, market='US')['items']

def main():
    env_vars = load_env_variables()
    sp = authenticate_spotify(env_vars)
    username = env_vars['username']

    try:
        playlists = get_playlists(sp)
        release_radar = find_playlist(playlists, 'Release Radar', sp)
        new_album_releases_playlist = find_playlist(playlists, 'New Album Releases', sp)

        # Delete the New Album Releases playlist if it already exists
        if new_album_releases_playlist:
            delete_playlist(sp, username, new_album_releases_playlist['id'])

        if not release_radar or release_radar['tracks']['total'] == 0:
            print('Release Radar playlist not found or empty')
            return

        new_album_releases = [
            track['track']['album'] for track in release_radar['tracks']['items']
            # Filter out singles and EPs
            if track['track']['album']['album_type'] == 'album'
        ]

        if not new_album_releases:
            print('No new album releases found')
            return

        # Remove duplicates
        new_album_releases = list({album['id']: album for album in new_album_releases}.values())

        print(f'{len(new_album_releases)} new albums released this week:\n')
        for i, album in enumerate(new_album_releases, start=1):
            print(f'{i}:\t{album["artists"][0]["name"]} released "{album["name"]}" on {album["release_date"]}\n')

        tracks_to_add = [track['uri'] for album in new_album_releases for track in get_album_tracks(sp, album['id'])]

        # Split the tracks into chunks of 100 to avoid the "URI list too long" error
        splitted_tracks_to_add = divide_chunks(tracks_to_add, 100)
        print('Creating New Album Releases playlist...')
        new_playlist = create_playlist(sp, username, 'New Album Releases')

        print(f'Adding {len(tracks_to_add)} tracks to the playlist...')
        for tracks_uri in splitted_tracks_to_add:
            sp.playlist_add_items(new_playlist['id'], tracks_uri)

    except spotipy.SpotifyException as e:
        print(f'Spotify API Error: {e}')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    main()