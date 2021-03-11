# playlist-tool
I 'quickly' put together to export my plug.dj JSON data and manage my playlists. It's mainly for my personal use so UX is pretty rough. If you are to use this, please read below!

## Functionality
* Use plug.dj JSON data to export playlists to YouTube and Soundcloud
* Plug playlists be retrieved via [this method](https://pastebin.com/ezyUvcu0)
* Compensates for YouTube's rate limiting for large playlists

## Usage Disclaimers
You will need to input your Soundcloud login credentials directly into the program due to OAuth User Credentials Flow. I could not bother creating a local server just for Authorization Code Flow.

You must provide your own YouTube and Soundcloud keys for this to work (no stealing my keys sry). YouTube has a standard quota of 10000 units daily, in which adding one song utilizes 50 units. In other words, one can only add 200 songs to a playlist everyday. I have tried to remedy this through writing a program that can be ran daily to add ≤200 songs to a playlist. It's imperative to make sure the YouTube quota hasn't been reached before running either program. Soundcloud has no quota.

## Setup
1. I used Python 3.8. This program probably works for any Python 3.x, but who knows
2. Install [Soundcloud](https://github.com/soundcloud/soundcloud-python) and [YouTube](https://developers.google.com/youtube/v3/quickstart/python) libraries
3. Obtain YouTube API credentials, download the client_secret.json, and place it as `./auth/client_secret.json` (ensure same name)
   * Ensure you enable the full `youtube` scope and have set up OAuth
5. Paste your standard YouTube API key in `YT_devkey` field of `./auth/auth-keys.json`
6. Get Soundcloud credentials and fill in the rest of `.auth/auth-keys.json` respectively.
7. Place `plug-export.json` in the main directory.

## Programs
* Use `PLUG-EXPORT.py` to export specified playlists into YouTube and Soundcloud playlists
* Use `PLUG-YT-ADDER.py` daily to add songs to a YouTube playlist if there are over 200 songs in a playlist
  * If you're trying to export a playlist of over 200 songs, a `.csv` of remaining IDs will be saved to `./ID-storage`
