# scripts/analyze_newsletter.py
import os
import argparse
from entity_extraction import analyze_newsletter, extract_topics, extract_entity_relationships
from research_prompt_gen import generate_research_prompt, enhance_prompt_with_vector_search
from entity_visualization import create_entity_graph

def main():
    parser = argparse.ArgumentParser(description="Analyze a newsletter and generate research materials")
    parser.add_argument("pdf_path", help="Path to the PDF newsletter")
    parser.add_argument("--search", help="Optional search query to enhance the prompt")
    args = parser.parse_args()
    
    # Check if the PDF exists
    if not os.path.exists(args.pdf_path):
        print(f"Error: File not found - {args.pdf_path}")
        return
    
    # Create output directory
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract PDF text if not already cached
    print("Checking for cached text...")
    cache_dir = "cache/"
    os.makedirs(cache_dir, exist_ok=True)
    
    pdf_name = os.path.basename(args.pdf_path)
    text_cache_path = os.path.join(cache_dir, pdf_name + ".txt")
    
    if not os.path.exists(text_cache_path):
        print("Text not cached. Extracting from PDF...")
        import fitz  # PyMuPDF
        doc = fitz.open(args.pdf_path)
        all_text = []
        for page in doc:
            page_text = page.get_text()
            all_text.append(page_text)
        text = "\f".join(all_text)
        
        with open(text_cache_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Text extracted and cached to {text_cache_path}")
    else:
        print(f"Using cached text from {text_cache_path}")
        with open(text_cache_path, 'r', encoding='utf-8') as f:
            text = f.read()
    
    # Generate the research prompt
    print("Generating research prompt...")
    prompt = generate_research_prompt(args.pdf_path)
    
    # Enhance with vector search if query provided
    if args.search:
        print(f"Enhancing prompt with search for: {args.search}")
        prompt = enhance_prompt_with_vector_search(prompt, args.search, args.pdf_path)
    
    # Save the prompt
    prompt_path = os.path.join(output_dir, f"{os.path.splitext(pdf_name)[0]}_research_prompt.md")
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    print(f"Research prompt saved to {prompt_path}")
    
    # Create entity visualization
    print("Creating entity relationship visualization...")
    graph_path = create_entity_graph(text, min_occurrences=2)
    print(f"Entity graph saved to {graph_path}")
    
    print("\nAnalysis complete! You can now use the research prompt for further investigation.")

if __name__ == "__main__":
    main()