from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, VideoFileClip, ColorClip
from PIL import Image, ImageOps
import os
import logging
import traceback
import random

# Configure logging
def configure_logging(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"):
    logging.basicConfig(level=level, format=format)
    logger = logging.getLogger(__name__)
    return logger

# Default configuration for the video creation
default_config = {
    "aspect_ratio": (1080, 1920),  # TikTok vertical video format
    "fps": 24,
    "bitrate": "5000k",
    "audio_bitrate": "192k",
    "preset": "slow",
    "crf": "18",
    "threads": 8,
    "bg_videos_folder": os.path.join("Backend", "Workflows", "Assets", "bg_videos"),
    "ffmpeg_params": ["-crf", "18"]
}

def create_tiktok_video(
    post_folder: str,
    config: dict = default_config,
    output_filename: str = "tiktok_video.mp4",
    bg_videos_folder: str = None,
    fps: int = None,
    bitrate: str = None,
    audio_bitrate: str = None,
    crf: str = None,
    threads: int = None,
    preset: str = None,
    desired_width: int = None,
    desired_height: int = None,
    ffmpeg_params: list = None
):
    try:
        logger = configure_logging()

        # Apply config or fall back to defaults
        desired_width = desired_width or config['aspect_ratio'][0]
        desired_height = desired_height or config['aspect_ratio'][1]
        fps = fps or config['fps']
        bitrate = bitrate or config['bitrate']
        audio_bitrate = audio_bitrate or config['audio_bitrate']
        preset = preset or config['preset']
        crf = crf or config['crf']
        threads = threads or config['threads']
        ffmpeg_params = ffmpeg_params or config['ffmpeg_params']
        bg_videos_folder = bg_videos_folder or config['bg_videos_folder']

        logger.info(f"Desired dimensions: {desired_width}x{desired_height}")

        # Load Assets
        screenshot_path = os.path.join(post_folder, "post_1g9ny24.png")
        narration_path = os.path.join(post_folder, "narration.mp3")
        
        # Load and process screenshot
        logger.info(f"Loading screenshot: {screenshot_path}")
        screenshot_img = Image.open(screenshot_path)
        logger.info(f"Original screenshot dimensions: {screenshot_img.size}")

        # Calculate aspect ratio and padding
        tiktok_aspect_ratio = desired_width / desired_height
        img_width, img_height = screenshot_img.size
        img_aspect_ratio = img_width / img_height

        if img_aspect_ratio > tiktok_aspect_ratio:
            new_height = int(desired_width / img_aspect_ratio)
            padding = (0, (desired_height - new_height) // 2) * 2
        else:
            new_width = int(desired_height * img_aspect_ratio)
            padding = ((desired_width - new_width) // 2, 0) * 2

        screenshot_img.thumbnail((desired_width, desired_height), Image.Resampling.LANCZOS)
        padded_img = ImageOps.expand(screenshot_img, padding, fill="black")
        logger.info(f"Padded screenshot dimensions: {padded_img.size}")

        temp_resized_screenshot = os.path.join(post_folder, "padded_screenshot.png")
        padded_img.save(temp_resized_screenshot)

        # Load narration and get duration
        logger.info(f"Loading narration: {narration_path}")
        narration = AudioFileClip(narration_path)
        video_duration = narration.duration
        logger.info(f"Video duration: {video_duration} seconds")

        # Attempt to load a background video
        background_video = None
        try:
            bg_video_files = [f for f in os.listdir(bg_videos_folder) if f.endswith(('.mp4', '.webm'))]
            if bg_video_files:
                selected_bg_video = random.choice(bg_video_files)
                selected_bg_video_path = os.path.join(bg_videos_folder, selected_bg_video)
                logger.info(f"Loading background video: {selected_bg_video_path}")
                
                background_video = VideoFileClip(selected_bg_video_path)
                logger.info(f"Original background video dimensions: {background_video.size}")
                
                # Resize background video
                background_video = background_video.resize(width=desired_width, height=desired_height)
                logger.info(f"Resized background video dimensions: {background_video.size}")
                
                # Loop if necessary
                if background_video.duration < video_duration:
                    logger.info("Looping background video")
                    background_video = background_video.loop(duration=video_duration)
                
                background_video = background_video.subclip(0, video_duration)
                
        except Exception as e:
            logger.error(f"Failed to load background video: {e}")
            background_video = None  # No background if loading fails

        # Create screenshot clip
        logger.info("Creating screenshot clip")
        screenshot_clip = ImageClip(temp_resized_screenshot)
        screenshot_clip = screenshot_clip.set_duration(video_duration)
        logger.info(f"Screenshot clip dimensions: {screenshot_clip.size}")

        # Create final composite
        logger.info("Creating composite video")
        clips = [screenshot_clip]  # Start with just the screenshot
        if background_video:
            clips.insert(0, background_video)  # Add background video as the first layer if loaded

        final_video = CompositeVideoClip(clips, size=(desired_width, desired_height))
        final_video = final_video.set_audio(narration)
        logger.info(f"Final video dimensions: {final_video.size}")

        # Save video
        output_path = os.path.join(post_folder, output_filename)
        logger.info(f"Saving video to: {output_path}")
        final_video.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac", 
            fps=fps, 
            bitrate=bitrate,
            preset=preset, 
            threads=threads, 
            audio_bitrate=audio_bitrate, 
            ffmpeg_params=ffmpeg_params
        )

        # Cleanup
        if os.path.exists(temp_resized_screenshot):
            os.remove(temp_resized_screenshot)
            
        logger.info("Closing clips")
        narration.close()
        if background_video:
            background_video.close()
        screenshot_clip.close()
        final_video.close()

        logger.info("TikTok video created successfully!")
        return output_path

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()
        return None

# Example usage
if __name__ == "__main__":
    test_post_folder = os.path.join(
        "Backend", "Workflows", "data", "Reddit to TikTok", 
        "2024-10-23", "AskReddit", "post_1g9ny24"
    )
    output_video = create_tiktok_video(test_post_folder)
    if output_video:
        print(f"Video created successfully at: {output_video}")
    else:
        print("Failed to create video. Check logs for details.")