import chromadb

# Open the same database that your app writes to
client = chromadb.PersistentClient(path="Data/vectorstore")

# Open the collection called "lessons"
collection = client.get_collection(name="lessons")

# Get the metadata (source and page) of every chunk
data = collection.get(include=["metadatas"])

# Collect each file name only once, and sort them
sources = sorted({item["source"] for item in data["metadatas"]})

# Print them one per line
for source in sources:
    print(source)