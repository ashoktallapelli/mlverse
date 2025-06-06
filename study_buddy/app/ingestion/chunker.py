# Splits text into chunks

def chunk_text(text):
    return [text[i:i+500] for i in range(0, len(text), 500)]
