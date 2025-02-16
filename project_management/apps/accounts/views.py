from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate,logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
'''
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]
'''
class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email', '')
        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')

        # Simple validation checks
        if not username or not password or not password_confirm:
            return Response(
                {"detail": "Username, password, and password_confirm are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password != password_confirm:
            return Response(
                {"detail": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "Username is already taken."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Optional: Automatically log the user in right after signup
        # If you want to auto-login, then authenticate + login them:
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

        return Response(
            {"detail": "User created successfully."},
            status=status.HTTP_201_CREATED
        )



class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Django's built-in login
            return Response({"detail": "Logged in successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)  # Django's built-in logout
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)



#htmx views

#@ensure_csrf_cookie
def signup_htmx(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email', '')
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')

            # Basic validation
            if not username or not password or not password_confirm:
                return render(request, 'accounts/partials/_signup_form.html', {
                    'error': 'Username, password, and confirm password are required',
                    'username': username,
                    'email': email
                }, status=400)

            if password != password_confirm:
                return render(request, 'accounts/partials/_signup_form.html', {
                    'error': 'Passwords do not match',
                    'username': username,
                    'email': email
                }, status=400)

            if User.objects.filter(username=username).exists():
                return render(request, 'accounts/partials/_signup_form.html', {
                    'error': 'Username already taken',
                    'username': username,
                    'email': email
                }, status=400)

            # Create user
            user = User.objects.create_user(username=username, email=email, password=password)
            print('userf',user)
            # Auto-login
            user = authenticate(username=username, password=password)
            print('userx',user)

            if user is not None:
                login(request, user)

            print('here')

            # Return a success partial
            return render(request, 'accounts/partials/_signup_success.html', {
                'username': username
            }, status=201)

        # If GET request or any other method, render the full page (with a partial inside it)
        return render(request, 'accounts/signup.html')

    except Exception as e:  # Corrected exception handling
        print('Errorxxx:', e)


@ensure_csrf_cookie
def login_htmx(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            return render(request, 'accounts/partials/_login_form.html', {
                'error': 'Username and password required.',
            }, status=400)

        user = authenticate(username=username, password=password)
        print('user',user)

        if user is not None:
            login(request, user)
            return render(request, 'accounts/partials/_login_success.html', {
                'username': user.username
            })
        else:
            return render(request, 'accounts/partials/_login_form.html', {
                'error': 'Invalid credentials.',
            }, status=401)

    # If GET, render full page with the partial
    return render(request, 'accounts/login.html')


def logout_htmx(request):

    if request.method == 'GET':
        logout(request)
        # Return a partial that might show a "You have been logged out" message
        return render(request, 'accounts/partials/_logout_success.html')


@login_required
def user_logout(request):
    """Logs out the current user and redirects to login or homepage."""
    logout(request)
    return redirect('login')  # or wherever you want to redirect

