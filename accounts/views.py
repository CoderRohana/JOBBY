from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm
from .models import UserProfile

# Signup view
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                user_type=form.cleaned_data['user_type']
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            # Print errors for debugging
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

# Login view
def loginUser(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'accounts/login.html', {'next': request.POST.get('next')})

    # GET request
    return render(request, 'accounts/login.html', {'next': request.GET.get('next')})

# Logout view
def logoutUser(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')

# Profile view
@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})
