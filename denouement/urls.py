from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('forums/', views.forums, name='forums'),
    path('forums/user/<username>/', views.view_user_profile, name='view_user_profile'),
    path('forums/user/<username>/comment/<int:comment_id>/delete/', views.delete_profile_comment, name='delete_profile_comment'),
    path('forums/thread/<int:thread_id>/delete/', views.delete_thread, name='delete_thread'),
    path('forums/thread/<int:thread_id>/lock/', views.lock_thread, name='lock_thread'),
    path('forums/thread/<int:thread_id>/pin/', views.pin_thread, name='pin_thread'),
    path('forums/categories/<int:id>/', views.view_forum_category_untitled, name='forum_category_untitled'),
    path('forums/categories/<int:id>/<title>/', views.view_forum_category, name='forum_category_titled'),
    path('forums/thread/<int:id>/', views.view_forum_thread_untitled, name='forum_thread_untitled'),
    path('forums/thread/<int:thread_id>/<int:post_id>/delete/', views.delete_forum_post, name='delete_forum_post'),

    path('forums/thread/<int:thread_id>/<int:post_id>/edit/', views.edit_forum_post, name='edit_forum_post'),    
    path('forums/thread/<int:id>/<title>/', views.view_forum_thread, name='forum_thread_titled'),
    path('forums/post/<category_id>/', views.post_thread, name='post_thread'),
    path('forums/account/signup/', views.sign_up, name='sign_up'),
    path('forums/account/signin/', views.sign_in, name='sign_in'),
    path('forums/account/signout/', views.sign_out, name='sign_out'),
    path('forums/account/upload/', views.upload_image, name='upload_picture'),
    path('forums/user/<username>/<action>', views.user_moderation, name='user_moderation')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

