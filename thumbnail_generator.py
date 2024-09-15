import os
import re
import requests
import textwrap
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def extract_nouns(text):
    text = re.sub(r'^AITA\s+', '', text, flags=re.IGNORECASE)
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = set(['for', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must', 'ought'])
    potential_nouns = [word for word in words if word not in stop_words and len(word) > 2]
    return ' '.join(potential_nouns)

def search_image(query):
    api_key = os.getenv('PIXABAY_API_KEY')
    if not api_key:
        raise ValueError("Pixabay API key not found in .env file")
    
    url = f"https://pixabay.com/api/?key={api_key}&q={query}&image_type=photo&min_width=1280&min_height=720"
    response = requests.get(url)
    data = response.json()
    
    if 'hits' in data and len(data['hits']) > 0:
        return data['hits'][0]['largeImageURL']
    else:
        return None

def create_thumbnail(image_url, text):
    # Download the image
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    
    # Resize and crop the image to exactly 1280x720
    img = img.convert('RGB')
    img.thumbnail((1280, 720), Image.LANCZOS)
    width, height = img.size
    left = (width - 1280)/2
    top = (height - 720)/2
    right = (width + 1280)/2
    bottom = (height + 720)/2
    img = img.crop((left, top, right, bottom))
    
    # Create a new image with a semi-transparent black overlay
    overlay = Image.new('RGBA', (1280, 720), (0, 0, 0, 180))  # Increased opacity for better text visibility
    img = Image.alpha_composite(img.convert('RGBA'), overlay)
    
    # Add text
    draw = ImageDraw.Draw(img)
    font_size = 60  # Significantly increased font size
    font_path = "custom_font.ttf"  # Make sure this font file exists in your directory
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()
        print("Warning: Arial font not found. Using default font.")
    
    # Wrap text
    wrapped_text = textwrap.fill(text, width=10)  # Reduced width for larger font
    
    # Calculate text position (centered)
    text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
    text_position = ((1280 - text_bbox[2]) / 2, (720 - text_bbox[3]) / 2)
    
    # Draw text
    draw.multiline_text(text_position, wrapped_text, font=font, fill=(255, 255, 255), align='center')
    
    # Save the image
    img.save("output/thumbnail.png")

def main():
    reddit_title = input("Enter the Reddit post title: ")
    search_query = extract_nouns(reddit_title)
    image_url = search_image(search_query)
    
    if image_url:
        create_thumbnail(image_url, reddit_title)
        print("Thumbnail created successfully!")
    else:
        print("No suitable image found.")

if __name__ == "__main__":
    main()
