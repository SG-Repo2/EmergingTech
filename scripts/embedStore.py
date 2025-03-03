import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# --- Load Cached Text ---
cache_path = "cache/sample.pdf.txt"
if not os.path.exists(cache_path):
    raise FileNotFoundError(f"Cache file not found: {cache_path}. Please run extract_text.py first.")

with open(cache_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Optionally, split the text into chunks
# For example, if your text contains a form-feed (\f) between pages:
chunks = text.split("\f")
print(f"Document split into {len(chunks)} chunks for embedding.")

# --- Initialize SentenceTransformer ---
model_name = "all-MiniLM-L6-v2"  # or "sentence-transformers/all-MiniLM-L6-v2"
# Force CPU usage to bypass MPS issues on macOS:
embedder = SentenceTransformer(model_name, device='cpu')

# Generate embeddings for each chunk
embeddings = embedder.encode(chunks, convert_to_numpy=True)
print("Embeddings computed. Shape:", embeddings.shape)

# --- Initialize ChromaDB ---
client = chromadb.Client(Settings(is_persistent=True, persist_directory="chromadb_data"))
collection = client.get_or_create_collection(name="pdf_collection")

# Create unique IDs for each chunk (e.g., "sample_chunk_0", "sample_chunk_1", etc.)
ids = [f"sample_chunk_{i}" for i in range(len(chunks))]

# Add documents (chunks) and their embeddings to the collection
collection.add(
    documents=chunks,
    embeddings=embeddings.tolist(),
    ids=ids
)

print(f"Added {len(chunks)} embeddings to ChromaDB collection 'pdf_collection'.")

print("Collection count:", collection.count())
# Or fetch by ID to see if data round-trips
test_id = ids[0]
result = collection.get(ids=[test_id])
print("Retrieved by ID:", result['documents'][0][:100], "...")