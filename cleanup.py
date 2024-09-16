import os
import shutil

def delete_files_in_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} does not exist.")
        return

    files = os.listdir(folder_path)
    if not files:
        print(f"Folder {folder_path} is already empty.")
        return

    print(f"\nProcessing folder: {folder_path}")
    for file in files:
        file_path = os.path.join(folder_path, file)
        response = input(f"Delete {file}? (y/n/a for all): ").lower()
        if response == 'y':
            os.remove(file_path)
            print(f"Deleted: {file}")
        elif response == 'a':
            shutil.rmtree(folder_path)
            os.makedirs(folder_path)
            print(f"All files in {folder_path} have been deleted.")
            return True
        else:
            print(f"Skipped: {file}")
    return False

def clear_processed_posts():
    file_path = 'processed_posts.txt'
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted {file_path}")
        print("Cache of scraped posts has been cleared.")
    else:
        print(f"{file_path} does not exist. No cache to clear.")

def main():
    folders = [
        "output/audios",
        "output/shortvids",
        "output/longvids",
        "output/thumbnails"
    ]

    delete_all = False

    for folder in folders:
        if delete_all:
            shutil.rmtree(folder, ignore_errors=True)
            os.makedirs(folder, exist_ok=True)
            print(f"All files in {folder} have been deleted.")
        else:
            delete_all = delete_files_in_folder(folder)

    print("\nCleanup of output folders completed.")

    # Prompt for clearing cache of scraped posts
    clear_cache = input("\nDo you want to clear the cache of scraped posts? (y/n): ").lower()
    if clear_cache == 'y':
        clear_processed_posts()
    else:
        print("Cache of scraped posts was not cleared.")

    print("\nCleanup process completed.")

if __name__ == "__main__":
    main()
