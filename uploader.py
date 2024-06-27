import os
import pickle
from pyrogram import Client, filters
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.auth.exceptions
from googleapiclient.http import MediaFileUpload

# إعدادات البوت
API_ID = "20928059"
API_HASH = "e5cf9b59dd2e9d444aed2479e2d18516"
BOT_TOKEN = "6699616785:AAE0636PL-PFCtbilLh3IwhHbEsxd2iYNS0"

# إعدادات YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "C:/Users/hossamx/pybro/yt/client_secret.json"
CREDENTIALS_FILE = "C:/Users/hossamx/pybro/yt/credentials.pickle"

app = Client("uploader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_authenticated_service():
    credentials = None
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "rb") as f:
            credentials = pickle.load(f)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        
        with open(CREDENTIALS_FILE, "wb") as f:
            pickle.dump(credentials, f)
    
    return build("youtube", "v3", credentials=credentials)

def upload_video(youtube, video_path):
    request_body = {
        "snippet": {
            "title": "Uploaded via Telegram Bot",
            "description": "Video uploaded from Telegram bot",
            "tags": ["telegram", "bot"],
            "categoryId": "22"  # 'People & Blogs' category
        },
        "status": {
            "privacyStatus": "public",  # 'public', 'private' or 'unlisted'
            "selfDeclaredMadeForKids": False,
        }
    }
    
    try:
        media = MediaFileUpload(video_path, resumable=True)
        response = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        ).execute()
        
        return response
    except google.auth.exceptions.TransportError as e:
        print(f"An error occurred during the upload: {e}")
        return None

@app.on_message(filters.video)
def handle_video(client, message):
    print("Received a video message")
    video_file = message.video.file_name
    
    # تنزيل الفيديو
    print(f"Downloading video: {video_file}")
    video_path = app.download_media(message)
    print(f"Downloaded video to: {video_path}")
    
    # تحميل الفيديو إلى YouTube
    print("Authenticating YouTube service")
    youtube = get_authenticated_service()
    print("Uploading video to YouTube")
    response = upload_video(youtube, video_path)
    
    if response:
        print(f"Video uploaded successfully: https://youtu.be/{response['id']}")
        message.reply(f"Video uploaded successfully! Watch it here: https://youtu.be/{response['id']}")
    else:
        print("Failed to upload the video to YouTube")
        message.reply("Failed to upload the video to YouTube.")
    
    # حذف الفيديو المحلي بعد التحميل
    print(f"Deleting local video file: {video_path}")
    os.remove(video_path)

print("Bot is running")
app.run()
