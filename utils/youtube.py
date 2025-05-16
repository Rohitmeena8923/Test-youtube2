from yt_dlp import YoutubeDL

def search_youtube(query):
    ydl_opts = {"quiet": True, "extract_flat": True, "skip_download": True}
    with YoutubeDL(ydl_opts) as ydl:
        search_result = ydl.extract_info(f"ytsearch10:{query}", download=False)
        return search_result["entries"]

def get_download_options(video_url):
    ydl_opts = {
        "quiet": True,
        "listformats": True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        formats = {f"{f['format_note']}": f["format_id"]
                   for f in info['formats'] if f.get('vcodec') != "none" and f.get("format_note")}
        return formats

def download_video(video_url, format_id, output_path):
    ydl_opts = {
        "format": format_id,
        "outtmpl": output_path,
        "progress_hooks": [progress_hook],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

progress_status = {}
def progress_hook(d):
    if d["status"] == "downloading":
        progress_status[d["filename"]] = d["_percent_str"], d["_speed_str"]