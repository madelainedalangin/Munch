from django.urls import path
from . import views

app_name = "munch"
urlpatterns = [
    path('', views.IndexView.as_view(), name='login'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('followers/', views.FollowersView.as_view(), name='followers'),

    # API endpoints

    # # Authors API
    # path('api/authors/', views.get_authors, name='get_authors'),
    # path('api/authors/<str:author_id>/', views.get_author, name='get_author'),

    # # Following API
    # path('api/authors/<str:author_serial>/following/', views.get_following, name='get_following'),
    # path('api/authors/<str:author_serial>/following/<str:target_FQID>', views.manage_following, name='manage_following'),

    # # Followers API
    # path('api/authors/<str:author_serial>/followers/<str:target_FQID>', views.manage_follower, name='manage_follower'),

    # # Follow Request API
    # path('api/authors/<str:author_serial>/follow_requests', views.get_follow_requests, name='get_follow_requests'),
    # path('api/authors/<str:target_serial>/inbox', views.follow, name='follow'),

    # # Entries API
    # path('api/authors/<str:author_id>/entries/<str:entry_serial>', views.manage_entry_by_serial, name='manage_entry_by_serial'),
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