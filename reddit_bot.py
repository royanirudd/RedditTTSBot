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

def process_subreddit(reddit, subreddit_name, limit=10):
    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.hot(limit=limit):
        if not submission.stickied and not submission.is_self:
            process_submission(submission)

def process_submission(submission):
    print(f"Processing submission: {submission.title}")
    search_query = extract_nouns(submission.title)
    image_url = search_image(search_query)
    
    if image_url:
        thumbnail_path = f"output/{submission.id}.png"
        create_thumbnail(image_url, submission.title)
        os.rename("thumbnail.png", thumbnail_path)
        print(f"Thumbnail created: {thumbnail_path}")
        # Here you would typically upload the thumbnail and post it
        # This part depends on where you want to share the thumbnails
    else:
        print("No suitable image found for the thumbnail.")

def main():
    reddit = setup_reddit_client()
    subreddit_name = "AmItheAsshole"  # You can change this to any subreddit you want
    process_subreddit(reddit, subreddit_name)

if __name__ == "__main__":
    main()
