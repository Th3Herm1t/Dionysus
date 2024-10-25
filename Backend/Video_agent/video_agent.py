# Backend/Video_agent/video_agent.py

import os
import moviepy.editor as mpe
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeAudioClip, concatenate_videoclips, CompositeVideoClip
from PIL import Image

class VideoAgent:
    def __init__(self, output_dir="output_videos"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def create_tiktok_video(
        self,
        screenshot_path,
        audio_path,
        vtt_path,
        output_filename,
        title_text=None,  # Add title text parameter
        title_duration=3,  # Duration of the title screen in seconds
    ):
        try:
            # Load assets
            screenshot = Image.open(screenshot_path)
            audio = AudioFileClip(audio_path)
            video_clip = self.image_to_video(screenshot, audio.duration)
            
            # Create title clip if title text is provided
            if title_text:
                title_clip = self.create_title_clip(title_text, title_duration)
                final_video = concatenate_videoclips([title_clip, video_clip])
            else:
                final_video = video_clip

            final_audio = mpe.CompositeAudioClip([audio])
            final_video = final_video.set_audio(final_audio)
            
            # Add subtitles
            if vtt_path and os.path.exists(vtt_path):
                subtitles = SubtitlesClip(vtt_path, self.make_textclip)
                final_video = CompositeVideoClip([final_video, subtitles.set_position(("center", "bottom"))])

            # Save the video
            output_path = os.path.join(self.output_dir, output_filename)
            final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
            
            return output_path

        except Exception as e:
            print(f"Error creating TikTok video: {e}")
            return None

    def image_to_video(self, image, duration):
        """Converts a single image to a video clip of the specified duration."""
        return mpe.ImageClip(image).set_duration(duration)

    def make_textclip(self, txt, fontsize=30, color='white', font='Arial'):
        """Creates a TextClip with the given text and styling."""
        return TextClip(txt, fontsize=fontsize, color=color, font=font)

    def create_title_clip(self, title_text, duration,  fontsize=50, bg_color=(0, 0, 0), text_color='white', font='Arial'):
        """Creates a title clip with the given text and duration."""
        title_clip = TextClip(title_text, fontsize=fontsize, color=text_color, font=font, bg_color=bg_color)
        title_clip = title_clip.set_pos('center').set_duration(duration)
        return title_clip