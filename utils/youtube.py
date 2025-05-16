import yt_dlp
from telegram import Bot

def progress_status(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        speed = d.get('_speed_str', '0 KiB/s')
        eta = d.get('eta', 0)
        print(f"Downloading... {percent} at {speed}, ETA: {eta}s")
    elif d['status'] == 'finished':
        print("Download finished.")

def search_youtube(query):
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(f"ytsearch10:{query}", download=False)['entries']
    return [{'title': vid['title'], 'url': vid['webpage_url']} for vid in info]

def get_download_options(url):
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = {}
        for fmt in info.get('formats', []):
            if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                height = fmt.get('height')
                if height:
                    formats[f"{height}p"] = fmt['format_id']
        return formats

def download_video(url, format_id, output_path):
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'noplaylist': True,
        'progress_hooks': [progress_status],
        # No cookies used here
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])