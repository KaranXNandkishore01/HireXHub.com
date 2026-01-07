from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import connection

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import JobListing, Application, Company
from .forms import JobPostForm, ApplicationForm, CompanyProfileForm
from .utils.resume_parser import parse_resume
from .utils.ranker import Ranker

def home(request):
    jobs = JobListing.objects.all().order_by('-created_at')[:5]
    return render(request, 'recruitment/home.html', {'featured_jobs': jobs})

@login_required
def dashboard_redirect(request):
    if request.user.is_hr:
        return redirect('hr_dashboard')
    elif request.user.is_applicant:
        return redirect('applicant_dashboard')
    else:
        return redirect('home')

@login_required
def hr_dashboard(request):
    if not request.user.is_hr:
        return redirect('home')
    
    # Check if company profile exists
    if not hasattr(request.user, 'company'):
        return redirect('create_company')

    jobs = JobListing.objects.filter(company=request.user.company)
    total_jobs = jobs.count()
    total_applicants = Application.objects.filter(job__company=request.user.company).count()

    return render(request, 'recruitment/hr_dashboard.html', {
        'jobs': jobs, 
        'company': request.user.company,
        'total_jobs': total_jobs,
        'total_applicants': total_applicants
    })

@login_required
def applicant_dashboard(request):
    if not request.user.is_applicant:
        return redirect('home')

    jobs = JobListing.objects.all()
    applications = Application.objects.filter(user=request.user)
    applied_job_ids = applications.values_list('job_id', flat=True)
    
    total_applications = applications.count()

    return render(request, 'recruitment/applicant_dashboard.html', {
        'jobs': jobs,
        'applications': applications,
        'applied_job_ids': applied_job_ids,
        'total_applications': total_applications
    })

@login_required
def create_company(request):
    if not request.user.is_hr:
        return redirect('home')
    
    company = getattr(request.user, 'company', None)
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            company.save()
            return redirect('hr_dashboard')
    else:
        form = CompanyProfileForm(instance=company)
    
    return render(request, 'recruitment/company_form.html', {'form': form})

@login_required
def post_job(request):
    if not request.user.is_hr or not hasattr(request.user, 'company'):
        return redirect('hr_dashboard')

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user.company
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('hr_dashboard')
    else:
        form = JobPostForm()
    
    return render(request, 'recruitment/job_form.html', {'form': form})

@login_required
def job_detail(request, pk):
    job = get_object_or_404(JobListing, pk=pk)
    
    # Check if already applied
    has_applied = False
    if request.user.is_authenticated and request.user.is_applicant:
        has_applied = Application.objects.filter(user=request.user, job=job).exists()

    # Check if job application window is open
    from django.utils import timezone
    is_open = True
    today = timezone.now().date()
    
    if job.application_start_date:
        if today < job.application_start_date:
            is_open = False
    
    if today > job.deadline:
        is_open = False

    if request.method == 'POST' and request.user.is_applicant and not has_applied:
        if not is_open:
             messages.error(request, "Applications for this job are currently closed.")
             return redirect('job_detail', pk=pk)

        form = ApplicationForm(request.POST, request.FILES, job=job)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.job = job
            application.save() # Saves file to disk

            # Calculate Ranking Score
            try:
                resume_text = parse_resume(application.resume.path)
                if resume_text:
                    ranker = Ranker()
                    resumes_data = [{'filename': application.resume.name, 'text': resume_text}]
                    # Use job description AND required skills for better matching
                    requirements = f"{job.required_skills} {job.description}"
                    results = ranker.rank_resumes(resumes_data, requirements)
                    
                    if results:
                        application.ranking_score = results[0]['score']
                        application.save()
            except Exception as e:
                print(f"Ranking failed: {e}")

            # Notify HR
            send_mail(
                subject=f"New Application for {job.title}",
                message=f"Hello,\n\nYou have received a new application from {application.full_name} for the position of {job.title}.\n\nReview it on your dashboard.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[job.company.user.email],
                fail_silently=True
            )

            # Notify Applicant
            send_mail(
                subject=f"Application Received: {job.title}",
                message=f"Dear {application.full_name},\n\nWe have received your application for {job.title} at {job.company.name}. We will review it shortly.\n\nBest regards,\n{job.company.name}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[application.email],
                fail_silently=True
            )

            messages.success(request, 'Application submitted successfully!')
            return redirect('applicant_dashboard')
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['full_name'] = request.user.get_full_name()
            initial_data['email'] = request.user.email
            if hasattr(request.user, 'profile'):
                initial_data['phone'] = request.user.profile.phone_number
        
        form = ApplicationForm(initial=initial_data, job=job)

    return render(request, 'recruitment/job_detail.html', {
        'job': job, 
        'form': form, 
        'has_applied': has_applied,
        'is_open': is_open
    })

@login_required
def view_applicants(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    if not request.user.is_hr or job.company.user != request.user:
        return redirect('hr_dashboard')
    
    applications = job.applications.all().order_by('-ranking_score')
    return render(request, 'recruitment/view_applicants.html', {'job': job, 'applications': applications})

@login_required
def update_application_status(request, application_id, status):
    application = get_object_or_404(Application, id=application_id)
    
    # Ensure only the job owner can update status
    if request.user.is_hr and application.job.company.user == request.user:
        if status == 'Accepted':
            application.status = status
            application.save()
            
            # Notify Applicant
            send_mail(
                subject=f"Congratulations! Application Accepted for {application.job.title}",
                message=f"Dear {application.full_name},\n\nWe are pleased to inform you that your application for {application.job.title} at {application.job.company.name} has been ACCEPTED.\n\nOur team will contact you shortly regarding the next steps.\n\nBest regards,\n{application.job.company.name}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[application.email],
                fail_silently=True
            )
            messages.success(request, f"Application accepted and applicant notified.")
            
        elif status == 'Rejected':
            # Notify Applicant before deletion
            send_mail(
                subject=f"Update on your application for {application.job.title}",
                message=f"Dear {application.full_name},\n\nThank you for your interest in {application.job.title} at {application.job.company.name}. After careful consideration, we regret to inform you that we will not be moving forward with your application at this time.\n\nWe wish you the best in your job search.\n\nBest regards,\n{application.job.company.name}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[application.email],
                fail_silently=True
            )
            
            # Delete the application record as requested
            application.delete()
            messages.warning(request, f"Application rejected and record deleted.")
            
        else:
            messages.error(request, "Invalid status update.")
    else:
        messages.error(request, "Permission denied.")
    
    return redirect('view_applicants', job_id=application.job.id)

def about(request):
    return render(request, 'recruitment/about.html')

def services(request):
    return render(request, 'recruitment/services.html')

def contact(request):
    return render(request, 'recruitment/contact.html')

def resume_scorer(request):
    score = None
    match_count = 0
    total_skills = 0
    missing_skills = []
    
    # Predefined Job Roles and their keywords
    JOB_ROLES = {
        'Python Developer': 'python, django, flask, sql, rest api, docker, git, aws, linux',
        'Frontend Developer': 'html, css, javascript, react, angular, vue, typescript, bootstrap, responsive design',
        'Data Scientist': 'python, r, sql, machine learning, pandas, numpy, scikit-learn, tensorflow, statistics',
        'Java Developer': 'java, spring boot, hibernate, sql, maven, gradle, microservices, git',
        'DevOps Engineer': 'linux, bash, docker, kubernetes, aws, azure, jenkins, git, terraform, ci/cd',
    }

    if request.method == 'POST':
        # Get input: either from selected role or custom input
        role_selection = request.POST.get('job_role')
        skills_input = request.POST.get('skills', '')
        uploaded_file = request.FILES.get('resume')

        # Use role keywords if selected and no custom override
        target_skills_text = ""
        if role_selection and role_selection in JOB_ROLES:
            target_skills_text = JOB_ROLES[role_selection]
        
        # Merge or use custom skills if provided
        if skills_input:
            target_skills_text += ", " + skills_input

        if target_skills_text and uploaded_file:
            # 1. Parse Skills (for missing keywords display)
            target_skills = [s.strip().lower() for s in target_skills_text.split(',') if s.strip()]
            total_skills = len(target_skills)

            # 2. Extract Text
            text_content = ""
            try:
                filename = uploaded_file.name.lower()
                if filename.endswith('.pdf'):
                    import pypdf
                    reader = pypdf.PdfReader(uploaded_file)
                    for page in reader.pages:
                        text_content += page.extract_text() + " "
                elif filename.endswith('.docx'):
                    import docx
                    doc = docx.Document(uploaded_file)
                    for para in doc.paragraphs:
                        text_content += para.text + " "
                else:
                    # Fallback to text
                    text_content = uploaded_file.read().decode('utf-8', errors='ignore')
                
                text_content = text_content.lower()

            except Exception as e:
                print(f"Error reading resume: {e}")
                text_content = ""

            # 3. Calculate Score using TF-IDF Ranker
            try:
                ranker = Ranker()
                resumes_data = [{'filename': 'uploaded_resume', 'text': text_content}]
                # Use target skills as the "job description" for ranking
                ranking_results = ranker.rank_resumes(resumes_data, target_skills_text)
                
                if ranking_results:
                    score = int(ranking_results[0]['score'])
                else:
                    score = 0
            except Exception as e:
                print(f"Ranking error: {e}")
                score = 0

            # 4. Identify Missing Keywords (Set logic)
            matched_skills = []
            for skill in target_skills:
                if skill in text_content:
                    matched_skills.append(skill)
                else:
                    missing_skills.append(skill)
            
            match_count = len(matched_skills)
            
            # Hybrid Score (Optional: Average of TF-IDF and Keyword Match?)
            # For now, let's Stick to Ranker score as the primary, but ensure it's not 0 if keywords match.
            # Or use keyword match count for a simpler "Keyword Coverage" metric.
            
            # Let's use the Ranker score as the "AI Score"
            if score < 10 and match_count > 0:
                 # Fallback if TF-IDF is too strict for short inputs
                 score = int((match_count / total_skills) * 100)

    return render(request, 'recruitment/resume_scorer.html', {
        'score': score,
        'match_count': match_count,
        'total_skills': total_skills,
        'missing_skills': missing_skills,
        'job_roles': JOB_ROLES
    })

@login_required
def smart_matching(request):
    # Simple recommendation logic: Filter jobs by skills matching user's resume (if exists) or profile
    # For now, return all jobs as "Recommended" to demonstrate UI
    recommended_jobs = JobListing.objects.all().order_by('-created_at')[:5]
    return render(request, 'recruitment/smart_matching.html', {'recommended_jobs': recommended_jobs})

def analytics_dashboard(request):
    # Gather some basic stats
    total_jobs = JobListing.objects.count()
    total_applications = Application.objects.count()
    companies_count = Company.objects.count()
    
    context = {
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'companies_count': companies_count,
    }
    return render(request, 'recruitment/analytics.html', context)



def secure_recruiting(request):
    return render(request, 'recruitment/secure_recruiting.html')

def health_check(request):
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = True
    except Exception as e:
        db_status = False

    return JsonResponse({
        "status": "ok",
        "database": db_status
    })

