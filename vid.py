from moviepy import AudioFileClip, ImageClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.video.fx.FadeIn import FadeIn

# --- CONFIGURATION ---
AUDIO_FILE = "/home/tecosys/quotes/new.mp3"
QUOTE_IMAGE_FILE = "/home/tecosys/quotes/generated_image_1.jpeg"
OUTPUT_FILE = "quote_video.mp4"

TITLE_TEXT = "Daily Vibe"
VIDEO_SIZE = (1080, 1920)
FADE_IN_DELAY = 9
FADE_IN_DURATION = 4

print("🔊 Loading audio and image...")
audio_clip = AudioFileClip(AUDIO_FILE)
video_duration = audio_clip.duration

# Background
background_clip = ColorClip(size=VIDEO_SIZE, color=(20, 20, 20)).with_duration(video_duration)

font_main = "DejaVuSans-Bold"

print("📝 Creating text clips...")

# Banner just above the quote
banner_y = 300
banner_height = 160  # 👈 Taller banner

# White banner background
banner_clip = ColorClip(size=(VIDEO_SIZE[0], banner_height), color=(255, 255, 255))\
    .with_duration(video_duration)\
    .with_position(("center", banner_y))

# Title text centered inside taller banner
title_clip = TextClip(
    font_main,
    text=TITLE_TEXT,
    method='caption',
    size=(VIDEO_SIZE[0] - 100, None),
    font_size=70,
    color='black'
).with_duration(video_duration).with_position(("center", banner_y + 35))  # Adjusted padding inside banner

# Quote image fades in after 9s
quote_clip = (
    ImageClip(QUOTE_IMAGE_FILE)
    .with_duration(video_duration - FADE_IN_DELAY)
    .with_start(FADE_IN_DELAY)
    .resized(width=VIDEO_SIZE[0])
    .with_position("center")
    .with_effects([FadeIn(FADE_IN_DURATION)])
)

# Final composition
print("🎬 Compositing video...")
layers = [background_clip, banner_clip, title_clip, quote_clip]
final_video = CompositeVideoClip(layers).with_audio(audio_clip)

# Export video
print(f"💾 Writing final video to {OUTPUT_FILE}...")
final_video.write_videofile(OUTPUT_FILE, codec="libx264", audio_codec="aac", fps=24)

audio_clip.close()
final_video.close()
print("✅ Video created successfully!")
