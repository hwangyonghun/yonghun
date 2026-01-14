from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import os
import pickle

# Define scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def upload_video(file_path, title="Toubina AI Promo", description="Deepfake Detection by aisolute.com"):
    creds = None
    # Check if token exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # Refresh or Login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('client_secrets.json'):
                print("Error: 'client_secrets.json' not found. Download it from Google Cloud Console.")
                return
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save creds
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            
    youtube = build('youtube', 'v3', credentials=creds)
    
    print(f"Uploading {file_path}...")
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['AI', 'Deepfake', 'Security', 'Toubina'],
            'categoryId': '28' # Science & Technology
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
            
    print(f"Upload Complete! Video ID: {response['id']}")

if __name__ == '__main__':
    video_file = input("Enter video file path (or press Enter for default 'toubina_promo.mp4'): ").strip()
    if not video_file:
        video_file = 'app/static/toubina_promo.mp4' # Default location if created by app
        
    if not os.path.exists(video_file):
        # Try finding it in upload folder
        video_file = os.path.join('app', 'uploads', 'toubina_promo.mp4')
        
    if os.path.exists(video_file):
        upload_video(video_file)
    else:
        print(f"File not found: {video_file}")
