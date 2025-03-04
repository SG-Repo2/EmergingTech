# Comprehensive Research Plan for Local PDF Processing and Research System on macOS M3

## 1. System Overview & Environment Setup

**Hardware & OS:** The target system is a Mac with an Apple M3 (Sequoia 04) chip and 36 GB RAM, running macOS (Apple Silicon architecture). This provides ample memory for handling multiple PDFs, in-memory embeddings, and caching results. The Apple M3’s performance will accelerate local computations (text extraction, embedding generation) and 36 GB RAM ensures the vector database can operate efficiently in-memory for sizable document collections.

**Environment Goals:** We will set up a local-first PDF processing pipeline using Python and open-source libraries. All heavy tasks (PDF parsing, embedding, search) run locally without external API calls. We’ll use Homebrew to manage system packages (like Python and Git) on macOS for consistency.

**Homebrew Installation:** If Homebrew is not already installed, install it by running the official script in Terminal:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, ensure Homebrew’s bin is in your PATH (Homebrew will prompt if needed). For Apple Silicon Macs, Homebrew typically installs to `/opt/homebrew`; the install script above handles this. Now update Homebrew and install required tools:

*   **Python 3 (latest stable)** – macOS’s system Python is outdated, so install a new one via Homebrew:

    ```bash
    brew update
    brew install python
    ```

    This will install the latest Python 3 (and pip) and symlink it as `python3` (and set `pip3`). You can verify by checking the version: `python3 --version` (should report Python 3.x).

*   **Git** – for version control and downloading any repositories or files if needed:

    ```bash
    brew install git
    ```

    Verify Git is installed with `git --version`. (Optional: configure your Git name/email with `git config --global user.name "Your Name"`)

*   **Developer Tools** – Xcode Command Line Tools might be required for building some Python packages (for example, compiling native code). On a new Mac, run:

    ```bash
    xcode-select --install
    ```

    This ensures compilers are available. (Homebrew may prompt this as well.)

**Python Environment:** It’s recommended to use a virtual environment for Python to isolate this project’s dependencies. Create and activate a virtualenv using the Homebrew-installed Python:

```bash
python3 -m venv venv           # create virtual environment in folder 'venv'
source venv/bin/activate       # activate the virtual environment
```

After activation, the `python` and `pip` commands will refer to the venv’s Python. Upgrade pip and setuptools inside the venv:

```bash
pip install --upgrade pip setuptools wheel
```

Now we will install the necessary Python libraries for each module.

## 2. Module Breakdown & Detailed Steps

### 2.1 Local-First Setup (Dependencies Installation)
[COMPLETED AND FINALIZED]

**Packages to Install:** We will use the following key Python packages (with suggested versions) for our system:

*   **ChromaDB** (`chromadb`) – local vector database for embeddings (e.g. version 0.4.5 or latest).
*   **PyMuPDF** (`PyMuPDF`) – PDF extraction library (e.g. 1.25.3).
*   **Sentence-Transformers** (`sentence-transformers`) – for embedding text (e.g. 3.4.0).
*   **spaCy** (`spacy`) – NLP library for text processing and entity extraction (e.g. 3.8.4).
*   **LangChain** (`langchain`) – higher-level framework for chaining operations (e.g. 0.3.19).
*   **PyVis** (`pyvis`) – for network/graph visualization (e.g. 0.3.2).
*   **NetworkX** (`networkx`) – (optional) for easier graph construction to pass into pyvis.

Pinning versions as above helps ensure compatibility. These versions are known to work with Python 3.9+ and each other. Now, install all via pip:

```bash
pip install chromadb==0.4.5 PyMuPDF==1.25.3 sentence-transformers==3.4.0 spacy==3.8.4 langchain==0.3.19 pyvis==0.3.2 networkx==3.1
```

This single command installs all required libraries. You should see pip downloading each package and its dependencies. Key points:

*   ChromaDB will install its core and any needed dependencies (like `chromadb-hnswlib` for similarity search). It requires Python ≥3.9 and SQLite ≥3.35 (which Python 3.11+ satisfies).
*   PyMuPDF (also imported as `fitz`) should install with no external dependencies needed.
*   `sentence-transformers` will pull in PyTorch (for the transformer model backend). On Apple Silicon, this may download a compatible wheel (ensure an internet connection). If PyTorch doesn’t have a prebuilt wheel for Python 3.x on M3, pip might try to compile – if so, ensure the Xcode tools are installed as above. You can also install PyTorch separately if needed (e.g., `pip install torch`).
*   spaCy will install the library but not the language model data by default (we handle that next).
*   LangChain is pure Python and should install smoothly (along with any sub-dependencies it uses for integrations).
*   PyVis and NetworkX are straightforward; pyvis uses jupyterlab and networkx internally for some functionalities but those are usually optional.

After installation, verify that all packages are available. Launch a Python REPL (`python`) and try importing each:

```python
import chromadb, fitz, spacy, sentence_transformers, langchain, pyvis
print("All libraries loaded successfully")
```

If no errors occur, the environment is set up correctly. (Note: `fitz` is the import name for PyMuPDF, and `sentence_transformers` is the import for Sentence Transformers.)

**Language Model Data (spaCy):** Download spaCy’s English model for NLP. We’ll use the small English model `en_core_web_sm` for entity extraction. Run the download command:

```bash
python -m spacy download en_core_web_sm
```

This downloads the model package and links it to spaCy. If this command prints an error about not finding spacy, ensure you ran it in the active venv and with `python -m`. Once complete, you can test loading it in Python:

```python
import spacy
nlp = spacy.load("en_core_web_sm")
print("SpaCy model loaded:", nlp.meta["name"])
```

It should output “en_core_web_sm”. (If download fails due to firewall or no internet, you can manually install the model via pip using a direct URL, but the spacy download command is simpler.)

**Configuration & Setup:** At this stage, we have all required libraries installed. It’s useful to structure our project directory:

```
project_root/
├── PDFs/           # put your PDF documents here
├── cache/          # cache files (extracted text, etc.)
├── venv/           # Python virtual environment
├── scripts/        # Python scripts for each module
└── outputs/        # e.g., for graphs or other results
```

Create directories for your PDFs and for cache/outputs. In our examples below, we’ll assume file paths accordingly.

Make sure to activate the virtual environment whenever working on this project so that the correct dependencies are used. You can add an alias or update your shell profile to ease activation if needed.

### 2.2 Enhanced PDF Processing with Caching
[COMPLETED AND FINALIZED]

In this module, we focus on extracting text from PDFs using PyMuPDF and caching the results for efficiency. The goal is to avoid re-processing PDFs on each run by storing their extracted text locally.

**Step 1: PDF Text Extraction** – We use PyMuPDF (`fitz`) to read the PDF pages and extract text. PyMuPDF is very fast and retains layout ordering reasonably well. A simple extraction script:

```python
import fitz  # PyMuPDF
import os

pdf_path = "PDFs/sample.pdf"
cache_dir = "cache/"
os.makedirs(cache_dir, exist_ok=True)

# Derive a cache file path, e.g., "cache/sample.pdf.txt"
pdf_name = os.path.basename(pdf_path)
text_cache_path = os.path.join(cache_dir, pdf_name + ".txt")

text = ""
if os.path.exists(text_cache_path):
    # If cache exists, read from it instead of re-extracting
    with open(text_cache_path, 'r', encoding='utf-8') as f:
        text = f.read()
    print(f"Loaded cached text for {pdf_name}")
else:
    # Extract text from PDF
    doc = fitz.open(pdf_path)
    all_text = []
    for page in doc:
        page_text = page.get_text()  # extract text from page
        all_text.append(page_text)
    text = "\f".join(all_text)  # join pages with form feed (optional)
    # Save to cache file
    with open(text_cache_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Extracted text from {pdf_name} and saved to cache.")
```

**Explanation:** We open the PDF, iterate through each page, and use `page.get_text()` to get the text content. We join all pages with a form-feed (`\f`) delimiter just to preserve page boundaries (this is a technique suggested in PyMuPDF docs, where `chr(12)` is form-feed). The extracted text is then written to a `.txt` file under `cache/`. The next time the script runs, if the `.txt` exists, it will skip extraction and load the text directly (this cache check uses `os.path.exists`).

*   **File Naming Convention:** We name the cache file after the PDF (e.g., `sample.pdf.txt`). For multiple PDFs, this scheme keeps one text file per PDF. Ensure the cache directory is separate from original PDFs to avoid confusion.

**Step 2: Verify Extraction** – After running the script for a PDF, open the resulting `.txt` file to confirm it contains the text. You can also print the first few hundred characters in the script to visually inspect, e.g. `print(text[:500])`. The output might not be perfectly formatted (PDF text often has line breaks or spacing issues), but that’s fine for embedding purposes. If the PDF was scanned (image PDF), PyMuPDF will not extract text (it would return empty string) because there is no embedded text. In such cases, an OCR step would be needed (PyMuPDF can perform OCR if Tesseract is installed, but that’s beyond our current scope).

**Step 3: Caching Mechanism** – The benefit of caching is significant. For large PDFs, text extraction can be time-consuming, but by saving to a text file, subsequent runs can load the text in seconds. The logic above prints a message whether it did extraction or used the cache, so you know what happened. Make sure to re-extract (e.g., by deleting the cache file) if the PDF content updates or if you suspect an issue with a previous extraction.

**Tip:** You can extend this approach to many PDFs by looping through all files in the `PDFs/` directory and processing each one similarly. Each PDF’s text can then be cached and later used for embeddings.

### 2.3 Local Embeddings and Vector Database Integration
[COMPLETED AND FINALIZED]

With text data available, we move to generating embeddings for that text and storing them in a local vector database (ChromaDB) for efficient similarity search.

**Step 1: SentenceTransformer Model Setup** – We’ll use SentenceTransformers to convert text into numerical embeddings (vectors). Choose a model appropriate for sentence or paragraph embeddings. A good default is `"all-MiniLM-L6-v2"` which is lightweight and was, in fact, ChromaDB’s default as well. Initialize the model:

```python
from sentence_transformers import SentenceTransformer

# Load the embedding model (will download on first use if not cached)
model_name = "sentence-transformers/all-MiniLM-L6-v2"
embedder = SentenceTransformer(model_name)
```

When you run this the first time, it will download the model files to your machine (likely under `~/.cache/torch/sentence_transformers/`). This is a one-time download (~90MB). Ensure internet access for this step. If you want to cache the model offline, you can download it separately or keep the `.cache` directory for reuse. If downloading is problematic, you could alternatively choose the model `all-MiniLM-L6-v2` via Hugging Face’s transformers or use a local path, but using the SentenceTransformer API is simplest.

**Step 2: Splitting Text (if needed)** – Decide how to break your text into chunks for embedding. For many research use-cases, embedding the entire document as one vector might be too coarse. Often, splitting the text by sections, paragraphs, or a fixed token length is useful so that the vector search can retrieve specific portions. For simplicity, let’s assume each page (or each significant section) is a separate chunk since we joined text with form-feeds. We can split on `\f` to get page-wise text:

```python
# Suppose 'text' is the content of sample.pdf from previous step
pages = text.split("\f")  # list of page texts
print(f"Document split into {len(pages)} pages for embedding.")
```

Alternatively, one could split by paragraphs or use nltk or spaCy sentence segmentation for finer chunks. For a first iteration, page-level or section-level chunks are okay.

**Step 3: Generate Embeddings** – Now use the model to encode the text chunks into vectors:

```python
documents = pages  # or any list of text segments
embeddings = embedder.encode(documents, convert_to_numpy=True)
print("Embedding shape:", embeddings.shape)
```

This will output a NumPy array of shape `(n_documents, embedding_dim)`. For the MiniLM model, `embedding_dim` is 384. The `SentenceTransformer.encode` method can take a list of strings and process them in batches. We set `convert_to_numpy=True` to get a NumPy array (which is convenient for storing in Chroma). Make sure your machine has enough RAM; each vector is 384 floats (about 1.5KB each), so even 10,000 such vectors is ~15 MB – well within our 36 GB RAM.

**Step 4: Initialize ChromaDB (Local Vector Store)** – Now that we have embeddings, we’ll store them in ChromaDB for similarity search. We use Chroma in “persistent” mode so that the index is saved to disk (so we don’t have to re-embed everything each time). Set up a Chroma client:

```python
import chromadb
from chromadb.config import Settings

# Initialize Chroma in persistent mode, storing data in ./chromadb_data directory
client = chromadb.Client(Settings(is_persistent=True, persist_directory="chromadb_data"))
```

This configuration ensures that all vectors and indexes are saved under `chromadb_data/` on disk. (By default, without `is_persistent=True`, Chroma runs in-memory and data would be lost on exit.) The first time you run this, the directory will be created and will contain a SQLite database and index files.

**Step 5: Create a Collection and Insert Embeddings** – Chroma organizes vectors into collections. We’ll create a collection for our PDF (or you could name it for a set of documents, e.g., “research_papers”). For example:

```python
collection = client.get_or_create_collection(name="pdf_collection")
```

Using `get_or_create_collection` is handy to avoid duplicates if it already exists. Now add our document vectors:

```python
# Prepare metadata or IDs for each document
ids = [f"{pdf_name}_page{idx}" for idx in range(len(documents))]
collection.add(documents=documents, embeddings=embeddings.tolist(), ids=ids)
print(f"Added {len(documents)} embeddings to Chroma collection.")
```

We provide the raw text (`documents` list), the embeddings (converted to list of lists for compatibility), and unique ids for each entry (here we use `filename_page#` as an identifier). Chroma will store the texts, embeddings, and IDs. If you don’t pass embeddings, Chroma would attempt to generate them using an internal embedding function if configured. By default it uses 'all-MiniLM-L6-v2' under the hood, but we explicitly supply embeddings to ensure we control the model and can reuse the embedder for queries.

Chroma will handle indexing these vectors (using an HNSW index) so that we can query by similarity. The `collection.add` call may take a moment if you have many vectors, as it builds the index.

**Step 6: Configuration & Meta** – We didn’t add any metadata other than IDs, but you could. For instance, if you have multiple PDFs, you could include metadata like `{"source": "sample.pdf", "page": 1}` for each vector. Chroma supports filtering by metadata in queries, which can be powerful if your vector store has many documents of different types. In our simple case, we might not need it yet. Just be aware it’s possible.

**Step 7: Testing the Vector Store** – It’s good to test that the collection is working. You can check the count of items:

```python
print("Collection count:", collection.count())
# Or fetch by ID to see if data round-trips
test_id = ids[0]
result = collection.get(ids=[test_id])
print("Retrieved by ID:", result['documents'][0][:100], "...")
```

The above should retrieve the document text for `test_id` from the store, confirming that our data is saved.

**Troubleshooting:**

*   If `pip install chromadb` failed with an error about building `chromadb-hnswlib`, it’s likely a compilation issue on Apple Silicon. Ensure you have cmake installed (`brew install cmake`) and try again. Also, setting an environment variable to avoid a known clang flag issue can help: `export HNSWLIB_NO_NATIVE=1` before installing will skip using certain native optimizations that clang on Mac might not support.
*   If Chroma still fails, consider using a slightly older version (e.g., 0.3.x) as a fallback, or check the Chroma docs for any Apple Silicon specific notes. However, as of version 0.4+, these issues are largely resolved and the SQLite persistence is stable.
*   If the SentenceTransformer model fails to download (or if you’re offline), you can manually download the model from the HuggingFace Hub and load it from the local path: `SentenceTransformer('/path/to/model')`. Ensure the path contains the model files (`config.json`, `pytorch_model.bin`, etc.).

### 2.4 Research Prompt Generation and Integration

**[Active Stage]** This module bridges the local system with an external AI (ChatGPT web interface) by forming a research prompt using data from our PDF. The idea is to leverage the extracted knowledge to ask better questions.

**Initial Plan/Thoughts:**

*   Overarching research objective: To guide the user in creating a prompt that provides context to ChatGPT, followed by a specific query, thereby enhancing the quality of ChatGPT's responses.
*   Key next steps:
    *   Develop a refined prompt template that incorporates user-defined research questions.
    *   Implement a function to automate the retrieval of relevant context from the vector database based on the research question.
    *   Integrate the prompt generation function into the existing workflow, allowing users to easily create and refine prompts for ChatGPT.

### 2.5 Search, Query, and Visualization

This module covers performing similarity search queries on the local vector database and creating visualizations (namely, an entity relationship graph) from the data to aid research.

**Search & Query (Vector Similarity):** Now that our data is embedded in ChromaDB, we can query it using natural language to find relevant passages.

**Step 1: Formulate a Query** – For a given user query or topic, embed the query text with the same model:

```python
query = "What are the main conclusions about climate change mitigation?"
query_embedding = embedder.encode([query])
```

**Step 2: Query ChromaDB** – Use `collection.query` to find similar vectors:

```python
results = collection.query(
    query_embeddings=query_embedding,
    n_results=5,
    include=["documents", "distances"]
)
top_docs = results["documents"][0]   # list of top matching documents (text chunks)
distances = results["distances"][0]  # similarity scores (lower = more similar if using cosine distance)
```

Here we ask for the 5 nearest neighbors. We included `distances` to see how close the matches are (Chroma uses cosine similarity by default, but returns distance = 1 - cosine_sim for each result). You can loop through `top_docs` and print snippets:

```python
for doc, dist in zip(top_docs, distances):
    print(f"Score {dist:.2f} -> {doc[:200]}...")
```

This will show the top matching excerpts. Review these to ensure they are relevant. These excerpts are what you’d include in the prompt to ChatGPT (Module 4). If some results are irrelevant, you might try using filters or modifying the query. For example, if you have metadata, you could filter by document source or section.

**Step 3: (Optional) Use LangChain for QA** – Although our plan is to use ChatGPT via web, note that with LangChain installed, one could directly integrate an LLM for Q&A. LangChain can take the ChromaDB as a retriever and an LLM (like GPT-4 via API) to answer questions. While we won’t implement that here (since we assume manual ChatGPT usage), our environment is prepared for it. This is an extensibility point: if the user later acquires an OpenAI API key or uses a local LLM, LangChain could orchestrate an automated answer chain.

**Visualization (Entity Relationship Graph):** To complement text queries, we can visualize relationships in the document via a graph of named entities. This can help identify key players, topics, and their interconnections in the PDF.

**Step 4: Extract Named Entities with spaCy** – We use spaCy to find entities (people, organizations, places, etc.) in the text:

```python
import spacy
nlp = spacy.load("en_core_web_sm")

doc = nlp(text)  # 'text' is the full text of the PDF from cache
entities = [ent.text for ent in doc.ents]
print(f"Found {len(entities)} entities, {len(set(entities))} unique.")
```

We get a list of all entity strings. Likely many repeats exist (e.g., “United Nations” might appear multiple times). We’ll use these to build a graph.

**Step 5: Build Relationships** – Define a simple heuristic for relationships: if two entities appear in the same sentence, we’ll create an edge between them in a graph (meaning they are contextually related). For example, if a sentence says “Alice partnered with Bob at Company X,” we connect Alice–Bob, Alice–Company X, and Bob–Company X.

```python
import itertools
edges = set()
for sent in doc.sents:
    ent_texts = [ent.text for ent in sent.ents]
    # create all pair combinations of entities in this sentence
    for a, b in itertools.combinations(set(ent_texts), 2):
        edges.add((a, b))
```

We use a set of `ent_texts` to avoid self-pairs or duplicate pairs in the same sentence. The result `edges` is a set of tuples like `(entity1, entity2)` that co-occur.

**Step 6: Visualize with PyVis** – Now use PyVis to create an interactive network graph:

```python
from pyvis.network import Network

net = Network(height="600px", width="100%", notebook=False)
net.barnes_hut()  # use Barnes-Hut physics model for nicer layout (good for medium-sized graphs)

# Add nodes for each unique entity
unique_entities = set([ent.text for ent in doc.ents])
for ent in unique_entities:
    net.add_node(ent, label=ent)

# Add edges for each relationship
for a, b in edges:
    net.add_edge(a, b)

# Save the network to an HTML file
net.show("outputs/entity_graph.html")
print("Entity relationship graph saved to outputs/entity_graph.html")
```

We add each entity as a node, and each pair from `edges` as a connection. The `net.show()` call will generate an HTML file with the interactive graph. You can open this file in a web browser – it will display a network where you can drag nodes, zoom, and inspect relationships. Each node is labeled with the entity name. If you hover, you can see connections.

**Step 7: Interpreting the Graph** – In the graph, clusters of interconnected nodes indicate entities that are mentioned together frequently (likely related topics or collaborations). For example, if the PDF is a scientific paper, you might see the authors connected to their institution or research terms, or a method connected to results or datasets. This gives a quick visual insight into the content structure of the document.

*   You can refine the graph by filtering out very common entities that might clutter the view (for instance, if the word “Fig. 1” was detected as an entity, you might remove it, or certain generic terms). You could do this by checking `ent.label_` from spaCy to only include specific types (e.g., `ORG`, `PERSON`, `GPE`).
*   If the graph is too dense, consider only adding edges that appear more than once (you could use a dictionary to count occurrences of each pair and filter by a threshold).

**Validation:** Open the `entity_graph.html` in a browser to ensure it works. You should see nodes and edges. Verify that important entities from the text are present. For example, if the paper is about “Climate Change”, expect nodes like “IPCC”, “Paris Agreement” or similar if they were mentioned. If nothing shows up, perhaps the text had no named entities (unlikely in a research paper) or something went wrong in extraction (like if text wasn’t in English for spaCy model).

**Search Query Validation:** To ensure the search is functioning, try a known query. For instance, take a sentence from the PDF and use it as the query – the top result should be that same sentence or very similar. This sanity-checks the embedding and retrieval process.

By completing the search and visualization modules, the user can both query the document semantically and get a visual map of key entities, greatly aiding in research and comprehension of the PDF content.

## 3. Step-by-Step Detailed Instructions

This section consolidates the above into a sequential guide from start to finish, including troubleshooting and validation at each step.

1.  **Install Homebrew (if not already installed)** – Skip if Homebrew is present. In Terminal, run the installation script. After it finishes, run `brew --version` to confirm it’s installed.

2.  **Install Python 3 and Git via Homebrew** – Use:

    ```bash
    brew install python git
    ```

    This installs the latest Python 3 (e.g., 3.11 or 3.12) and Git. Verify with `python3 --version` (expect Python 3.X) and `git --version`.
    *   **Troubleshooting:** If `brew install python` fails or hangs, ensure Command Line Tools are installed (run `xcode-select --install`). If you get a permission error, you might need to run the Homebrew command with `sudo` (not typical for brew). After Python installation, ensure that running `python3` invokes the Homebrew version (the Python guide noted brew puts it at `/usr/local/bin/python3` or `/opt/homebrew/bin/python3` for ARM Macs).

3.  **Set Up a Virtual Environment** – In your project directory:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    ```

    This creates and activates a clean environment. **Validation:** After activation, running `which python` (or `where python` on Windows) should show a path inside the `venv` directory.

4.  **Install Python Libraries** – Run the `pip install` command for all needed packages:

    ```bash
    pip install chromadb==0.4.5 PyMuPDF==1.25.3 sentence-transformers==3.4.0 spacy==3.8.4 langchain==0.3.19 pyvis==0.3.2 networkx==3.1
    ```

    This may take a few minutes (especially downloading PyTorch for `sentence-transformers`). You will see output for each package.
    *   **Troubleshooting:**
        *   If `chromadb` installation fails with an HNSWLIB wheel error (e.g., “Failed to build chroma-hnswlib”), install CMake and rerun: `brew install cmake` then `pip install chromadb` again. Also set `export HNSWLIB_NO_NATIVE=1` in your shell to avoid compiler flags.
        *   If `sentence-transformers` (PyTorch) fails, you might be on an unsupported Python version (e.g., Python 3.12 was only recently supported by PyTorch). In that case, consider installing Python 3.11 via Homebrew (`brew install [email protected]` and use that in your venv), or install PyTorch separately with a wheel that supports macOS/M3. Check the PyTorch site for Apple Silicon instructions.
        *   If any package has version conflicts (pip will usually warn), try adjusting the version. For instance, LangChain updates often; the version pin `0.3.19` is hypothetical – use `pip install langchain==0.x.y` matching a stable release around your install date (or omit version to get latest, understanding it may change behavior).

    **Validation:** After installation, run:

    ```bash
    python -c "import chromadb, fitz, spacy, sentence_transformers, langchain, pyvis; print('OK')"
    ```

    This should print “OK” with no errors. If an `ImportError` occurs, the module didn’t install correctly – check the pip output for issues.

5.  **Download spaCy Model** – Still in the venv, run:

    ```bash
    python -m spacy download en_core_web_sm
    ```

    This should output a success message indicating the model is installed. **Troubleshoot:** If you see “Unable to find model” or similar, ensure the spacy version and model version are compatible. Running `python -m spacy validate` can show if models are out-of-date for the installed spaCy. If needed, upgrade spaCy or download a different model version. You can also install models via pip if the download command fails (e.g., `pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.4/en_core_web_sm-3.8.4.tar.gz` for a specific version).

6.  **Place PDF Files** – Put your target PDF(s) into the `PDFs/` directory. Ensure the filenames have no spaces (or handle them accordingly in code). If your PDF is large, be patient during extraction.

7.  **Run PDF Extraction Script** – Use the script from Module 2.2. You can create a Python file `scripts/extract_text.py` with the code, and run it:

    ```bash
    python scripts/extract_text.py
    ```

    It should output either “Extracted text from X and saved to cache.” on first run, or “Loaded cached text for X” on subsequent runs. Check the `cache/` directory for a `.txt` file. Open it (in VSCode, a text editor, or `less` command) to verify it has content. This is your raw text. If it’s full of gibberish or empty, the PDF might be a scan (image-based) or encoded in a way PyMuPDF can’t parse. In such cases, you might need an OCR step or a different PDF parser, but assuming it’s a normal text PDF, you should see readable text.

8.  **Split Text (if needed)** – Decide on chunking strategy (you can skip this if one-vector-per-PDF is acceptable, but for best results, do some splitting). For now, proceed with the page split approach included in the embedding script.

9.  **Run Embedding & DB Script** – Now create a script `scripts/embed_store.py` that loads the cached text, splits it, generates embeddings, and stores them in Chroma. This script will use code from Module 2.3. For example:

    ```python
    # scripts/embed_store.py
    import os
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings

    # Load text from cache
    cache_path = "cache/sample.pdf.txt"
    with open(cache_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split text by page
    pages = text.split("\f")
    print(f"Loaded {len(pages)} pages of text from cache.")

    # Initialize model and compute embeddings
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode(pages, convert_to_numpy=True)
    print("Embeddings shape:", embeddings.shape)  # e.g., (N, 384)

    # Store embeddings in ChromaDB
    client = chromadb.Client(Settings(is_persistent=True, persist_directory="chromadb_data"))
    collection = client.get_or_create_collection("pdf_collection")
    # Use filename_page indexing for IDs
    ids = [f"sample_p{idx}" for idx in range(len(pages))]
    collection.add(documents=pages, embeddings=embeddings.tolist(), ids=ids)
    print("Vectors added to Chroma. Current collection count:", collection.count())

    # Quick test query
    query = "mitigation strategies"  # some phrase you expect in text
    q_embed = model.encode([query])
    res = collection.query(query_embeddings=q_embed, n_results=2, include=["documents"])
    print("Top match:", res["documents"][0][0][:100])
    ```

    Run this script:

    ```bash
    python scripts/embed_store.py
