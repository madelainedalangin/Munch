from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q #without Q, Django gonna always filter to an "AND"

from munch.serializers import *
from munch.models import *
from munch.forms import AuthorUpdateForm
from munch.utils import sync_github_activity

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
@login_required
def public_profile(request, author_uuid):
    
    author = get_object_or_404(Author, uuid=author_uuid)

    try:
        sync_github_activity(author)
    except Exception as e:
        print(f"GitHub sync failed: {e}")

    entries = Entry.objects.filter(author=author)

    if request.user.is_authenticated and request.user.is_superuser:
        entries = entries.order_by("-published")
    elif request.user.is_authenticated and request.user == author:
        entries = entries.exclude(visibility='DELETED').order_by("-published")
    else:
        visibility_filter = Q(visibility='PUBLIC')

        if request.user.is_authenticated:
            follows_author = Follow.objects.filter(
                actor=request.user,
                object=author,
                status='accepted'
            ).exists()
            author_follows_user = Follow.objects.filter(
                actor=author,
                object=request.user,
                status='accepted'
            ).exists()
            is_friend = follows_author and author_follows_user

            if follows_author:
                visibility_filter |= Q(visibility='UNLISTED')
            if is_friend:
                visibility_filter |= Q(visibility='PRIVATE')

        entries = entries.exclude(visibility='DELETED').filter(visibility_filter)

    entries = entries.order_by('-published')
    #This is to have the followers and following count to show on public profile
    #Previously the 0s were hardcoded in the js file but not anymore
    following_count = Follow.objects.filter(actor=author, status='accepted').count()
    followers_count = Follow.objects.filter(object=author, status='accepted').count()

    context = {
        'author': author,
        'entries': entries,
        'following_count': following_count,
        'followers_count': followers_count,
    }
    return render(request, 'munch/public_profile.html', context)