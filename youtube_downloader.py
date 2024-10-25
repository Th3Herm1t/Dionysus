import yt_dlp
import os

def download_background_video(url, output_path='.'):
    """
    Download a YouTube video optimized for use as a background video in TikTok videos.
    """
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Ensure we get a complete video
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'prefer_ffmpeg': True,
        'ffmpeg_location': None,  # Change this if ffmpeg is in a specific location
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from: {url}")
            info = ydl.extract_info(url, download=True)
            video_title = info['title']
            video_path = os.path.join(output_path, f"{video_title}.mp4")
            print(f"Video downloaded successfully to: {video_path}")
            return video_path
    except Exception as e:
        print(f"An error occurred while downloading: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    # Create the output directory if it doesn't exist
    output_dir = os.path.join('Backend', 'Workflows', 'Assets', 'bg_videos')
    os.makedirs(output_dir, exist_ok=True)
    
    # Download the video
    video_url = 'https://www.youtube.com/watch?v=ZkHKGWKq9mY'
    downloaded_path = download_background_video(video_url, output_dir)
    
    if downloaded_path:
        print(f"Video ready for use at: {downloaded_path}")
    else:
        print("Failed to download video")