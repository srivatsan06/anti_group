import os
import shutil

# Files and directories to KEEP (Essential for the deployed app)
KEEP_FILES = {
    'app.py',
    'requirements.txt',
    '.gitignore',
    'README.md',
    'DEPLOYMENT.md',
    'QUICKSTART.md',
    'setup_remote.py',  # Useful for DB initialization
}

KEEP_DIRS = {
    '.streamlit',
    'models',
    'controllers',
    'services',
    'utils',
    'analytics_output',
    '.git',
    '.devcontainer',
    '__pycache__'
}

def cleanup():
    base_dir = os.getcwd()
    archive_dir = os.path.join(base_dir, '_archive')
    
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print(f"Created archive directory: {archive_dir}")

    files_moved = 0
    
    # List all files and directories in the root
    for item in os.listdir(base_dir):
        # Skip the archive directory itself
        if item == '_archive':
            continue
            
        item_path = os.path.join(base_dir, item)
        
        if os.path.isfile(item_path):
            if item not in KEEP_FILES:
                print(f"Moving file: {item}")
                shutil.move(item_path, os.path.join(archive_dir, item))
                files_moved += 1
        elif os.path.isdir(item_path):
            if item not in KEEP_DIRS:
                print(f"Moving directory: {item}")
                shutil.move(item_path, os.path.join(archive_dir, item))
                files_moved += 1
                
    print(f"\nCleanup complete. Moved {files_moved} items to {archive_dir}")
    print("Verify the app still works, then you can delete the '_archive' directory.")

if __name__ == "__main__":
    cleanup()
