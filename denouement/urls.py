from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('account/signup', views.sign_up, name='sign_up'),
    path('account/signin', views.sign_in, name='sign_in'),
    path('account/signout', views.sign_out, name='sign_out')
]

