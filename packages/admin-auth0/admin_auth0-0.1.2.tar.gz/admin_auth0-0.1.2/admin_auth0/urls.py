from django.urls import path

from admin_auth0 import views

urlpatterns = [
    path('login', views.custom_login, name='login'),
    path('logout', views.logout, name='logout'),
    path('callback', views.callback, name='callback'),
]
