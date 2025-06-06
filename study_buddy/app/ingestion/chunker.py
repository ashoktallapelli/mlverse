# Splits text into chunks

def chunk_text(text, chunk_size=500, overlap=50):
    # Ensure the overlap is not greater than the chunk size
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks
