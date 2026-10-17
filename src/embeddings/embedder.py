from sentence_transformers import SentenceTransformer


def embed_chunks(chunks, model_name="all-MiniLM-L6-v2"):
    #load the embedding model
    model = SentenceTransformer(model_name)

    #extract the text from every chunk
    texts = [chunk["text"]for chunk in chunks]

    #convert the texts into numerical embeddings
    embeddings = model.encode(texts)

    #loop through chunks and their embeddings together
    for chunk, embedding in zip(chunks, embeddings):

        #save each embedding inside its chunk
        chunk["embedding"] = embedding.tolist()

    return chunks 

if __name__ == "__main__":
    from src.ingestion.pdf_reader import load_pdf
    from src.chunking.chunker import chunk_pages

    #load the pdf,split it into chunks and embed them
    pages = load_pdf("Data/papers/raw/Lesson01-Introduction.pdf")
    chunks = chunk_pages(pages)
    embedded_chunks = embed_chunks(chunks)

    #print the number of chunks and embedding dimensions
    print("Number of chunks:",len(embedded_chunks))
    print("Numbers in first embedding:", len(embedded_chunks[0]["embedding"]))
