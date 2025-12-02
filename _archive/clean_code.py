import os
import re
import tokenize
import io

TARGET_DIRS = ['models', 'utils', 'services']

def remove_comments_and_docstrings(source):
    """
    Parses the source code and removes comments and docstrings.
    """
    io_obj = io.BytesIO(source.encode('utf-8'))
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    
    try:
        tokens = list(tokenize.tokenize(io_obj.readline))
    except tokenize.TokenError:
        print("TokenError, skipping file content modification")
        return source

    for i, tok in enumerate(tokens):
        token_type = tok.type
        token_string = tok.string
        start_line, start_col = tok.start
        end_line, end_col = tok.end
        
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += " " * (start_col - last_col)
            
        if token_type == tokenize.ENCODING:
            continue
            
        if token_type == tokenize.COMMENT:
            pass
        elif token_type == tokenize.STRING:
            # Check if it's a docstring
            # A docstring is a string literal that appears as a statement
            is_docstring = False
            
            # Look backwards for the previous meaningful token
            j = i - 1
            while j >= 0:
                if tokens[j].type in (tokenize.NL, tokenize.COMMENT, tokenize.NEWLINE):
                    j -= 1
                    continue
                break
            
            prev_meaningful_type = tokens[j].type if j >= 0 else tokenize.ENCODING
            
            if prev_meaningful_type in (tokenize.INDENT, tokenize.ENCODING):
                is_docstring = True
            elif prev_meaningful_type == tokenize.OP and tokens[j].string == ':':
                is_docstring = True
            
            if is_docstring:
                pass
            else:
                out += token_string
        else:
            out += token_string
            
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
        
    # Post-processing to remove empty lines created by removal
    lines = out.split('\n')
    cleaned_lines = [line for line in lines if line.strip()]
    return '\n'.join(cleaned_lines) + '\n'

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
