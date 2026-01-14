import yt_dlp
import os

print("Testing yt-dlp for MSN URL...")
url = "https://www.msn.com/ko-kr/news/other/%ED%95%98%EC%9A%B0%EB%A8%B8%EB%8B%88-%EC%86%8C%EB%B9%84%EC%9E%90%EB%93%A4-1%EB%85%84-%ED%9B%84%EC%97%90%EB%8F%84-%EC%A7%91%EA%B0%92-%EC%83%81%EC%8A%B9-%EC%9D%B4%EC%9C%A0%EB%8A%94/vi-AA1DBAwA?ocid=msedgntp&pc=U531&cvid=69624ed9b5dd4871ac06c7e47e68759d&ei=16"

ydl_opts = {
    'format': 'best',
    'outtmpl': 'msn_test.mp4',
    'quiet': False
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("Download success")
except Exception as e:
    print(f"Download failed: {e}")
