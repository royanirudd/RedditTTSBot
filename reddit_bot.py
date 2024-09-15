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
    
    # Ask user for number of posts to process
    while True:
        try:
            num_posts = int(input("How many posts do you want to scrape and make thumbnails for? "))
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
