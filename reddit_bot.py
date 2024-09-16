import praw
import os
import re
from dotenv import load_dotenv
from thumbnail_generator import create_thumbnail, search_image, extract_nouns
from gtts import gTTS
from pydub import AudioSegment
import tempfile
from video_generator import generate_short_video, generate_long_video
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

def generate_tts(title, text, output_path, long_video=False):
    # Replace "AITA" with "Am I the A-hole" in both title and text
    title = re.sub(r'\bAITA\b', 'Am I the A-hole', title, flags=re.IGNORECASE)
    text = re.sub(r'\bAITA\b', 'Am I the A-hole', text, flags=re.IGNORECASE)
    
    # Generate full TTS with specified voice
    full_text = f"{title}. {text}"
    tts = gTTS(text=full_text, lang='en', tld='us', slow=False)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
        tts.save(temp_file.name)
        
        # Load the audio file
        audio = AudioSegment.from_mp3(temp_file.name)
        
        # Speed up the audio by 1.5x
        fast_audio = audio.speedup(playback_speed=1.5)
        
        if not long_video:
            # Take the first 30 seconds for short videos
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
        else:
            # For long video, use the entire audio
            fast_audio.export(output_path, format="mp3")
    
    os.unlink(temp_file.name)

def process_submissions(reddit, subreddit_name, num_posts, processed_posts):
    subreddit = reddit.subreddit(subreddit_name)
    processed_count = 0
    long_audio_paths = []
    
    for submission in subreddit.hot(limit=100):  # Fetch up to 100 posts to ensure we get enough non-stickied ones
        if processed_count >= num_posts:
            break
        
        if not submission.stickied and submission.id not in processed_posts:
            success, long_audio_path = process_submission(submission, processed_count + 1)
            if success:
                processed_count += 1
                save_processed_post('processed_posts.txt', submission.id)
                long_audio_paths.append(long_audio_path)
    
    # Generate long video
    if long_audio_paths:
        long_video_path = "output/longvids/long_video.mp4"
        generate_long_video(long_audio_paths, long_video_path)
        print(f"Long video created: {long_video_path}")
    
    return processed_count

def process_submission(submission, count):
    print(f"Processing submission {count}: {submission.title}")
    search_query = extract_nouns(submission.title)
    image_url = search_image(search_query)
    
    if image_url:
        thumbnail_path = f"output/thumbnails/thumbnail_{count}.png"
        short_audio_path = f"output/audios/short_audio_{count}.mp3"
        long_audio_path = f"output/audios/long_audio_{count}.mp3"
        short_video_path = f"output/shortvids/video_{count}.mp4"
        try:
            create_thumbnail(image_url, submission.title, thumbnail_path)
            generate_tts(submission.title, submission.selftext, short_audio_path)
            generate_tts(submission.title, submission.selftext, long_audio_path, long_video=True)
            
            if os.path.exists(thumbnail_path) and os.path.exists(short_audio_path) and os.path.exists(long_audio_path):
                print(f"Thumbnail created: {thumbnail_path}")
                print(f"Short audio created: {short_audio_path}")
                print(f"Long audio created: {long_audio_path}")
                
                # Generate short video
                generate_short_video(short_audio_path, short_video_path)
                print(f"Short video created: {short_video_path}")
                
                return True, long_audio_path
            else:
                print(f"Thumbnail or audio creation failed.")
                return False, None
        except Exception as e:
            print(f"Error processing submission: {str(e)}")
            return False, None
    else:
        print("No suitable image found for the thumbnail.")
        return False, None

def main():
    reddit = setup_reddit_client()
    subreddit_name = "AmItheAsshole"  # You can change this to any subreddit you want
    
    # Ensure output directories exist
    os.makedirs("output/thumbnails", exist_ok=True)
    os.makedirs("output/audios", exist_ok=True)
    os.makedirs("output/shortvids", exist_ok=True)
    os.makedirs("output/longvids", exist_ok=True)
    
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
        print(f"Created {processed_count} short videos and 1 long video.")
    else:
        print("No posts were processed. Please check the error messages above.")

if __name__ == "__main__":
    main()
