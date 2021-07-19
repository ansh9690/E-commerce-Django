from django.urls import path
from accounts.views import register, login_view, logout_view

app_name = "accounts"

urlpatterns = [
    # register / login / logout 
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
