from django.urls import path
from .views import signup_htmx, login_htmx,SignupView,user_logout,logout_htmx

urlpatterns = [
    path('createUser/', SignupView.as_view(), name='signup'),
    path('signup/', signup_htmx, name='signup_htmx'),
    path('login/', login_htmx, name='login_htmx'),
    path('logout/', logout_htmx, name='logout_htmx'),
path('logout/', user_logout, name='logout'),

    # You can add paths for login/logout if not using DRF’s token or session endpoints
]
