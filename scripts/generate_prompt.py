#!/usr/bin/env python3
# scripts/generate_prompt.py

import os
import argparse
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Define the prompt template
PROMPT_TEMPLATE = """
I'm researching a topic based on a PDF document. Below are relevant excerpts from the document that provide context for my question:

{context}

Based on these excerpts and any other relevant knowledge, please answer the following question:
{question}

Please structure your response as follows:
1. Direct answer to the question (2-3 sentences)
2. Analysis of the key points from the provided context
3. Any additional insights or considerations
"""

def retrieve_context(question, collection, embedder, n_results=3, min_score_threshold=0.6):
    """
    Retrieve relevant context from ChromaDB based on a research question.
    
    Args:
        question (str): The research question
        collection: ChromaDB collection containing document embeddings
        embedder: SentenceTransformer model to embed the question
        n_results (int): Number of passages to retrieve
        min_score_threshold (float): Minimum similarity score (0-1) for inclusion
        
    Returns:
        str: Formatted context from relevant passages
    """
    # Embed the question
    question_embedding = embedder.encode([question], convert_to_numpy=True)
    
    # Query the collection
    results = collection.query(
        query_embeddings=question_embedding.tolist(),
        n_results=n_results,
        include=["documents", "distances"]
    )
    
    # Check if we got any results
    if not results["documents"] or len(results["documents"][0]) == 0:
        return "No relevant context found in the document. The query may be outside the scope of this document."
    
    passages = results["documents"][0]
    distances = results["distances"][0]
    
    # Convert distances to similarity scores (1 - distance for cosine distance)
    similarity_scores = [1 - dist for dist in distances]
    
    # Filter by threshold and format the context
    context_parts = []
    for i, (passage, score) in enumerate(zip(passages, similarity_scores)):
        if score >= min_score_threshold:
            # Truncate very long passages to a reasonable length
            if len(passage) > 1000:
                passage = passage[:997] + "..."
            
            context_parts.append(f"Excerpt {i+1} (Relevance: {score:.2f}):\n{passage}\n")
    
    # Join all relevant passages
    if context_parts:
        return "\n".join(context_parts)
    else:
        return "No highly relevant context found in the document. The available excerpts did not meet the minimum relevance threshold."

def filter_proper_nouns(text):
    """
    Placeholder for future implementation of proper noun filtering.
    This function would identify and potentially filter out irrelevant named entities.
    
    Args:
        text (str): The text to filter
        
    Returns:
        str: The filtered text
    """
    # TODO: Implement proper noun validation using spaCy
    # This could identify company names, product names, or other entities
    # and filter them based on relevance to the query
    return text

def generate_research_prompt(question, collection, embedder, n_results=3, 
                           min_score_threshold=0.6, template=PROMPT_TEMPLATE):
    """
    Generate a research prompt combining the question with relevant context.
    
    Args:
        question (str): User's research question
        collection: ChromaDB collection
        embedder: SentenceTransformer model
        n_results (int): Number of results to retrieve
        min_score_threshold (float): Relevance threshold
        template (str): Prompt template string
        
    Returns:
        str: Complete research prompt for ChatGPT
    """
    try:
        # Get relevant context
        context = retrieve_context(question, collection, embedder, 
                                  n_results=n_results, 
                                  min_score_threshold=min_score_threshold)
        
        # Generate the prompt using the template
        prompt = template.format(
            context=context,
            question=question
        )
        
        return prompt
    except Exception as e:
        return f"Error generating research prompt: {str(e)}\n\nPlease check your configuration and try again."

def validate_prompt(prompt, max_tokens=4000):
    """
    Validate the generated prompt.
    
    Args:
        prompt (str): The generated prompt
        max_tokens (int): Maximum tokens allowed (approximate)
        
    Returns:
        dict: Validation results with status, message, and token estimate
    """
    # Rough token estimation (English average is ~1.3 tokens per word)
    word_count = len(prompt.split())
    token_estimate = int(word_count * 1.3)
    
    # Check if prompt contains error message
    if prompt.startswith("Error generating research prompt"):
        return {
            "valid": False,
            "message": "Prompt generation failed",
            "token_estimate": token_estimate
        }
    
    # Check if context indicates no results found
    if "No relevant context found" in prompt or "No highly relevant context found" in prompt:
        return {
            "valid": True,  # Still valid, but with a warning
            "message": "Warning: Limited or no relevant context found in the document",
            "token_estimate": token_estimate,
            "warning": True
        }
    
    # Check if prompt is too long
    if token_estimate > max_tokens:
        return {
            "valid": False,
            "message": f"Prompt may be too long ({token_estimate} tokens, max {max_tokens})",
            "token_estimate": token_estimate
        }
    
    # Check if context is substantive (at least 100 words)
    if len(prompt.split()) < 100:
        return {
            "valid": False,
            "message": "Prompt context is too short, may not provide enough information",
            "token_estimate": token_estimate
        }
    
    return {
        "valid": True,
        "message": f"Prompt is valid ({token_estimate} tokens)",
        "token_estimate": token_estimate
    }

def main():
    """
    Main function to run the research prompt generator.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate research prompts from PDF content')
    parser.add_argument('--question', type=str, required=True, help='Research question')
    parser.add_argument('--output', type=str, default=None, help='Output file for the prompt (optional)')
    parser.add_argument('--collection', type=str, default="pdf_collection", help='ChromaDB collection name')
    parser.add_argument('--results', type=int, default=3, help='Number of relevant passages to include')
    parser.add_argument('--threshold', type=float, default=0.6, help='Minimum relevance threshold (0-1)')
    parser.add_argument('--config', type=str, default=None, help='Path to configuration file (not implemented yet)')
    args = parser.parse_args()
    
    # Initialize sentence transformer
    print("Loading embedding model...")
    try:
        # Explicitly set device to CPU to avoid MPS issues on Apple Silicon
        embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device='cpu')
    except Exception as e:
        print(f"Error loading embedding model: {str(e)}")
        print("Make sure the sentence-transformers library is installed correctly.")
        return
    
    # Connect to ChromaDB
    print("Connecting to ChromaDB...")
    try:
        client = chromadb.Client(Settings(is_persistent=True, persist_directory="chromadb_data"))
    except Exception as e:
        print(f"Error connecting to ChromaDB: {str(e)}")
        print("Make sure chromadb is installed and the data directory exists.")
        return
    
    # Get collection
    try:
        collection = client.get_collection(name=args.collection)
        doc_count = collection.count()
        print(f"Found collection '{args.collection}' with {doc_count} documents")
        
        if doc_count == 0:
            print("Warning: The collection is empty. Please run the embedding script first.")
            return
    except ValueError:
        print(f"Error: Collection '{args.collection}' not found. Please run the embedding script first.")
        return
    except Exception as e:
        print(f"Error accessing collection: {str(e)}")
        return
    
    # Generate prompt
    print(f"Generating research prompt for question: {args.question}")
    prompt = generate_research_prompt(
        args.question, 
        collection, 
        embedder,
        n_results=args.results,
        min_score_threshold=args.threshold
    )
    
    # Validate prompt
    validation = validate_prompt(prompt)
    if not validation["valid"]:
        print(f"Warning: {validation['message']}")
    elif validation.get("warning", False):
        print(f"Note: {validation['message']}")
    
    print(f"Prompt generated ({validation['token_estimate']} estimated tokens)")
    
    # Save or display prompt
    if args.output:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or '.', exist_ok=True)
        # Write prompt to file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"Prompt saved to {args.output}")
    else:
        print("\n" + "="*50 + " GENERATED PROMPT " + "="*50)
        print(prompt)
        print("="*120)
        print("\nCopy the above prompt to use with ChatGPT.")

if __name__ == "__main__":
    main()