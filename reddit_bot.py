import praw
import os
import re
from dotenv import load_dotenv
from thumbnail_generator import create_thumbnail, search_image, extract_nouns
from gtts import gTTS
from pydub import AudioSegment
import tempfile
from video_generator import generate_video
from post_tracker import load_processed_posts, save_processed_post

# Load environment variables
load_dotenv()

def setup_reddit_client():
    return praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT'),
        username=os.getenv('REDDIT_USERNAME'),
        password=os.getenv('REDDIT_PASSWORD')
    )

def generate_tts(title, text, output_path):
    # Replace "AITA" with "Am I the asshole" in the title
    title = re.sub(r'\bAITA\b', 'Am I the asshole', title, flags=re.IGNORECASE)
    
    # Generate full TTS with specified voice
    full_text = f"{title}. {text}"
    tts = gTTS(text=full_text, lang='en', tld='us', slow=False)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
        tts.save(temp_file.name)
        
        # Load the audio file
        audio = AudioSegment.from_mp3(temp_file.name)
        
        # Speed up the audio by 1.5x
        fast_audio = audio.speedup(playback_speed=1.5)
        
        # Take the first 30 seconds
        thirty_seconds = 30 * 1000  # pydub works in milliseconds
        first_30_seconds = fast_audio[:thirty_seconds]
        
        # Generate the "Watch the complete video" message
        watch_message = gTTS(text="Watch the complete video for full story", lang='en', tld='us', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as watch_temp_file:
            watch_message.save(watch_temp_file.name)
            watch_audio = AudioSegment.from_mp3(watch_temp_file.name)
            
            # Speed up the watch message by 1.5x
            fast_watch_audio = watch_audio.speedup(playback_speed=1.5)
            
            # Combine the first 30 seconds with the watch message
            final_audio = first_30_seconds + fast_watch_audio
            
            # Export the final audio
            final_audio.export(output_path, format="mp3")
            
        # Clean up temporary files
        os.unlink(watch_temp_file.name)
    
    os.unlink(temp_file.name)

def process_submissions(reddit, subreddit_name, num_posts, processed_posts):
    subreddit = reddit.subreddit(subreddit_name)
    processed_count = 0
    
    for submission in subreddit.hot(limit=100):  # Fetch up to 100 posts to ensure we get enough non-stickied ones
        if processed_count >= num_posts:
            break
        
        if not submission.stickied and submission.id not in processed_posts:
            success = process_submission(submission, processed_count + 1)
            if success:
                processed_count += 1
                save_processed_post('processed_posts.txt', submission.id)
    
    return processed_count

def process_submission(submission, count):
    print(f"Processing submission {count}: {submission.title}")
    search_query = extract_nouns(submission.title)
    image_url = search_image(search_query)
    
    if image_url:
        thumbnail_path = f"output/thumbnails/thumbnail_{count}.png"
        audio_path = f"output/audios/audio_{count}.mp3"
        video_path = f"output/videos/video_{count}.mp4"
        try:
            create_thumbnail(image_url, submission.title, thumbnail_path)
            generate_tts(submission.title, submission.selftext, audio_path)
            
            if os.path.exists(thumbnail_path) and os.path.exists(audio_path):
                print(f"Thumbnail created: {thumbnail_path}")
                print(f"Audio created: {audio_path}")
                
                # Generate video
                generate_video(audio_path, video_path)
                print(f"Video created: {video_path}")
                
                return True
            else:
                print(f"Thumbnail or audio creation failed.")
                return False
        except Exception as e:
            print(f"Error processing submission: {str(e)}")
            return False
    else:
        print("No suitable image found for the thumbnail.")
        return False

def main():
    reddit = setup_reddit_client()
    subreddit_name = "AmItheAsshole"  # You can change this to any subreddit you want
    
    # Ensure output directories exist
    os.makedirs("output/thumbnails", exist_ok=True)
    os.makedirs("output/audios", exist_ok=True)
    os.makedirs("output/videos", exist_ok=True)
    
    # Load processed posts
    processed_posts = load_processed_posts('processed_posts.txt')
    
    # Ask user for number of posts to process
    while True:
        try:
            num_posts = int(input("How many posts do you want to scrape and process? "))
            if num_posts > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    processed_count = process_submissions(reddit, subreddit_name, num_posts, processed_posts)
    
    if processed_count > 0:
        print(f"Successfully processed {processed_count} posts!")
    else:
        print("No posts were processed. Please check the error messages above.")

if __name__ == "__main__":
    main()
