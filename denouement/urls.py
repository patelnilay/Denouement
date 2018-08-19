from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('forums', views.forums, name='forums'),
    path('forums/categories/<int:id>', views.view_forum_category_untitled, name='forum_category_untitled'),
    path('forums/categories/<int:id>/<title>', views.view_forum_category, name='forum_category_titled'),
    path('forums/thread/<int:id>', views.view_forum_thread_untitled, name='forum_thread_untitled'),
    path('forums/thread/<int:id>/<title>', views.view_forum_thread, name='forum_thread_titled'),
    path('forums/post/<category_id>', views.post_thread, name='post_thread'),
    path('account', views.view_account, name='view_account'),
    path('account/signup', views.sign_up, name='sign_up'),
    path('account/signin', views.sign_in, name='sign_in'),
    path('account/signout', views.sign_out, name='sign_out'),
    path('account/upload', views.upload_image, name='upload_picture'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

