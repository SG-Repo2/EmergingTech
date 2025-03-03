from sentence_transformers import SentenceTransformer

# Load the embedding model (will download on first use if not cached)
model_name = "sentence-transformers/all-MiniLM-L6-v2"
embedder = SentenceTransformer(model_name)