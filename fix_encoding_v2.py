import os
import re

TARGET_DIRS = ['models', 'utils', 'services']

def fix_encoding_artifacts(content):
    """Remove all 'utf-8' encoding artifacts from the start of files."""
    # Handle case 1: utf-8 on its own line
    if content.startswith('utf-8\n'):
        content = content[6:]  # len('utf-8\n') = 6
    elif content.startswith('utf-8\r\n'):
        content = content[7:]  # len('utf-8\r\n') = 7
    # Handle case 2: utf-8 merged with next line (no newline)
    elif content.startswith('utf-8'):
        content = content[5:]  # len('utf-8') = 5
    
    return content

def main():
    base_dir = os.getcwd()
    fixed_count = 0
    
    for d in TARGET_DIRS:
        dir_path = os.path.join(base_dir, d)
        if not os.path.exists(dir_path):
            continue
            
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if content.startswith('utf-8'):
                        print(f"Fixing {file_path}...")
                        new_content = fix_encoding_artifacts(content)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        fixed_count += 1
                        
    print(f"Done. Fixed {fixed_count} files.")

if __name__ == "__main__":
    main()
