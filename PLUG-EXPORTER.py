import soundcloud, os, google_auth_oauthlib.flow, googleapiclient.discovery, googleapiclient.errors, time, json, csv
from utils.extract import json_extract
from utils.duplicated import removeDuplicates
import urllib.request as request
from datetime import datetime

# Get API keys from file
with open("auth/auth-keys.json") as f:
    keys = json.load(f)
CLIENT_ID = keys["client_id"]
CLIENT_SECRET = keys["client_secret"]


def sc_adder(IDs, client):
    # PLAYLIST IMPORTATION
    name = str(input("\nPlaylist name: "))
    description = "Imported from plug.dj via Redstone's import tool, " + datetime.now().replace(microsecond=0).isoformat()
    tracks = list(map(lambda id: dict(id=id), IDs))
    playlistID = ""
    failed = False
    try:
        response = client.post('/playlists', playlist={
            'title': name,
            'description': description,
            'sharing': 'public',
            'tracks': tracks
        })
        time.sleep(0.5)
        print(response.track_count, "songs now in playlist.")
        playlistID = response.id
    except Exception as e:
        print(e)

    # UNADDED SONG SEARCH #
    with request.urlopen('https://api.soundcloud.com/playlists/' + str(playlistID) + '?client_id=' + CLIENT_ID) as response:
        playlist = json.loads(response.read())
    with open('plug_export.json', encoding="utf-8") as f:
        data = json.load(f)

    IDlist = json_extract(playlist, "id")
    IDs = [int(x) for x in IDs]  # Makes all elements into integers
    del IDlist[1::2]  # Remove every other ID (the uploader ID)
    del IDlist[-1]  # Removes last element (playlist creator ID)

    # Removes all duplicated IDs to find ones that were not added
    IDs = [x for x in IDs if x not in IDlist]

    print("There are " + str(len(IDs)) + " unadded songs.")
    if len(IDs) > 0:
        for y in IDs:
            print(y)
            print("\t" + str(data["1"]["m"][str(y)]["title"]) + " by " + str(data["1"]["m"][str(y)]["author"]))


def yt_adder(ytId, youtube):
    cnt = 1
    errorList = []  # List of deleted song IDs
    print("Please premake a playlist for your songs!!")
    playlistId = input("Enter the playlist ID: ")
    for videoId in ytId:
        time.sleep(0.3)
        print("Adding " + videoId + "... (" + str(cnt) + ")")
        try:
            request = youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlistId,  # Insert playlist ID here
                        "position": 0,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": videoId
                        }
                    }
                }
            )
            responses = request.execute()  # Adds 1 video to playlist
        except Exception as e:  # Most common exception should be deleted videos
            print("\t" + str(e))
            errorList.append(videoId)
        cnt += 1
    return errorList


# JSON loader
with open('plug_export.json', encoding="utf-8") as f:
    data = json.load(f)
playlists = json_extract(data, 'name')  # List of playlist names
playlistID = json_extract(data, 'id')  # List of playlist IDs
del playlistID[0:-len(playlists)]  # Removes IDs from 'm' nest

print("PLUG.DJ JSON EXPORTER by SCRedstone")
field = "."
while field != "":
    ytID = []  # YouTube video IDs list
    scID = []  # Soundcloud song IDs list
    print("\nPLAYLIST(S) FOUND")
    for i in playlists:
        print('"' + i + '" ', end='')  # Prints playlist names
    print("")
    while field != "":  # Runs as long as there is an input
        field = input("Pick a playlist to add to queue; enter nothing to add the current queue to YT/SC: ")
        if field == "":
            break
        elif field in playlists:
            getID = str(playlistID[playlists.index(field)])  # Gets playlist ID from selection
            getID = data["1"]["p"][getID]["items"]  # Gets the list of song IDs, searching via playlist ID

            # Sorts all IDs found in the playlist into YouTube and Soundcloud lists
            count, ytCount, scCount = 0, 0, 0
            for key, value in getID.items():
                try:  # Tests if key is Soundcloud (int) or YouTube (string) ID
                    int(key)
                    scID.append(key)
                    scCount += 1
                except ValueError:
                    ytID.append(key)
                    ytCount += 1
                count = count + 1

            print("\t" + str(count), "songs added | " + str(ytCount) + " YT, " + str(scCount) + " SC.")
            ytID = removeDuplicates(ytID, "YouTube")
            scID = removeDuplicates(scID, "Soundcloud")
            print("\nCURRENT QUEUE:", len(ytID), "YT,", len(scID), "SC.")

        elif field not in playlists:
            print("Invalid playlist!!")
            continue
        else:
            print("ERROR. Try again.")

    # -- SOUNDCLOUD ADDING -- #
    print("ADDING SOUNDCLOUD...")

    # CLIENT OAUTH
    try:  # Seeing if client already exists
        client
    except NameError:
        client = ""
    while client == "":
        username = str(input("Soundcloud username: "))
        password = str(input("Soundcloud password: "))
        try:
            client = soundcloud.Client(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                username=username,
                password=password
            )
        except Exception as e:
            print("\t" + str(e))
    time.sleep(0.2)
    print("Logged in as", client.get('/me').username)
    time.sleep(0.2)

    if len(scID) > 500:
        print("NOTE: there is a 500 song limit to SC songs. Queue will be split.")
        scID = [scID[i * 500:(i + 1) * 500] for i in range((len(scID) + 500 - 1) // 500)]
        for x in scID:
            time.sleep(0.5)
            sc_adder(x, client)
    else:
        sc_adder(scID, client)

    # -- YOUTUBE ADDING -- #
    print("\nADDING YOUTUBE...")

    # CLIENT OAUTH
    scopes = ["https://www.googleapis.com/auth/youtube"]
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "auth/client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    YTerrors = []
    if len(ytID) > 200:
        print("Due to YouTube API rate limiting, only 200 songs can be added to a playlist per day. "
              "The tool will split the YT queue and save it to disk; use YT-adder.py to upload it in the coming days."
              "\n\tYou may rename the file generated to make it more convenient.")
        ytID = [ytID[i * 200:(i + 1) * 200] for i in range((len(ytID) + 200 - 1) // 200)]
        YTerrors = yt_adder(ytID[0], youtube)

        del ytID[0]  # Deletes the list that just got added
        filename = "ID-storage/Youtube-IDs-" + datetime.now().strftime('%y-%m-%d-%H%M%S') + ".csv"
        with open(filename, 'w', newline='') as fp:
            csv.writer(fp).writerows(ytID)
    else:
        YTerrors = yt_adder(ytID, youtube)

    if YTerrors:
        print("UNADDED VIDEOS:")
        for y in YTerrors:
            print(y)
            try:
                print("\t" + str(data["1"]["m"][str(y)]["title"]) + " by " + str(data["1"]["m"][str(y)]["author"]))
            except Exception as e:
                print("\t" + str(e) + "\n\tERROR: ID not located in plug_export.json")
        print("")  # Spacer

    field = input("Enter any key to return to beginning; nothing to exit.")
