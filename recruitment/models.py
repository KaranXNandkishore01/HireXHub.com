from django.db import models
from django.conf import settings

class Company(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company')
    name = models.CharField(max_length=255)
    description = models.TextField()
    website = models.URLField(blank=True)
    location = models.CharField(max_length=255)
    # Using FileField to avoid Pillow dependency initially, can switch to ImageField later
    logo = models.FileField(upload_to='company_logos/', blank=True, null=True)

    def __str__(self):
        return self.name

class JobListing(models.Model):
    # Job Listing Model updated
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.TextField(help_text="Comma-separated skills")
    salary = models.CharField(max_length=100, blank=True)
    
    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
    ]
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='Full Time')

    WORK_MODE_CHOICES = [
        ('On Site', 'On Site'),
        ('Remote', 'Remote'),
    ]
    work_mode = models.CharField(max_length=20, choices=WORK_MODE_CHOICES, default='On Site')

    start_date = models.DateField(null=True, blank=True)
    application_start_date = models.DateField(null=True, blank=True, help_text="Date when applications start opening")
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def formatted_created_at(self):
        return self.created_at.strftime('%Y-%m-%d')

    def __str__(self):
        return self.title

class Application(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    
    # Enhanced Application Fields
    full_name = models.CharField(max_length=255, default="")
    email = models.EmailField(default="")
    phone = models.CharField(max_length=20, default="")
    start_date = models.DateField(null=True, blank=True)
    available_interview_date = models.DateTimeField(null=True, blank=True)
    cover_letter = models.TextField(blank=True, default="")
    
    resume = models.FileField(upload_to='resumes/')
    ranking_score = models.FloatField(default=0.0)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"
