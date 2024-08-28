# Spotify New Albums Release Radar

This project stems from my need to automate the generation of a playlist of new albums to listen to each week.
Spotify generates a playlist of new music from the artists we follow but does not include the full albums, so I decided to create this script.

## Prerequisite

To use this tool, you will need a Spotify for Developers account, which you can get access to https://developer.spotify.com/. You will need to create a new app and that will provide you with a Spotify client id and secret.

## Usage

This is a simple Python script that relies on [Spotipy](https://spotipy.readthedocs.io/en)

```
$ git clone ...
```

Install required modules:

```
$ pip install -r requirements.txt
```

Reference the Spotify API credentials here:

```
$ export SPOTIPY_CLIENT_ID=<<your spotify client id>>
$ export SPOTIPY_CLIENT_SECRET=<<your spotify secret>>
$ export SPOTIPY_REDIRECT_URI=<<your spotify redirect uri>>
$ export SPOTIFY_USERNAME=<<your spotify username>>
```

Running the tool:

```bash
$ python3 spotify-new-albums-radar.py
```

## Notes

This project was heavly inspired by Robby Russell's [Spotify New Album Release Radar](https://github.com/robbyrussell/spotify-new-albums-radar). In fact, I took his idea, wrote it in Python and added some useful features (such as automatic playlist creation) 😎
