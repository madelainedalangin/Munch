from django.contrib import admin
from .models import *

# add/edit/delete authors via /admin
admin.site.register(Author)
admin.site.register(Entry)
admin.site.register(Comment)