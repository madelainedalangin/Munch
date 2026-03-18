from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def settings_page(request): #renamed to settings_page its overwriting our import settings from django
    return render(request, 'munch/settings.html')
