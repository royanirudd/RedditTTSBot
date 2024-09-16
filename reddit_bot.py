import praw
import os
from dotenv import load_dotenv
from thumbnail_generator import create_thumbnail, search_image, extract_nouns
from gtts import gTTS
from pydub import AudioSegment

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

def generate_tts(text, output_path):
    # Generate full TTS
    tts = gTTS(text)
    temp_path = "temp_audio.mp3"
    tts.save(temp_path)

    # Load the audio file
    audio = AudioSegment.from_mp3(temp_path)

    # Take the first 30 seconds
    thirty_seconds = 30 * 1000  # pydub works in milliseconds
    first_30_seconds = audio[:thirty_seconds]

    # Generate the "Watch the complete video" message
    watch_message = gTTS("Watch the complete video for full story")
    watch_message.save("watch_message.mp3")
    watch_audio = AudioSegment.from_mp3("watch_message.mp3")

    # Combine the first 30 seconds with the watch message
    final_audio = first_30_seconds + watch_audio

    # Export the final audio
    final_audio.export(output_path, format="mp3")

    # Clean up temporary files
    os.remove(temp_path)
    os.remove("watch_message.mp3")

def process_submissions(reddit, subreddit_name, num_posts):
    subreddit = reddit.subreddit(subreddit_name)
    processed_count = 0
    
    for submission in subreddit.hot(limit=100):  # Fetch up to 100 posts to ensure we get enough non-stickied ones
        if processed_count >= num_posts:
            break
        
        if not submission.stickied:
            success = process_submission(submission, processed_count + 1)
            if success:
                processed_count += 1
    
    return processed_count

def process_submission(submission, count):
    print(f"Processing submission {count}: {submission.title}")
    search_query = extract_nouns(submission.title)
    image_url = search_image(search_query)
    
    if image_url:
        thumbnail_path = f"output/thumbnail_{count}.png"
        audio_path = f"output/audio_{count}.mp3"
        try:
            create_thumbnail(image_url, submission.title, thumbnail_path)
            generate_tts(submission.selftext, audio_path)
            
            if os.path.exists(thumbnail_path) and os.path.exists(audio_path):
                print(f"Thumbnail created: {thumbnail_path}")
                print(f"Audio created: {audio_path}")
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
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
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
    
    processed_count = process_submissions(reddit, subreddit_name, num_posts)
    
    if processed_count > 0:
        print(f"Successfully processed {processed_count} posts!")
    else:
        print("No posts were processed. Please check the error messages above.")

if __name__ == "__main__":
    main()
