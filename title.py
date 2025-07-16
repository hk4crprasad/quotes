from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

# Banner dimensions
WIDTH = 1024
HEIGHT = 250
TEXT = "money is the big thing in lyfe, you have to achive it"
BG_COLOR = "white"
TEXT_COLOR = "black"
MARGIN = 40
LINE_SPACING = 10

# Font path (Linux)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def load_font(size):
    if os.path.exists(FONT_PATH):
        return ImageFont.truetype(FONT_PATH, size)
    else:
        return ImageFont.load_default()

def wrap_text(text, font, draw, max_width):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width - 2 * MARGIN:
            line = test_line
        else:
            if line:  # Only add line if it's not empty
                lines.append(line)
                line = word
            else:  # Single word is too long, add it anyway
                lines.append(word)
                line = ""
    if line:
        lines.append(line)
    return lines

def get_best_font(text, draw, max_width, max_height):
    for size in range(100, 8, -2):  # Go down to size 8, step by 2 for faster processing
        font = load_font(size)
        lines = wrap_text(text, font, draw, max_width)
        
        # Calculate actual text height for each line
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]  # Actual height of text
            line_heights.append(line_height)
        
        total_height = sum(line_heights) + (len(lines) - 1) * LINE_SPACING
        
        if total_height <= max_height - 2 * MARGIN:
            return font, lines
    
    # Final fallback with smallest possible font
    return load_font(8), wrap_text(text, load_font(8), draw, max_width)

# Create image
image = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(image)

font, wrapped_lines = get_best_font(TEXT, draw, WIDTH, HEIGHT)

# Center vertically
line_heights = [draw.textbbox((0, 0), line, font=font)[3] for line in wrapped_lines]
total_text_height = sum(line_heights) + (len(wrapped_lines) - 1) * LINE_SPACING
y = (HEIGHT - total_text_height) // 2

# Draw each line
for line in wrapped_lines:
    bbox = draw.textbbox((0, 0), line, font=font)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    draw.text((x, y), line, fill=TEXT_COLOR, font=font)
    y += bbox[3] + LINE_SPACING

# Save or show
image.save("banner_1024x300.png")
image.show()
