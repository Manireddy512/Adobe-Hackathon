# Round 1A: PDF Structure Extractor

## Overview
This solution extracts hierarchical structure (title and headings H1, H2, H3) from PDF documents and outputs them in JSON format.

## Approach
My approach combines font analysis with heuristic validation to identify document structure:

1. **Font Analysis**: Extract text with formatting information using PyMuPDF
2. **Hierarchy Detection**: Analyze font sizes to determine heading levels
3. **Heuristic Validation**: Apply rules to confirm text elements are actual headings
4. **Structure Extraction**: Build document outline with page numbers

## Key Features
- Handles various PDF layouts and fonts
- Uses multiple validation techniques beyond just font size
- Processes documents up to 50 pages efficiently
- Works offline without internet connectivity
- Optimized for performance (≤10 seconds per 50-page PDF)

## Technology Stack
- **PyMuPDF (fitz)**: Fast PDF text extraction with formatting preservation
- **Python 3.9**: Core processing language
- **JSON**: Structured output format

## Algorithm Details

### Heading Detection Strategy
1. **Font Size Analysis**: Collect all font sizes and create hierarchy
2. **Bold Text Recognition**: Use formatting flags to identify emphasis
3. **Pattern Matching**: Detect numbered sections and common heading words
4. **Length Validation**: Filter out text that's too long for headings
5. **Context Checking**: Look for chapter/section keywords

### Validation Heuristics
- Text length limits (max 150 characters for headings)
- Punctuation analysis (exclude text with excessive periods)
- Formatting checks (bold text preference)
- Keyword recognition (chapter, section, introduction, etc.)
- Pattern matching for numbered sections

## Docker Usage

### Build the image:
```bash
docker build --platform linux/amd64 -t pdf-extractor:v1 .
