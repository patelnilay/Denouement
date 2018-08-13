from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('account', views.view_account, name="view_account"),
    path('account/signup', views.sign_up, name='sign_up'),
    path('account/signin', views.sign_in, name='sign_in'),
    path('account/signout', views.sign_out, name='sign_out'),
    path('account/upload', views.upload_image, name='upload_picture')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

