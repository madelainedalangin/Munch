from django.contrib import admin
from .models import Author

# add/edit/delete authors via /admin
admin.site.register(Author)