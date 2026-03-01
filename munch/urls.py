from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = "munch"
urlpatterns = [

    path('signup/', views.signup, name='signup'),

    path('authors/<uuid:author_uuid>/', views.public_profile, name='public_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    # Built-in Django login/logout
    path('login/', auth_views.LoginView.as_view(template_name='munch/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login-success/', views.login_success_redirect, name='login_success'),

    path('followers/', views.FollowersView.as_view(), name="followers"),

    path('stream/', views.stream, name='stream'),
    path('api/stream/', views.stream_api, name='stream_api'),
    
    # path('', views.IndexView.as_view(), name='index'),

    # API endpoints

    # # Authors API
    # path('api/authors/', views.get_authors, name='get_authors'),
    # path('api/authors/<str:author_id>/', views.get_author, name='get_author'),

    # Following API
    path('api/authors/<str:author_serial>/following/', views.get_following, name='get_following'),
    path('api/authors/<str:author_serial>/following/<str:target_FQID>', views.manage_following, name='manage_following'),

    # Followers API
    path('api/authors/<str:author_serial>/followers/<str:target_FQID>', views.manage_follower, name='manage_follower'),

    # Follow Request API
    path('api/authors/<str:author_serial>/follow_requests', views.get_follow_requests, name='get_follow_requests'),
    path('api/authors/<str:target_serial>/inbox', views.follow, name='follow'),

    # # Entries API
    path('api/authors/<str:author_id>/entries/<str:entry_serial>', views.manage_entry_by_serial, name='manage_entry_by_serial'),
    path('api/entries/<path:entry_FQID>/', views.manage_entry_by_FQID, name='manage_entry_by_FQID'),
    path('api/authors/<str:author_id>/entries/', views.create_entry, name='create_entry'),

    # # ENTRY PATHS FOR UI
     path('api/authors/<str:author_id>/entries/', views.create_entry_UI, name='create_entry_UI'),
    path('authors/<str:author_id>/entries/<str:entry_serial>/', views.display_entry_by_serial, name = 'display_entry_by_serial'),
    path('entries/<path:entry_FQID>/', views.display_entry_by_FQID, name = 'display_entry_by_FQID'),
    path('authors/<str:author_id>/entries/<str:entry_serial>/edit/', views.edit_entry, name='edit_entry'),
    path('authors/<str:author_id>/entries/<str:entry_serial>/delete/', views.delete_entry, name='delete_entry'),
    # path('api/entries/<str:entry_FQID>', views.manage_entry_by_FQID, name='manage_entry_by_FQID'),
    # path('api/authors/<str:author_id>/entries/', views.create_entry, name='create-entry'),

    # # Image Entries API
    # path('api/authors/<str:author_serial>/entries/<str:entry_serial>/image', views.get_image_by_serial, name='get_image_by_serial'),
    # path('api/entries/<str:entry_FQID>/image', views.get_image_by_FQID, name='get_image_by_FQID'),

    # # Comments API
    # path('api/authors/{AUTHOR_SERIAL}/inbox', views.comment, name='comment'),
    # path('api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/comments', views.get_comments_by_serial, name='get_comments_by_serial'),
    # path('api/entries/{ENTRY_FQID}/comments', views.get_comments_by_FQID, name='get_comments_by_FQID'),
    # path('api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/comments/{REMOTE_COMMENT_FQID}', views.get_comment, name='get_comment'),

    # # Commented API
    # path('api/authors/{AUTHOR_SERIAL}/commented', views., name=''),
    # path('api/authors/{AUTHOR_FQID}/commented', views., name=''),
    # path('api/authors/{AUTHOR_SERIAL}/commented/{COMMENT_SERIAL}', views., name=''),
    # path('api/commented/{COMMENT_FQID}', views., name=''),

    # # Likes API
    # path('api/authors/{AUTHOR_SERIAL}/inbox', views., name=''),
    # path('api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/likes', views., name=''),
    # path('api/entries/{ENTRY_FQID}/likes', views., name=''),
    # path('api/authors/{AUTHOR_SERIAL}/entries/{ENTRY_SERIAL}/comments/{COMMENT_FQID}/likes', views., name=''),

    # # Liked API
    # path('api/authors/{AUTHOR_SERIAL}/liked', views., name=''),
    # path('api/authors/{AUTHOR_SERIAL}/liked/{LIKE_SERIAL}', views., name=''),
    # path('api/authors/{AUTHOR_FQID}/liked', views., name=''),
    # path('api/liked/{LIKE_FQID}', views., name=''),
]