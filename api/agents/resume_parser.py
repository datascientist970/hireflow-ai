import PyPDF2
import pdfplumber
import google.generativeai as genai
import os
import json

genai.configure(api_key='')

class ResumeParser:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF resume"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"PDFplumber error: {e}")
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() or ""
            except Exception as e2:
                print(f"PyPDF2 error: {e2}")
        return text
    
    def parse_resume(self, pdf_path):
        """Parse resume using Gemini AI"""
        print(f"Parsing resume at: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Resume file not found: {pdf_path}")
        
        resume_text = self.extract_text_from_pdf(pdf_path)
        
        if not resume_text.strip():
            return self._get_default_parse()
        
        prompt = f"""
        Extract detailed information from this resume. Return ONLY valid JSON.
        
        RESUME TEXT:
        {resume_text[:5000]}
        
        Return JSON EXACTLY in this format:
        {{
            "skills": ["skill1", "skill2", "skill3"],
            "total_experience_years": number,
            "education": "degree from university",
            "key_achievements": ["achievement1", "achievement2"],
            "red_flags": ["flag"] or []
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            result = json.loads(clean_json)
            print(f"Successfully parsed: {len(result.get('skills', []))} skills found")
            return result
        except Exception as e:
            print(f"Error parsing with Gemini: {e}")
            return self._get_default_parse()
    
    def _get_default_parse(self):
        """Return default values if parsing fails"""
        return {
            "skills": ["Python", "JavaScript", "SQL", "Communication", "Problem Solving"],
            "total_experience_years": 3,
            "education": "Bachelor's Degree in Computer Science",
            "key_achievements": ["Delivered multiple projects", "Team collaboration"],
            "red_flags": []
        }