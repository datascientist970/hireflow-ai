import google.generativeai as genai
import os
import json

genai.configure(api_key='')

class JobMatcher:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
    
    def calculate_fit_score(self, resume_data, job_description, job_requirements):
        """Calculate fit score with detailed analysis"""
        
        prompt = f"""
        You are an expert recruitment AI. Analyze this candidate and job match.
        
        CANDIDATE PROFILE:
        Skills: {resume_data.get('skills', [])}
        Experience: {resume_data.get('total_experience_years', 0)} years
        Education: {resume_data.get('education', 'N/A')}
        Achievements: {resume_data.get('key_achievements', [])}
        Red Flags: {resume_data.get('red_flags', [])}
        
        JOB DESCRIPTION:
        {job_description[:1500]}
        
        JOB REQUIREMENTS:
        {job_requirements[:1000]}
        
        Analyze deeply and return ONLY valid JSON (no explanations, no markdown):
        
        {{
            "fit_score": <number 0-100>,
            "skills_match": [<list of specific skills that match>],
            "missing_skills": [<list of critical missing skills>],
            "strengths": [<list of specific strengths>],
            "weaknesses": [<list of areas to improve>],
            "recommendation": "<detailed recommendation>"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            result = json.loads(clean_json)
            
            return {
                "fit_score": result.get('fit_score', 70),
                "skills_match": result.get('skills_match', ['Communication', 'Problem solving']),
                "missing_skills": result.get('missing_skills', ['Role-specific skills']),
                "strengths": result.get('strengths', ['Relevant experience']),
                "weaknesses": result.get('weaknesses', ['May need training']),
                "recommendation": result.get('recommendation', 'Consider for interview')
            }
            
        except Exception as e:
            print(f"Error in job matcher: {e}")
            return self._get_default_analysis(resume_data, job_description)
    
    def _get_default_analysis(self, resume_data, job_description):
        """Fallback analysis"""
        skills = resume_data.get('skills', [])
        experience = resume_data.get('total_experience_years', 0)
        
        fit_score = min(85, 50 + (experience * 5) + (len(skills) * 2))
        
        return {
            "fit_score": fit_score,
            "skills_match": skills[:5] if skills else ["Technical skills"],
            "missing_skills": ["Additional experience may be needed"],
            "strengths": [f"{experience}+ years experience"],
            "weaknesses": ["Would benefit from role-specific training"],
            "recommendation": "Candidate shows potential. Recommend interview."
        }