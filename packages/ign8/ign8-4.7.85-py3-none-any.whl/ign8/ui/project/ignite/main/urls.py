
from django.urls import path, include
from .views import  mainview, projectdetail

urlpatterns = [
    path('', mainview, name='ignite_home')
]