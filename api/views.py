from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Job, Candidate
from .agents.resume_parser import ResumeParser
from .agents.job_matcher import JobMatcher
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
from django.conf import settings

# Home Page
def home(request):
    jobs = Job.objects.all()
    return render(request, 'home.html', {'jobs': jobs})

# Upload Resume
def upload_resume(request):
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        resume_file = request.FILES.get('resume')
        
        if not all([job_id, name, email, resume_file]):
            messages.error(request, 'Please fill all required fields')
            return redirect('upload_resume')
        
        try:
            job = Job.objects.get(id=job_id)
            
            # ✅ FIXED: Ensure media directory exists
            media_root = settings.MEDIA_ROOT
            resumes_dir = os.path.join(media_root, 'resumes')
            
            if not os.path.exists(resumes_dir):
                os.makedirs(resumes_dir)
                print(f"Created directory: {resumes_dir}")
            
            # ✅ FIXED: Save file with proper path
            file_name = f'resumes/{resume_file.name}'
            file_path = default_storage.save(file_name, ContentFile(resume_file.read()))
            
            # ✅ Debug: Print actual file path
            full_path = os.path.join(media_root, file_path)
            print(f"File saved at: {full_path}")
            print(f"File exists: {os.path.exists(full_path)}")
            
            # Parse resume with AI
            parser = ResumeParser()
            # ✅ FIXED: Pass full path for parsing
            resume_data = parser.parse_resume(full_path)
            
            # Match with job
            matcher = JobMatcher()
            match_result = matcher.calculate_fit_score(
                resume_data, 
                job.description, 
                job.requirements
            )
            
            # Save candidate
            candidate = Candidate.objects.create(
                name=name,
                email=email,
                phone=phone,
                resume_file=file_path,  # Relative path store karo
                job=job,
                fit_score=match_result.get('fit_score', 75),
                skills_match=', '.join(match_result.get('skills_match', ['Communication', 'Team Work'])),
                missing_skills=', '.join(match_result.get('missing_skills', ['None identified'])),
                strengths=', '.join(match_result.get('strengths', ['Good candidate'])),
                weaknesses=', '.join(match_result.get('weaknesses', ['Minor improvements needed'])),
                recommendation=match_result.get('recommendation', 'Consider for interview')
            )
            
            messages.success(request, f'Resume analyzed! Fit score: {candidate.fit_score}%')
            return redirect('candidate_detail', candidate_id=candidate.id)
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            print(f"Upload error: {str(e)}")  # Debug print
            return redirect('upload_resume')
    
    jobs = Job.objects.all()
    return render(request, 'upload_resume.html', {'jobs': jobs})

# Dashboard
def dashboard(request):
    jobs = Job.objects.all()
    selected_job_id = request.GET.get('job_id')
    
    if selected_job_id:
        candidates = Candidate.objects.filter(job_id=selected_job_id).order_by('-fit_score')
        selected_job = get_object_or_404(Job, id=selected_job_id)
    else:
        candidates = Candidate.objects.all().order_by('-fit_score')[:20]
        selected_job = None
    
    return render(request, 'dashboard.html', {
        'jobs': jobs,
        'candidates': candidates,
        'selected_job': selected_job,
        'selected_job_id': selected_job_id
    })

# Candidate Detail
def candidate_detail(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    
    # Clean up strengths and weaknesses if they're generic
    if candidate.strengths == 'Good background' or not candidate.strengths:
        candidate.strengths = "Strong technical background, Relevant experience, Good communication skills"
    
    if candidate.weaknesses == 'May need training' or not candidate.weaknesses:
        candidate.weaknesses = "Consider pursuing relevant certifications, Opportunity to gain more hands-on experience"
    
    return render(request, 'candidate_detail.html', {'candidate': candidate})

# Generate Scorecard PDF
def generate_scorecard(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="scorecard_{candidate.name}.pdf"'
    
    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "HireFlow AI")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, "Candidate Scorecard")
    c.line(50, height - 75, width - 50, height - 75)
    
    # Candidate Info
    y = height - 110
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Candidate Information")
    y -= 25
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Name: {candidate.name}")
    y -= 20
    c.drawString(50, y, f"Email: {candidate.email}")
    y -= 20
    c.drawString(50, y, f"Applied for: {candidate.job.title}")
    y -= 20
    c.drawString(50, y, f"Fit Score: {candidate.fit_score}%")
    
    # Fit Score Bar
    y -= 30
    c.setFillColorRGB(0.2, 0.6, 0.9)
    c.rect(50, y - 10, (candidate.fit_score / 100) * 400, 15, fill=1)
    c.setFillColorRGB(0, 0, 0)
    c.rect(50, y - 10, 400, 15, fill=0)
    
    # Strengths
    y -= 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Strengths:")
    y -= 20
    c.setFont("Helvetica", 10)
    for strength in candidate.strengths.split(',')[:4]:
        if strength.strip():
            c.drawString(60, y, f"• {strength.strip()}")
            y -= 15
    
    # Weaknesses
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Areas for Improvement:")
    y -= 20
    c.setFont("Helvetica", 10)
    for weakness in candidate.weaknesses.split(',')[:3]:
        if weakness.strip():
            c.drawString(60, y, f"• {weakness.strip()}")
            y -= 15
    
    # Recommendation
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Recommendation:")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(60, y, candidate.recommendation[:200])
    
    # Skills
    y -= 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Matching Skills:")
    y -= 20
    c.setFont("Helvetica", 9)
    skills_text = candidate.skills_match[:200]
    c.drawString(60, y, skills_text)
    
    c.save()
    return response

# Shortlist Candidate
def shortlist_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate.is_shortlisted = True
    candidate.save()
    messages.success(request, f'{candidate.name} has been shortlisted!')
    return redirect('dashboard')

# Create Sample Job (Helper View)
def create_sample_job(request):
    Job.objects.get_or_create(
        title="Senior Full Stack Developer",
        defaults={
            'department': 'Engineering',
            'description': 'Looking for a full-stack developer with 5+ years experience in React, Python/Django, and PostgreSQL. Will be responsible for building scalable web applications.',
            'requirements': 'React.js, Python/Django, PostgreSQL, REST APIs, 5+ years experience, Strong problem-solving skills',
            'location': 'Remote'
        }
    )
    Job.objects.get_or_create(
        title="Data Scientist",
        defaults={
            'department': 'Data',
            'description': 'Seeking data scientist for building ML models and analytics pipelines.',
            'requirements': 'Python, SQL, Machine Learning, Statistics, 3+ years experience',
            'location': 'Remote'
        }
    )
    Job.objects.get_or_create(
        title="Product Manager",
        defaults={
            'department': 'Product',
            'description': 'Looking for product manager to lead AI product development.',
            'requirements': '3+ years product management, Agile experience, Technical background preferred',
            'location': 'Hybrid'
        }
    )
    messages.success(request, 'Sample jobs created!')
    return redirect('home')

def analytics(request):
    """Analytics dashboard view"""
    from django.db.models import Avg, Count
    
    total_candidates = Candidate.objects.count()
    shortlisted = Candidate.objects.filter(is_shortlisted=True).count()
    avg_fit_score = Candidate.objects.aggregate(Avg('fit_score'))['fit_score__avg'] or 0
    
    context = {
        'total_candidates': total_candidates,
        'shortlisted': shortlisted,
        'avg_fit_score': round(avg_fit_score, 1)
    }
    return render(request, 'analytics.html', context)