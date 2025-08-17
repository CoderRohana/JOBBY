from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import SignUpForm
from .models import UserProfile

# Signup view
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Create UserProfile
                UserProfile.objects.create(
                    user=user,
                    user_type=form.cleaned_data.get('user_type', 'regular')  # Default fallback
                )
                # Log the user in
                login(request, user)
                messages.success(request, 'Account created successfully!')
                
                # Redirect to next URL if provided, otherwise home
                next_url = request.POST.get('next') or request.GET.get('next') or 'home'
                return redirect(next_url)
                
            except Exception as e:
                # Log the error for debugging
                print(f"Error creating user profile: {e}")
                messages.error(request, 'There was an error creating your account. Please try again.')
        else:
            # Print errors for debugging and add them to messages
            print("Form errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignUpForm()
    
    context = {
        'form': form,
        'next': request.GET.get('next', '')
    }
    return render(request, 'accounts/signup.html', context)

# Login view
def loginUser(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', '').strip()
        
        # Basic validation
        if not username or not password:
            messages.error(request, "Please enter both username and password")
            return render(request, 'accounts/login.html', {'next': next_url})
        
        try:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                    
                    # Redirect to next URL or default to home
                    if next_url and next_url.startswith('/'):  # Security check
                        return redirect(next_url)
                    else:
                        return redirect('home')
                else:
                    messages.error(request, "Your account is inactive. Please contact support.")
            else:
                messages.error(request, "Invalid username or password")
                
        except Exception as e:
            print(f"Login error: {e}")
            messages.error(request, "An error occurred during login. Please try again.")
        
        return render(request, 'accounts/login.html', {'next': next_url})
    
    # GET request
    next_url = request.GET.get('next', '')
    return render(request, 'accounts/login.html', {'next': next_url})

# Logout view
def logoutUser(request):
    try:
        logout(request)
        messages.success(request, "You have been logged out successfully!")
    except Exception as e:
        print(f"Logout error: {e}")
        messages.error(request, "An error occurred during logout.")
    
    return redirect('login')

# Profile view
@login_required
def profile(request):
    try:
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'user_type': 'regular'}  # Default value if created
        )
        if created:
            messages.info(request, "Profile created successfully!")
            
        return render(request, 'accounts/profile.html', {'profile': profile})
        
    except Exception as e:
        print(f"Profile error: {e}")
        messages.error(request, "Error loading profile.")
        return redirect('home')