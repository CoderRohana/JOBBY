from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm
from accounts.models import UserProfile

def home(request):
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_jobs': Job.objects.filter(is_active=True).count(),
    }
    return render(request, 'jobs/home.html', context)

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    has_applied = False
    
    if request.user.is_authenticated:
        has_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()
    
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'has_applied': has_applied
    })

@login_required
def post_job(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.user_type != 'employer':
        messages.error(request, 'Only employers can post jobs.')
        return redirect('home')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobForm()
    
    return render(request, 'jobs/post_job.html', {'form': form})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    profile = UserProfile.objects.get(user=request.user)
    
    if profile.user_type != 'jobseeker':
        messages.error(request, 'Only job seekers can apply for jobs.')
        return redirect('job_detail', job_id=job_id)
    
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', job_id=job_id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('job_detail', job_id=job_id)
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})

@login_required
def my_jobs(request):
    profile = UserProfile.objects.get(user=request.user)
    
    if profile.user_type == 'employer':
        jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
        return render(request, 'jobs/my_jobs.html', {'jobs': jobs})
    else:
        applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')
        return render(request, 'jobs/my_applications.html', {'applications': applications})