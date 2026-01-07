from django.contrib import admin
from .models import Company, JobListing, Application

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'user')
    search_fields = ('name', 'location')

@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'deadline', 'created_at')
    list_filter = ('company', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'job', 'ranking_score', 'applied_at')
    list_filter = ('job', 'ranking_score')
    search_fields = ('full_name', 'email', 'job__title')
