from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip

# File paths
input_video_path = r"Backend\Workflows\Assets\bg_videos\6 Minutes Minecraft Shader Parkour Gameplay (Night-Time) [Free to Use] [Map Download].mp4"
narration_audio_path = r"Backend\Workflows\data\Reddit to TikTok\2024-10-23\AskReddit\post_1g9ny24\narration.mp3"
screenshot_path = r"Backend\Workflows\data\Reddit to TikTok\2024-10-23\AskReddit\post_1g9ny24\post_1g9ny24.png"
output_video_path = r"Backend\Workflows\Assets\bg_videos\tiktok_minecraft_shader_parkour_with_screenshot.mp4"

# TikTok video settings
tiktok_resolution = (1080, 1920)  # 9:16 aspect ratio
tiktok_duration = 60               # TikTok typical max duration in seconds

# Load the video
video = VideoFileClip(input_video_path).without_audio()

# Calculate the cropping dimensions to make it 9:16 aspect ratio
video_width, video_height = video.size
aspect_ratio = 9 / 16

if video_width / video_height > aspect_ratio:
    # Video is too wide, crop the sides
    new_width = int(video_height * aspect_ratio)
    x1 = (video_width - new_width) // 2
    y1 = 0
    crop_box = (x1, y1, x1 + new_width, video_height)
else:
    # Video is too tall, crop the top and bottom
    new_height = int(video_width / aspect_ratio)
    x1 = 0
    y1 = (video_height - new_height) // 2
    crop_box = (x1, y1, video_width, y1 + new_height)

# Apply the crop and resize to TikTok resolution
video = video.crop(*crop_box).resize(tiktok_resolution)

# Trim the video to the desired duration
video = video.subclip(0, min(tiktok_duration, video.duration))

# Load the narration audio
narration_audio = AudioFileClip(narration_audio_path)

# Add narration audio to the video
video = video.set_audio(narration_audio)

# Load the screenshot
screenshot = ImageClip(screenshot_path)

# Calculate the padding
padding = 50  # Padding on both left and right sides
screenshot_width = tiktok_resolution[0] - 2 * padding  # Set screenshot width to fit within the padding
screenshot = screenshot.resize(width=screenshot_width)

# Position the screenshot in the center of the upper half of the video
screenshot_x = (tiktok_resolution[0] - screenshot_width) // 2
screenshot_y = (tiktok_resolution[1] // 4) - (screenshot.size[1] // 2)  # Centered in upper half

# Set the position of the screenshot
screenshot = screenshot.set_position((screenshot_x, screenshot_y)).set_duration(video.duration)

# Combine video and screenshot
final_video = CompositeVideoClip([video, screenshot])

# Write the output video
final_video.write_videofile(output_video_path, codec="libx264", fps=60, bitrate="5000k", audio_bitrate="192k", preset="slow", threads=8)
