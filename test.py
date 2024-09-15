import praw
import os
from dotenv import load_dotenv
from thumbnail_generator import create_thumbnail, search_image, extract_nouns

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

def process_first_non_stickied_submission(reddit, subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.hot(limit=10):  # Check first 10 posts
        if not submission.stickied:
            return process_submission(submission)
    print("No non-stickied posts found in the first 10 hot posts.")
    return False

def process_submission(submission):
    print(f"Processing submission: {submission.title}")
    search_query = extract_nouns(submission.title)
    image_url = search_image(search_query)
    
    if image_url:
        thumbnail_path = f"output/test_{submission.id}.png"
        try:
            create_thumbnail(image_url, submission.title, thumbnail_path)
            
            if os.path.exists(thumbnail_path):
                print(f"Thumbnail created: {thumbnail_path}")
                return True
            else:
                print(f"Thumbnail creation failed: '{thumbnail_path}' was not created.")
                return False
        except Exception as e:
            print(f"Error creating thumbnail: {str(e)}")
            return False
    else:
        print("No suitable image found for the thumbnail.")
        return False

def main():
    reddit = setup_reddit_client()
    subreddit_name = "AmItheAsshole"  # You can change this to any subreddit you want
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    success = process_first_non_stickied_submission(reddit, subreddit_name)
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
