from django import forms
from .models import JobListing, Application, Company

class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = ['title', 'description', 'required_skills', 'salary', 'job_type', 'work_mode', 'application_start_date', 'start_date', 'deadline']
        labels = {
            'application_start_date': 'Applications Open From',
            'deadline': 'Applications Close On',
            'start_date': 'Job Start Date',
            'job_type': 'Job Type',
            'work_mode': 'Work Mode',
        }
        widgets = {
            'application_start_date': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date:
            from django.utils import timezone
            if start_date < timezone.now().date():
                raise forms.ValidationError("Job start date cannot be in the past.")
        return start_date

    def clean_application_start_date(self):
        app_date = self.cleaned_data.get('application_start_date')
        if app_date:
            from django.utils import timezone
            if app_date < timezone.now().date():
                raise forms.ValidationError("Application start date cannot be in the past.")
        return app_date

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        app_start_date = self.cleaned_data.get('application_start_date')
        
        if deadline:
            from django.utils import timezone
            if deadline < timezone.now().date():
                raise forms.ValidationError("Deadline cannot be in the past.")
            if app_start_date and deadline < app_start_date:
                raise forms.ValidationError("Deadline must be after the application start date.")
        return deadline

    def __init__(self, *args, **kwargs):
        super(JobPostForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['full_name', 'email', 'phone', 'start_date', 'available_interview_date', 'cover_letter', 'resume']
        labels = {
            'cover_letter': 'About You',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'available_interview_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'cover_letter': forms.Textarea(attrs={'rows': 4}),
            'resume': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date:
            from django.utils import timezone
            if start_date < timezone.now().date():
                raise forms.ValidationError("Start date cannot be in the past.")
            
            # Validate against job start date if available
            if self.job and self.job.start_date:
                if start_date < self.job.start_date:
                    raise forms.ValidationError(f"Start date cannot be before the job's start date ({self.job.start_date}).")
        return start_date

    def clean_available_interview_date(self):
        interview_date = self.cleaned_data.get('available_interview_date')
        if interview_date:
            from django.utils import timezone
            if interview_date < timezone.now():
                raise forms.ValidationError("Interview date cannot be in the past.")
        return interview_date

    def __init__(self, *args, **kwargs):
        self.job = kwargs.pop('job', None)
        super(ApplicationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Add specific placeholders
        self.fields['full_name'].widget.attrs.update({'placeholder': 'Enter your full name'})
        self.fields['email'].widget.attrs.update({'placeholder': 'example@example.com'})
        self.fields['phone'].widget.attrs.update({'placeholder': '(000) 000-0000'})


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'website', 'location', 'logo']

    def __init__(self, *args, **kwargs):
        super(CompanyProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

