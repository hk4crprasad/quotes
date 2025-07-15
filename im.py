from PIL import Image, ImageDraw, ImageFont

# Load original image
img = Image.open("generated_image_1.jpeg")

# Set up font
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_size = 50
font = ImageFont.truetype(font_path, font_size)

# Title text
title_text = "I'm trying to be better:"
padding = 30

# Measure text size using textbbox
draw = ImageDraw.Draw(img)
bbox = draw.textbbox((0, 0), title_text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Create new image with space for title
new_height = img.height + text_height + padding * 2
new_img = Image.new("RGB", (img.width, new_height), color="white")

# Paste original image below the title area
new_img.paste(img, (0, text_height + padding * 2))

# Draw title text (centered horizontally)
draw = ImageDraw.Draw(new_img)
text_x = (img.width - text_width) // 2
text_y = padding
draw.text((text_x, text_y), title_text, font=font, fill="black")

# Save the result
output_path = "quote_with_title.jpg"
new_img.save(output_path)
print(f"Saved with title at: {output_path}")
