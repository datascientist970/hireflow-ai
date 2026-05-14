from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100, default='Engineering')
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=100, default='Remote')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Candidate(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    resume_file = models.FileField(upload_to='resumes/')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='candidates')
    fit_score = models.FloatField(default=0.0)
    skills_match = models.TextField(blank=True)
    missing_skills = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    recommendation = models.TextField(blank=True)
    is_shortlisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.fit_score}%"