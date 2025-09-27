import os

def text_to_speech(folder):
    print(folder)

def create_reel(folder):
    print(folder)

if __name__ == "__main__":
    # Check if done.txt exists
    if not os.path.exists("done.txt"):
        # Create an empty done.txt if it doesn't exist
        with open("done.txt", "w") as f:
            pass

    # Read the contents of done.txt
    with open("done.txt", "r") as f:
        done_folders = f.readlines()

    folders = os.listdir("user_uploads")
    for folder in folders:
        if folder not in done_folders:
            text_to_speech(folder)
            create_reel(folder)