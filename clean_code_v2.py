import os
import re

TARGET_DIRS = ['models', 'utils', 'services']

def remove_comments_and_docstrings(content):
    """Remove comments and docstrings from Python code using regex."""
    lines = content.split('\n')
    cleaned_lines = []
    in_multiline_string = False
    multiline_quote = None
    skip_next_string = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip encoding declarations at the start
        if i == 0 and (stripped.startswith('#') and 'coding' in stripped.lower()):
            continue
            
        # Skip module-level docstrings (first non-empty line after encoding)
        if i <= 2 and (stripped.startswith('"""') or stripped.startswith("'''")):
            if stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                # Single-line docstring
                continue
            else:
                # Start of multi-line docstring
                in_multiline_string = True
                multiline_quote = '"""' if '"""' in stripped else "'''"
                continue
        
        # Handle multi-line strings
        if in_multiline_string:
            if multiline_quote in line:
                in_multiline_string = False
                multiline_quote = None
            continue
        
        # Remove inline comments
        if '#' in line:
            # Check if it's actually a comment (not in a string)
            in_string = False
            quote_char = None
            new_line = []
            
            for j, char in enumerate(line):
                if char in ('"', "'") and (j == 0 or line[j-1] != '\\'):
                    if not in_string:
                        in_string = True
                        quote_char = char
                    elif char == quote_char:
                        in_string = False
                        quote_char = None
                
                if char == '#' and not in_string:
                    break
                    
                new_line.append(char)
            
            line = ''.join(new_line).rstrip()
        
        # Only add non-empty lines
        if line.strip():
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines) + '\n' if cleaned_lines else ''

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
                    print(f"Cleaning {file_path}...")
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    new_content = remove_comments_and_docstrings(content)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        
    print("Done cleaning files.")

if __name__ == "__main__":
    main()
