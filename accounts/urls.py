from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True,
        extra_context={'next': 'home'}
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'  # Redirect to login after logout
    ), name='logout'),
]