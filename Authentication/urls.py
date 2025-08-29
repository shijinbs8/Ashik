from django.urls import path
from .views import *

urlpatterns=[
    path('',Login,name="login"),
    path('register/',register, name='register'),
    
]