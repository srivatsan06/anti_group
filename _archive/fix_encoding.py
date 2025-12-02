import os

TARGET_DIRS = ['models', 'utils', 'services']

def fix_encoding_line(content):
    """Remove the orphaned 'utf-8' line at the start."""
    lines = content.split('\n')
    if lines and lines[0].strip() == 'utf-8':
        lines = lines[1:]
    return '\n'.join(lines)

def main():
    base_dir = os.getcwd()
    
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
                        new_content = fix_encoding_line(content)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
    print("Done.")

if __name__ == "__main__":
    main()
