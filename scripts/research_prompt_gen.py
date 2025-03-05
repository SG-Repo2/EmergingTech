# scripts/entity_extraction.py
import spacy
from collections import Counter
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import re

def extract_entities(text):
    """Extract and categorize named entities from text."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    # Entity extraction
    entities = {
        "ORG": [],      # Companies, organizations
        "PERSON": [],   # People
        "PRODUCT": [],  # Products, technologies
        "GPE": [],      # Countries, cities
        "DATE": [],     # Dates, time references
        "CARDINAL": [], # Numbers, quantities
        "MONEY": []     # Financial references
    }
    
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    
    # Count frequencies
    entity_counts = {
        category: Counter(items) 
        for category, items in entities.items()
    }
    
    return entity_counts

def extract_topics(text, n_topics=10):
    """Extract key topics using TF-IDF."""
    # Clean text - remove numbers and special characters
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Split into paragraphs
    paragraphs = [p for p in cleaned_text.split('\n\n') if len(p) > 100]
    
    # Apply TF-IDF
    vectorizer = TfidfVectorizer(
        max_df=0.7,            # Ignore terms that appear in >70% of paragraphs
        min_df=2,              # Ignore terms that appear in <2 paragraphs
        stop_words='english',  # Remove English stopwords
        ngram_range=(1, 2)     # Consider both unigrams and bigrams
    )
    
    tfidf_matrix = vectorizer.fit_transform(paragraphs)
    feature_names = vectorizer.get_feature_names_out()
    
    # Sum TF-IDF scores across all paragraphs
    tfidf_sums = tfidf_matrix.sum(axis=0).A1
    
    # Get top n_topics terms
    top_indices = tfidf_sums.argsort()[-n_topics:][::-1]
    top_terms = [(feature_names[i], tfidf_sums[i]) for i in top_indices]
    
    return top_terms

def extract_entity_relationships(text):
    """Extract relationships between entities that appear in the same context."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    relationships = []
    
    # Extract relationships from sentences containing multiple entities
    for sent in doc.sents:
        entities = [(ent.text, ent.label_) for ent in sent.ents]
        
        # Only consider sentences with multiple entities
        if len(entities) >= 2:
            # Create relationships between all pairs of entities
            for i, (entity1, label1) in enumerate(entities):
                for entity2, label2 in entities[i+1:]:
                    # Store the sentence as context
                    relationships.append({
                        "entity1": entity1,
                        "type1": label1,
                        "entity2": entity2,
                        "type2": label2,
                        "context": sent.text
                    })
    
    return relationships

def analyze_newsletter(pdf_path):
    """Analyze a newsletter and return structured data."""
    # Load cached text if available
    cache_dir = "cache/"
    pdf_name = os.path.basename(pdf_path)
    text_cache_path = os.path.join(cache_dir, pdf_name + ".txt")
    
    with open(text_cache_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Extract entities
    entities = extract_entities(text)
    
    # Get top entities by category
    top_entities = {
        category: counter.most_common(10)
        for category, counter in entities.items() 
    }
    
    return {
        "source": pdf_path,
        "entities": top_entities,
        "full_text": text
    }

# Example usage
if __name__ == "__main__":
    results = analyze_newsletter("PDFs/ALN_Elon_Musks_Monopoly.pdf")
    
    # Print top organizations mentioned
    print("Top Organizations Mentioned:")
    for org, count in results["entities"]["ORG"]:
        print(f"- {org}: {count} mentions")