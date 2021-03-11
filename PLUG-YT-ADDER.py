import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import time
import csv
import json
import os


def yt_adder(yt_id, client):
    cnt = 1
    error_list = []  # List of deleted song IDs
    print("Navigate to your playlist and get the ID (youtube.com/playlist?list=____)")
    playlist_id = input("Enter the playlist ID: ")
    for videoId in yt_id:
        time.sleep(0.3)
        print("Adding " + videoId + "... (" + str(cnt) + ")")
        try:
            request = client.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,  # Insert playlist ID here
                        "position": 0,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": videoId
                        }
                    }
                }
            )
            responses = request.execute()  # Adds 1 video to playlist
        except Exception as x:  # Most common exception should be deleted videos
            print("\t" + str(x))
            error_list.append(videoId)
        cnt += 1
    return error_list


# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
scopes = ["https://www.googleapis.com/auth/youtube"]
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "auth/client_secret.json"

print("PLUG.DJ PLAYLIST EXPORTER -- YouTube Long Playlist Extension")
print("NOTE: Please ensure your daily YouTube API quota is unused!!")

while True:
    try:
        filename = input("Enter the filename (____.csv): ")
        filename = 'ID-storage/' + filename + '.csv'

        with open(filename, 'r') as f:
            ytID = list(csv.reader(f))
        break
    except Exception as e:
        print("\t" + str(e) + "\n\tTry again.")

# Get credentials and create an API client
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

errorList = yt_adder(ytID[0], youtube)  # Adds the first set of videos to YouTube

if errorList:
    with open('plug_export.json', encoding="utf-8") as f:
        data = json.load(f)
    print("UNADDED VIDEOS:")
    for y in errorList:
        print(y)
        try:
            print("\t" + str(data["1"]["m"][str(y)]["title"]) + " by " + str(data["1"]["m"][str(y)]["author"]))
        except Exception as e:
            print("\t" + str(e) + "\n\tERROR: ID not located in plug_export.json")
    print("")  # Spacer

del ytID[0]
print(ytID)
if ytID:
    print("more")
    with open(filename, 'w', newline='') as fp:
        csv.writer(fp).writerows(ytID)
else:
    print("All songs in the queue have been added to playlists.")
    os.remove(filename)

print("Program end.")
