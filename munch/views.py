from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AuthorUpdateForm
from .models import Author,Entry
from django.contrib.auth.decorators import login_required
from .forms import SignupForm,EntryForm
from django.views import generic


# The following function from Google, Gemini, "Django Author Identity", 02-28-2026
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = AuthorUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Redirect back to their public profile after saving
            return redirect('munch:public_profile', author_uuid=request.user.uuid)
    else:
        form = AuthorUpdateForm(instance=request.user)
    
    return render(request, 'munch/edit_profile.html', {'form': form})

# The following function from Google, Gemini, "Django Author Identity", 02-28-2026
def public_profile(request, author_uuid):
    # This matches the <uuid:author_uuid> in your urls.py
    author = get_object_or_404(Author, uuid=author_uuid)
    entries = Entry.objects.filter(author__uuid=author_uuid)
    
    # For now, only pass the author. 
    # add 'posts' for user story 5 when implemented
    context = {
        'author': author,
        'entries': entries,
    }
    return render(request, 'munch/public_profile.html', context)

# The following function from Google, Gemini, "Django Author Identity", 02-28-2026
@login_required
def login_success_redirect(request):
    """
    Redirects the user to their specific public profile after login.
    """
    return redirect('munch:public_profile', author_uuid=request.user.uuid)

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

class FollowersView(generic.TemplateView):
    template_name = "munch/followers.html"

def createEntry(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.author = request.user
            entry.save()
            return redirect(entry.fqid)
    else:
        form = EntryForm()
        
    return render(request, 'munch/create_post.html', {'form': form})

def manage_entry_by_serial(request, author_id, entry_serial):
    entry = get_object_or_404(Entry, author__uuid=author_id, serial=entry_serial)
    return render(request, "munch/entry_detail.html", {"entry": entry})
