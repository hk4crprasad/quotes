import os
import requests
import base64
from PIL import Image
from io import BytesIO

# Required Environment Variables or replace with hardcoded values
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://hara-md2td469-westus3.cognitiveservices.azure.com/")  
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-image-1")
api_version = os.getenv("OPENAI_API_VERSION", "2025-04-01-preview")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "ED8577EwFs8pfLmI8M2tusvBFaQKKy56YQDTnrhK1aIjBtZlsdv6JQQJ99BGACMsfrFXJ3w3AAAAACOGy4vI")

def decode_and_save_image(b64_data, output_filename):
    image = Image.open(BytesIO(base64.b64decode(b64_data)))
    image.show()
    image.save(output_filename)

def save_all_images_from_response(response_data, filename_prefix):
    if 'data' not in response_data:
        print("❌ Error: 'data' field missing in response.")
        print("🔎 Full response:")
        print(response_data)
        return

    for idx, item in enumerate(response_data['data']):
        b64_img = item['b64_json']
        filename = f"{filename_prefix}_{idx+1}.jpeg"
        decode_and_save_image(b64_img, filename)
        print(f"✅ Image saved to: '{filename}'")

# User provides quote here
user_quote = input("Enter your quote: ")

# Build the custom prompt using the user input
custom_prompt = f"""
Design a square motivational quote image with a realistic paper-like texture as the background. 
Use bold black serif or clean font for the quote. Highlight key parts of the text in yellow, 
as if marked with a highlighter. Place the quote in the center of the image, and in the bottom-right corner, 
write “—hara point” in a smaller, minimalist font. At the bottom center, include the line: “Share this if you agree.” 
The overall style should match an inspirational Instagram quote post with a warm, authentic, and thoughtful aesthetic.
Quote: {user_quote}
"""

# Build request
base_path = f'openai/deployments/{deployment}/images'
params = f'?api-version={api_version}'

generation_url = f"{endpoint}{base_path}/generations{params}"
generation_body = {
    "prompt": custom_prompt.strip(),
    "n": 1,
    "size": "1024x1024",
    "quality": "medium",
    "output_format": "jpeg",
}

# Call API
generation_response = requests.post(
    generation_url,
    headers={
        'Api-Key': subscription_key,
        'Content-Type': 'application/json',
    },
    json=generation_body
)

# Check for HTTP or JSON errors
try:
    json_response = generation_response.json()
except Exception as e:
    print("❌ Failed to parse JSON:", e)
    print("🔎 Raw Response Text:", generation_response.text)
    exit(1)

# Save Image(s) or print error
save_all_images_from_response(json_response, "generated_image")
