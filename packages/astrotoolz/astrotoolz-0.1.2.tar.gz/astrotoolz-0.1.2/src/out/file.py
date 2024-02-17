def to_text_file(filename: str, text: str):
    with open(filename, 'w') as f:
        f.write(text)
