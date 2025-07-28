# Round 1B: Persona-Driven Document Intelligence

## Overview
This solution acts as an intelligent document analyst that extracts and prioritizes the most relevant sections from a collection of documents based on a specific persona and their job-to-be-done.

## Approach
My system combines semantic understanding with persona-specific analysis to deliver contextually relevant document insights:

1. **Document Parsing**: Extract structured sections from multiple PDFs
2. **Persona Profiling**: Build comprehensive user profiles from role and task descriptions
3. **Semantic Analysis**: Use transformer models for deep content understanding
4. **Relevance Scoring**: Combine multiple signals to rank content importance
5. **Subsection Extraction**: Identify key passages within relevant sections

## Key Features
- Generic solution works across diverse domains and document types
- Semantic similarity matching using state-of-the-art embeddings
- Multi-signal relevance scoring (semantic + keyword + structural)
- Intelligent subsection analysis for granular insights
- Persona-aware content prioritization
- Efficient processing within 60-second constraint

## Technology Stack
- **Sentence-Transformers**: Semantic embeddings (all-MiniLM-L6-v2, ~90MB)
- **PyMuPDF**: Fast PDF text extraction and parsing
- **Scikit-learn**: Cosine similarity calculations
- **NumPy**: Numerical computations
- **Python 3.9**: Core processing environment

## Algorithm Details

### Document Section Extraction
1. **Layout Analysis**: Parse PDF structure using PyMuPDF
2. **Section Detection**: Identify headings based on formatting and content patterns
3. **Content Aggregation**: Group related paragraphs under section headers
4. **Quality Filtering**: Remove sections that are too short or irrelevant

### Persona Profile Creation
1. **Role Analysis**: Extract domain-specific interests based on persona description
2. **Task Decomposition**: Identify key requirements from job-to-be-done
3. **Semantic Encoding**: Create vector representations of user needs
4. **Focus Area Mapping**: Build keyword sets for different professional domains

### Relevance Scoring Algorithm
- **Semantic Similarity** (65% weight): Cosine similarity between content and persona embeddings
- **Keyword Matching** (35% weight): Explicit term overlap with focus areas
- **Combined Scoring**: Weighted average for final relevance ranking

### Subsection Analysis
1. **Content Chunking**: Intelligent paragraph and sentence-level splitting
2. **Relevance Filtering**: Score individual chunks against persona profile
3. **Text Refinement**: Clean and summarize content for output
4. **Quality Assurance**: Ensure subsections meet minimum length and relevance thresholds

## Docker Usage

### Build the image:
```bash
