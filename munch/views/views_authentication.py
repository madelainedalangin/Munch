from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from munch.serializers import *
from munch.models import *
from munch.forms import SignupForm

# The following function from Google, Gemini, "Django Author Identity", 02-28-2026
@login_required
def login_success_redirect(request):
    """
    Redirects the user to the stream after login.
    
    If user is not approved by admin, log them out and send them back to login
    """
    if not request.user.is_approved:
        from django.contrib.auth import logout
        logout(request)
        from django.contrib import messages
        messages.error(request, "Account pending for approval by admin.")
        return redirect('munch:login')
    return redirect('munch:stream')

# The following function from Google, Gemini, "Django Login Function", 03-01-2026
def logout_user(request):
    from django.contrib.auth import logout
    logout(request)
    from django.contrib import messages
    messages.info(request, "You have successfully logged out.")
    return redirect('munch:login')

# The following function from Google, Gemini, "Django Author Identity", 02-28-2026
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('munch:login') # Send to login after signup
    else:
        form = SignupForm()
    return render(request, 'munch/signup.html', {'form': form})