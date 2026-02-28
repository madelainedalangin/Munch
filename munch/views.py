from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Author

# Create your views here.

# Notes: 
# - Based on the figma, we need a login, profile, Followers List, Entry Details, Entry Management

class IndexView(generic.TemplateView):
    template_name = "munch/login.html"

class ProfileView(generic.TemplateView):
    template_name = "munch/profile.html"

class LoginView(generic.TemplateView):
    template_name = "munch/login.html"

class FollowersView(generic.TemplateView):
    template_name = "munch/followers.html"