#PDF Text Extraction with Formatting
import fitz
import json
import os
from collections import Counter
import re

def read_pdf_with_styles(file_path):
    """
    Extract text from PDF while preserving formatting information
    """
    pdf_document = fitz.open(file_path)
    all_page_data = []
    
    for page_index in range(len(pdf_document)):
        current_page = pdf_document[page_index]
        page_content = current_page.get_text("dict")
        
        page_details = {
            'page_num': page_index + 1,
            'text_elements': []
        }
        
        # Go through each text block on the page
        for text_block in page_content["blocks"]:
            if "lines" in text_block:
                for text_line in text_block["lines"]:
                    for text_piece in text_line["spans"]:
                        if text_piece['text'].strip():  # Only keep non-empty text
                            page_details['text_elements'].append({
                                'content': text_piece['text'].strip(),
                                'font_name': text_piece['font'],
                                'font_size': text_piece['size'],
                                'is_bold': bool(text_piece['flags'] & 2**4),
                                'location': text_piece['bbox']
                            })
        
        all_page_data.append(page_details)
    
    pdf_document.close()
    return all_page_data

#Heading Detection Algorithm
def figure_out_headings(page_data):
    all_sizes = []
    text_by_size = {}
    
    for page in page_data:
        for element in page['text_elements']:
            size = element['font_size']
            all_sizes.append(size)
            
            if size not in text_by_size:
                text_by_size[size] = []
            text_by_size[size].append(element)
    
    size_frequency = Counter(all_sizes)
    unique_sizes = sorted(set(all_sizes), reverse=True)
    
    heading_map = {}
    level_names = ['TITLE', 'H1', 'H2', 'H3']
    
    for i, size in enumerate(unique_sizes[:4]):  
        if i < len(level_names):
            heading_map[size] = level_names[i]
    
    return heading_map, text_by_size

#Validate if a text element is actually a heading using heuristics
def check_if_really_heading(text_content, element_info):
    
    if len(text_content) > 150:  
        return False
    
    if text_content.count('.') > 2:  
        return False
    
    if element_info['is_bold']: 
        return True
    
    if text_content.isupper() and len(text_content) < 80: 
        return True
      
    heading_patterns = [
        r'^\d+\.?\s+', 
        r'^chapter\s+\d+',  
        r'^section\s+\d+',  
    ]
    
    for pattern in heading_patterns:
        if re.search(pattern, text_content.lower()):
            return True

    heading_words = ['chapter', 'section', 'introduction', 'conclusion', 'abstract', 'summary']
    if any(word in text_content.lower() for word in heading_words):
        return True
    
    return True  

#Main function to extract title and outline from PDF data
def extract_document_structure(page_data):
    
    heading_sizes, size_groups = figure_out_headings(page_data)
    
    document_title = ""
    document_outline = []
    
    for page in page_data:
        for element in page['text_elements']:
            text = element['content']
            size = element['font_size']
            
            if size in heading_sizes:
                heading_level = heading_sizes[size]
                
                if check_if_really_heading(text, element):
                    if heading_level == 'TITLE' and not document_title:
                        document_title = text
                    elif heading_level in ['H1', 'H2', 'H3']:
                        document_outline.append({
                            'level': heading_level,
                            'text': text,
                            'page': page['page_num']
                        })
    
    return document_title, document_outline
  
#Complete Processing Pipeline
def process_single_pdf(input_file, output_file):
    try:
        print(f"Processing: {input_file}")
        
        # Step 1: Read the PDF with formatting
        page_data = read_pdf_with_styles(input_file)
        
        # Step 2: Extract document structure
        title, outline = extract_document_structure(page_data)
        
        # Step 3: Format the output according to requirements
        final_result = {
            "title": title if title else "Document",
            "outline": outline
        }
        
        # Step 4: Save the result as JSON
        with open(output_file, 'w', encoding='utf-8') as output:
            json.dump(final_result, output, indent=2, ensure_ascii=False)
        
        print(f"✓ Successfully processed: {os.path.basename(input_file)}")
        
    except Exception as error:
        print(f"✗ Error processing {input_file}: {error}")

def main():
    """
    Main execution function - processes all PDFs in input directory
    """
    input_folder = "/app/input"
    output_folder = "/app/output"
    
    print("Starting PDF structure extraction...")
    
    os.makedirs(output_folder, exist_ok=True)

    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    for filename in pdf_files:
        input_path = os.path.join(input_folder, filename)
        output_name = filename.replace('.pdf', '.json')
        output_path = os.path.join(output_folder, output_name)
        
        process_single_pdf(input_path, output_path)
    
    print("PDF processing complete!")

if __name__ == "__main__":
    main()
