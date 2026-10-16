def chunk_pages(pages, chunk_size=500, overlap=100):
    chunks = []
    #loop through each page dictionary in pages 
    for page in pages:
        #get the text,page number and source from that page
        text = page["text"]
        page_number = page["page"]
        source = page["source"]
        #start with position 0
        start = 0
        #while start is less than the length of the text
        while start < len(text):
            #calculate the end position
            end = start + chunk_size
            #cut a piece of text using slicing
            chunk_text = text[start:end]
            #add a dictionary to chunks
            chunks.append({
                "text": chunk_text,
                "page": page_number,
                "source": source
            })
            #move forward,keeping the overlap
            start += chunk_size - overlap
    return chunks 
if __name__ == "__main__":
    from src.ingestion.pdf_reader import load_pdf
    pages = load_pdf("Data/papers/raw/Lesson01-Introduction.pdf")
    result = chunk_pages(pages)
    print("Chunks made:", len(result))
    print(result[0])           
