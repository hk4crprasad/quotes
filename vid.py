from moviepy import AudioFileClip, ImageClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.video.fx.FadeIn import FadeIn

# --- CONFIGURATION ---
AUDIO_FILE = "/home/tecosys/quotes/new.mp3"
QUOTE_IMAGE_FILE = "/home/tecosys/quotes/generated_image_1.jpeg"
OUTPUT_FILE = "quote_video_fixed.mp4"

TITLE_TEXT = "Make money so you can choose who deserves your time"
VIDEO_SIZE = (1080, 1920)
FADE_IN_DELAY = 9
FADE_IN_DURATION = 4
FONT_MAIN = "DejaVuSans-Bold" # Make sure this font is installed on your system

print("🔊 Loading audio and image...")
audio_clip = AudioFileClip(AUDIO_FILE)
video_duration = audio_clip.duration

# Background
background_clip = ColorClip(size=VIDEO_SIZE, color=(20, 20, 20)).with_duration(video_duration)

print("📝 Creating text clips...")

# Banner just above the quote
banner_y = 300
banner_height = 160

# White banner background
banner_clip = ColorClip(size=(VIDEO_SIZE[0], banner_height), color=(255, 255, 255))\
    .with_duration(video_duration)\
    .with_position(("center", banner_y))

# --- Dynamic Font Size Calculation ---
print("📏 Calculating best font size for the title...")
banner_width_constraint = VIDEO_SIZE[0] - 100 # Add some padding
banner_height_constraint = banner_height - 20 # Add some vertical padding

font_size = 100 # Start with a large font size
while True:
    # Create a temporary clip to measure its size
    temp_clip = TextClip(
        text=TITLE_TEXT,
        font=FONT_MAIN,
        font_size=font_size,
        color='black',
        method='caption',
        size=(banner_width_constraint, None)
        # REMOVED unsupported alignment/gravity argument
    )
    # Check if the generated clip's height fits within the banner
    if temp_clip.size[1] <= banner_height_constraint:
        print(f"✅ Font size {font_size} fits.")
        break
    # It doesn't fit, reduce font size and try again
    font_size -= 2
    # Safety break in case of an issue
    if font_size < 10:
        print("⚠️ Warning: Title text is very long, using smallest font.")
        break
# --- End of Dynamic Calculation ---

# Title text clip, created with the optimal font size
banner_center_y = banner_y + (banner_height / 2)
title_clip = TextClip(
    text=TITLE_TEXT,
    font=FONT_MAIN,
    font_size=font_size,
    color='black',
    method='caption',
    size=(banner_width_constraint, None)
    # REMOVED unsupported alignment/gravity argument
).with_duration(video_duration).with_position(('center', banner_center_y))

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