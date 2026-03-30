from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "munch"
urlpatterns = [

    # Authentication
    path('signup/', views.signup, name='signup'),

    # Built-in Django login/logout
    path('login/', auth_views.LoginView.as_view(template_name='munch/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login-success/', views.login_success_redirect, name='login_success'),
    path('logout/', views.logout_user, name='logout'),

    # Profile Management
    path('authors/<uuid:author_uuid>/', views.public_profile, name='public_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Follow Management
    path('authors/<uuid:author_uuid>/followers/', views.followers_view, name="list_followers"),
    path('authors/<uuid:author_uuid>/following/', views.list_following, name="list_following"),
    path('authors/<uuid:author_uuid>/follow_requests/', views.list_follow_requests, name="list_follow_requests"),
    path('connect/', views.connect, name='connect'),

    # Entry Management
    path('authors/<str:author_id>/entries/', views.create_entry_UI, name='create_entry_UI'),
    path('authors/<str:author_id>/entries/<str:entry_serial>/', views.display_entry_by_serial, name = 'display_entry_by_serial'),
    path('authors/<str:author_id>/entries/<str:entry_serial>/edit/', views.edit_entry, name='edit_entry'),
    path('authors/<str:author_id>/entries/<str:entry_serial>/delete/', views.delete_entry, name='delete_entry'),

    # Stream
    path('stream/', views.stream, name='stream'),
    path('api/stream/', views.stream_api, name='stream_api'),
    path('explore/', views.public_browse, name='public_browse'), # global public stream

    # Settings/Node Management
    path('settings/', views.settings_page, name='settings'),
    path('node-management/', views.node_management_page, name='node_management_page'),
    path('node-management/new/', views.create_node_connection, name='create_node_connection'),

    # Comments Management
    path('authors/<str:author_id>/entries/<str:entry_serial>/comment/', views.post_comment, name='post_comment'),


    # API endpoints

    # Inbox API
    path('api/authors/<str:target_serial>/inbox', views.inbox, name='inbox'),

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
    path('api/entries/<path:entry_fqid>/image/', views.get_image_by_fqid, name='get_image_by_fqid'),
    path('api/authors/<str:author_id>/entries/', views.create_entry, name='create_entry'),
    path('api/authors/<str:author_serial>/entries/<str:entry_serial>/image/', views.get_image_by_serial, name='get_image_by_serial'),

    # Comments API
    path('api/authors/<str:author_serial>/entries/<str:entry_serial>/comments/', views.get_entry_comments_by_serial, name='get_entry_comments_by_serial'),
    path('api/entries/<str:entry_fqid>/comments/', views.get_entry_comments_by_fqid, name='get_entry_comments_by_fqid'),
    #need to be before get_comment_by_entry_fqid because <path:comment_fqid>/  matches {serial}/likes before Django even peeps da likes URL.
    path('api/authors/<str:author_serial>/entries/<str:entry_serial>/comments/<path:comment_fqid>/likes/', views.get_comment_likes, name='get_comment_likes'),
    path('api/authors/<str:author_serial>/entries/<str:entry_serial>/comments/<path:comment_fqid>/', views.get_comment_by_fqid, name='get_comment_by_entry_fqid'),

# Commented API
    path('api/authors/<str:author_serial>/commented/', views.commented, name='commented'),
    path('api/authors/<str:author_serial>/commented/<str:comment_serial>/', views.get_comment_by_serial, name='get_comment_by_serial'),
    path('api/authors/<path:author_serial>/commented/', views.commented, name='commented_by_fqid'),
    path('api/commented/<path:comment_fqid>/', views.get_comment_by_fqid, name='get_comment_by_fqid'),


    # Likes API
    path('api/authors/<str:author_serial>/entries/<str:entry_serial>/likes/', views.get_entry_likes, name='get_entry_likes'),
    path('api/entries/<str:entry_fqid>/likes/', views.get_entry_likes_by_fqid, name='get_entry_likes_by_fqid'),

    # Liked API
    path('api/authors/<str:author_serial>/liked/', views.liked, name='liked'),
    path('api/authors/<str:author_serial>/liked/<str:like_serial>/', views.get_like_by_serial, name='get_like_by_serial'),
    path('api/authors/<path:author_serial>/liked/', views.liked, name='liked_by_fqid'),
    path('api/liked/<path:like_fqid>/', views.get_like_by_fqid, name='get_like_by_fqid'),

    # Authors API
    path('api/authors/', views.get_authors, name='get_authors'),
    path('api/authors', views.get_authors_paginated, name='get_authors_paginated'),
    path('api/authors/<path:author_id>/', views.get_author, name='get_author'),

    # Node Connection API
    path('api/nodes/', views.ConnectNode.as_view(), name='connect_node'),
    path('api/nodes/<path:node_url>', views.ManageNode.as_view(), name='refresh_node'),
    
    #hompage
    path('', views.landing, name='landing')
]