import os

def load_processed_posts(file_path):
    if not os.path.exists(file_path):
        return set()
    with open(file_path, 'r') as file:
        return set(file.read().splitlines())

def save_processed_post(file_path, post_id):
    with open(file_path, 'a') as file:
        file.write(f"{post_id}\n")
