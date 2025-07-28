import fitz
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
import os
from datetime import datetime

class MyDocumentReader:
    def __init__(self):
        print("Loading semantic understanding model...")
        self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
      
    #Split documents into meaningful sections for analysis
    def break_document_into_sections(self, pdf_file):
        document = fitz.open(pdf_file)
        document_sections = []
        
        for page_number in range(len(document)):
            page = document[page_number]
            
            text_blocks = page.get_text("dict")
            current_section = None
            
            for block in text_blocks["blocks"]:
                if "lines" not in block:
                    continue
                
                block_text = ""
                looks_like_heading = False
                
                for line in block["lines"]:
                    line_content = ""
                    for span in line["spans"]:
                        line_content += span["text"]
                        if span["size"] > 11 and (span["flags"] & 16):  
                            looks_like_heading = True
                    block_text += line_content + "\n"
                
                block_text = block_text.strip()
                if not block_text:
                    continue
                
                if looks_like_heading or self.seems_like_section_start(block_text):
                    if current_section and len(current_section['content']) > 50:
                        document_sections.append(current_section)
                    
                    current_section = {
                        'title': block_text,
                        'content': block_text,
                        'page': page_number + 1,
                        'source_file': os.path.basename(pdf_file)
                    }
                else:
                    if current_section:
                        current_section['content'] += "\n\n" + block_text
                    else:
                        current_section = {
                            'title': self.make_title_from_text(block_text),
                            'content': block_text,
                            'page': page_number + 1,
                            'source_file': os.path.basename(pdf_file)
                        }
            
            if current_section and len(current_section['content']) > 50:
                document_sections.append(current_section)
                current_section = None
        
        document.close()
        return document_sections
      
    #Logic to detect section headers
    def seems_like_section_start(self, text):
        
        if len(text) > 80:  
            return False
        
        if text.count('\n') > 1:  
            return False
        
        section_indicators = [
            'introduction', 'background', 'methodology', 'results', 
            'discussion', 'conclusion', 'abstract', 'summary',
            'chapter', 'section', 'overview', 'analysis',
            'literature review', 'related work', 'evaluation',
            'implementation', 'experiments', 'findings'
        ]
        
        return any(indicator in text.lower() for indicator in section_indicators)
    #Create a reasonable title from a text block
    def make_title_from_text(self, text):
        first_sentence = text.split('.')[0]
        if len(first_sentence) < 60:
            return first_sentence
        else:
            return first_sentence[:50] + "..."

class MyPersonaAnalyzer:
    def __init__(self, semantic_model):
        self.model = semantic_model

  #Understanding what the user needs based on their role and task
    def build_persona_profile(self, persona_description, job_task):
        full_context = f"Role: {persona_description}\nTask: {job_task}"
        
        focus_areas = self.identify_focus_areas(persona_description, job_task)
        
        context_embedding = self.model.encode([full_context])[0]
        
        return {
            'full_context': full_context,
            'focus_areas': focus_areas,
            'semantic_profile': context_embedding,
            'persona': persona_description,
            'task': job_task
        }

  #Figure out what someone in this role would care about
    def identify_focus_areas(self, persona, task):
        combined_text = (persona + " " + task).lower()
        
        role_interests = {
            'researcher': ['methodology', 'results', 'data', 'analysis', 'findings', 'study', 'experiment'],
            'student': ['concepts', 'examples', 'definitions', 'principles', 'theory', 'learning'],
            'analyst': ['trends', 'performance', 'metrics', 'comparison', 'insights', 'statistics'],
            'manager': ['strategy', 'planning', 'objectives', 'outcomes', 'decisions', 'leadership'],
            'developer': ['implementation', 'architecture', 'design', 'technical', 'code', 'system'],
            'doctor': ['symptoms', 'treatment', 'diagnosis', 'clinical', 'patient', 'medical'],
            'engineer': ['design', 'specification', 'requirements', 'testing', 'performance'],
            'scientist': ['hypothesis', 'experiment', 'observation', 'theory', 'validation'],
            'teacher': ['curriculum', 'pedagogy', 'assessment', 'learning', 'education'],
            'lawyer': ['legal', 'regulation', 'compliance', 'case', 'precedent', 'law']
        }
        
        relevant_interests = []
        for role, interests in role_interests.items():
            if role in combined_text:
                relevant_interests.extend(interests)
        
        task_words = re.findall(r'\b\w{4,}\b', task.lower())
        relevant_interests.extend(task_words)
        
        return list(set(relevant_interests))  # Remove duplicates

  #Scoring system to rank how relevant each section is
    def score_section_relevance(self, sections, persona_profile):
        scored_sections = []
        
        for section in sections:
            section_embedding = self.model.encode([section['content']])
            semantic_score = cosine_similarity(
                [persona_profile['semantic_profile']], 
                section_embedding
            )[0][0]
            
            keyword_score = self.calculate_keyword_match(
                section['content'], 
                persona_profile['focus_areas']
            )
            
            final_relevance = (0.65 * semantic_score) + (0.35 * keyword_score)
            
            scored_sections.append({
                'section_data': section,
                'semantic_similarity': semantic_score,
                'keyword_relevance': keyword_score,
                'overall_score': final_relevance
            })
        
        scored_sections.sort(key=lambda x: x['overall_score'], reverse=True)
        return scored_sections
  #Check how well content matches what the persona cares about
    def calculate_keyword_match(self, text, focus_areas):

        if not focus_areas:
            return 0.0
        
        text_lower = text.lower()
        matches = 0
        
        for focus_area in focus_areas:
            if focus_area.lower() in text_lower:
                matches += 1
        
        return matches / len(focus_areas)

class MySubsectionExtractor:
    def __init__(self, semantic_model):
        self.model = semantic_model
    # Find the most relevant parts within a section
    def find_best_subsections(self, section_content, persona_profile, max_count=3):
      
        content_chunks = self.smart_content_splitting(section_content)
        
        chunk_scores = []
        
        for i, chunk in enumerate(content_chunks):
            if len(chunk.strip()) < 30:  
                continue

            chunk_embedding = self.model.encode([chunk])
            relevance = cosine_similarity(
                [persona_profile['semantic_profile']], 
                chunk_embedding
            )[0][0]

            cleaned_chunk = self.improve_text_quality(chunk)
            
            chunk_scores.append({
                'original': chunk,
                'cleaned': cleaned_chunk,
                'relevance': relevance,
                'position': i
            })

        chunk_scores.sort(key=lambda x: x['relevance'], reverse=True)
        return chunk_scores[:max_count]
    #Split content into meaningful pieces
    def smart_content_splitting(self, content):
        
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if len(paragraphs) < 2:
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            chunks = []
            for i in range(0, len(sentences), 2):
                chunk = '. '.join(sentences[i:i+2])
                if chunk:
                    chunks.append(chunk)
            return chunks
        
        return paragraphs
    #Text cleaning and improvement function
    def improve_text_quality(self, text):
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        if len(cleaned) > 400:
            sentences = cleaned.split('.')
            if len(sentences) > 3:
                summary = sentences[0] + '. [...continues...] ' + sentences[-1]
                return summary
        
        return cleaned
#Complete document intelligence system
def my_main_processing_function(input_directory, persona_desc, job_desc, output_file):
    
    print("Starting document analysis system...")
    
    # Initialize components
    doc_reader = MyDocumentReader()
    persona_analyzer = MyPersonaAnalyzer(doc_reader.semantic_model)
    subsection_extractor = MySubsectionExtractor(doc_reader.semantic_model)
    
    # Build understanding of what the user needs
    user_profile = persona_analyzer.build_persona_profile(persona_desc, job_desc)
    print(f"Built profile for: {persona_desc}")
    
    # Process all documents
    all_sections = []
    processed_files = []
    
    for filename in os.listdir(input_directory):
        if filename.lower().endswith('.pdf'):
            print(f"Processing: {filename}")
            file_path = os.path.join(input_directory, filename)
            processed_files.append(filename)
            
            sections = doc_reader.break_document_into_sections(file_path)
            all_sections.extend(sections)
    
    print(f"Found {len(all_sections)} sections across {len(processed_files)} documents")
    
    # Rank all sections by relevance
    ranked_sections = persona_analyzer.score_section_relevance(all_sections, user_profile)
    
    # Build output structure
    analysis_results = {
        'metadata': {
            'input_documents': processed_files,
            'persona': persona_desc,
            'job_to_be_done': job_desc,
            'processing_timestamp': datetime.now().isoformat(),
            'total_sections_found': len(all_sections)
        },
        'extracted_sections': [],
        'subsection_analysis': []
    }
    
    # Extract top relevant sections
    top_sections_count = min(15, len(ranked_sections))
    print(f"Analyzing top {top_sections_count} most relevant sections...")
    
    for rank, section_info in enumerate(ranked_sections[:top_sections_count]):
        section = section_info['section_data']
        
        analysis_results['extracted_sections'].append({
            'document': section['source_file'],
            'page_number': section['page'],
            'section_title': section['title'],
            'importance_rank': rank + 1
        })
        
        # Detailed subsection analysis for top 8 sections
        if rank < 8:
            subsections = subsection_extractor.find_best_subsections(
                section['content'], user_profile
            )
            
            for sub_rank, subsection in enumerate(subsections):
                analysis_results['subsection_analysis'].append({
                    'document': section['source_file'],
                    'page_number': section['page'],
                    'refined_text': subsection['cleaned']
                })
    
    # Save analysis
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis complete! Results saved to: {output_file}")

def main():
    # Get user requirements from environment variables
    persona = os.getenv('PERSONA', 'General Researcher')
    job_task = os.getenv('JOB', 'Extract relevant information from documents')
    
    input_dir = "/app/input"
    output_file = "/app/output/challenge1b_output.json"
    
    # Ensure output directory exists
    os.makedirs("/app/output", exist_ok=True)
    
    print(f"Persona: {persona}")
    print(f"Job: {job_task}")
    
    my_main_processing_function(input_dir, persona, job_task, output_file)

if __name__ == "__main__":
    main()
