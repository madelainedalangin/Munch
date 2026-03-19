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
    path('logout/', views.logout_user, name='logout'),

    path('explore/', views.public_browse, name='public_browse'), # global public stream

    path('authors/<uuid:author_uuid>/followers/', views.followers_view, name="list_followers"),
    path('authors/<uuid:author_uuid>/following/', views.list_following, name="list_following"),
    path('authors/<uuid:author_uuid>/follow_requests/', views.list_follow_requests, name="list_follow_requests"),

    path('stream/', views.stream, name='stream'),
    path('api/stream/', views.stream_api, name='stream_api'),

    path('settings/', views.settings_page, name='settings'),
    
    # path('', views.IndexView.as_view(), name='index'),

    # API endpoints

    # Inbox API
    path('api/authors/<str:target_serial>/inbox', views.inbox, name='inbox'),

    # Authors API
    path('api/authors/', views.get_authors, name='get_authors'),
    path('api/authors', views.get_authors_paginated, name='get_authors_paginated'),

    # Following API
    path('api/authors/<str:author_serial>/following/', views.get_following, name='get_following'),
    path('api/authors/<str:author_serial>/following/<path:target_FQID>', views.manage_following, name='manage_following'),

    # Followers API
    path('api/authors/<str:author_serial>/followers/<path:target_FQID>', views.manage_follower, name='manage_follower'),

    # Follow Request API
    path('api/authors/<str:author_serial>/follow_requests', views.get_follow_requests, name='get_follow_requests'),

    # Entries API
    path('api/authors/<str:author_id>/entries/<str:entry_serial>/', views.manage_entry_by_serial, name='manage_entry_by_serial'),
    path('api/entries/<path:entry_FQID>/', views.manage_entry_by_FQID, name='manage_entry_by_FQID'),
    path('api/authors/<str:author_id>/entries/', views.create_entry, name='create_entry'),

    # ENTRY PATHS FOR UI
    path('authors/<str:author_id>/entries/', views.create_entry_UI, name='create_entry_UI'),
    path('authors/<str:author_id>/entries/<str:entry_serial>/', views.display_entry_by_serial, name = 'display_entry_by_serial'),
    # path('entries/<path:entry_FQID>/', views.display_entry_by_FQID, name = 'display_entry_by_FQID'),
    path('authors/<str:author_id>/entries/<str:entry_serial>/edit/', views.edit_entry, name='edit_entry'),
    path('authors/<str:author_id>/entries/<str:entry_serial>/delete/', views.delete_entry, name='delete_entry'),
    # path('api/entries/<str:entry_FQID>', views.manage_entry_by_FQID, name='manage_entry_by_FQID'),
    # path('api/authors/<str:author_id>/entries/', views.create_entry, name='create-entry'),

    # Image Entries API
    path('api/authors/<str:author_serial>/entries/<str:entry_serial>/image/', views.get_image_by_serial, name='get_image_by_serial'),
    path('api/entries/<path:entry_fqid>/image/', views.get_image_by_fqid, name='get_image_by_fqid'),

    # Comments API
    # path('api/authors/{AUTHOR_SERIAL}/inbox', views.comment, name='comment'),
    path('api/authors/<str:author_serial>/entries/<str:entry_serial>/comments/', views.get_entry_comments_by_serial, name='get_entry_comments_by_serial'),
    path('authors/<str:author_id>/entries/<str:entry_serial>/comment/', views.post_comment, name='post_comment'),
    path('api/commented/<path:comment_fqid>/', views.get_comment_by_fqid, name='get_comment_by_fqid'),
    
    # FQID-based comments
    path('api/entries/<str:entry_fqid>/comments/', views.get_entry_comments_by_fqid, name='get_entry_comments_by_fqid'),

    # Commented API
    path('api/authors/<str:author_serial>/commented/', views.commented, name='commented'),
    # path('api/authors/{AUTHOR_FQID}/commented', views., name=''),
    path('api/authors/<str:author_serial>/commented/<str:comment_serial>/', views.get_comment_by_serial, name='get_comment_by_serial'),
    # path('api/commented/{COMMENT_FQID}', views., name=''),

    # Likes API
    path('api/authors/<str:author_serial>/entries/<str:entry_serial>/likes/', views.get_entry_likes, name='get_entry_likes'),
    path('api/authors/<str:author_serial>/entries/<str:entry_serial>/comments/<str:comment_serial>/likes/', views.get_comment_likes, name='get_comment_likes'),
    path('api/liked/<path:like_fqid>/', views.get_like_by_fqid, name='get_like_by_fqid'),
    path('api/entries/<str:entry_fqid>/likes/', views.get_entry_likes_by_fqid, name='get_entry_likes_by_fqid'),

    # Liked API
    path('api/authors/<str:author_serial>/liked/', views.liked, name='liked'),
    path('api/authors/<str:author_serial>/liked/<str:like_serial>/', views.get_like_by_serial, name='get_like_by_serial'),
    # path('api/authors/{AUTHOR_FQID}/liked', views., name=''),
    # path('api/liked/{LIKE_FQID}', views., name=''),

    # Author API at the last
    path('api/authors/<path:author_id>/', views.get_author, name='get_author'),
]