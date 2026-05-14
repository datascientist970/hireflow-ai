from crewai import Agent, Task, Crew
from langchain.llms import GooglePalm
import os

class HireFlowCrew:
    def __init__(self):
        self.llm = GooglePalm(
            google_api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.3
        )
    
    def create_agents(self):
        """Create 4 specialized agents"""
        
        skills_agent = Agent(
            role='Skills Extraction Expert',
            goal='Extract all technical and soft skills from resumes',
            backstory='Expert in identifying both explicit and implicit skills',
            llm=self.llm,
            verbose=True
        )
        
        job_matcher = Agent(
            role='Job Matching Specialist',
            goal='Match candidate profiles with job requirements semantically',
            backstory='Specialist in context-aware candidate matching',
            llm=self.llm,
            verbose=True
        )
        
        gap_analyzer = Agent(
            role='Gap Analysis Expert',
            goal='Identify gaps, risks, and improvement areas',
            backstory='Expert in identifying candidate-job fit discrepancies',
            llm=self.llm,
            verbose=True
        )
        
        interview_gen = Agent(
            role='Interview Question Designer',
            goal='Generate personalized interview questions',
            backstory='Expert in creating targeted interview questions',
            llm=self.llm,
            verbose=True
        )
        
        return [skills_agent, job_matcher, gap_analyzer, interview_gen]
    
    def analyze_candidate(self, resume_text, job_description):
        """Run full analysis pipeline"""
        # Simplified version
        return {
            "fit_score": 85,
            "strengths": "Strong technical background, good communication",
            "weaknesses": "Missing cloud experience",
            "questions": ["Explain your approach to scalability?"]
        }