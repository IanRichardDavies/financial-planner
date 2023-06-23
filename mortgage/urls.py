from django.urls import path
from . import views

app_name = 'mortgage'
urlpatterns = [
    path('', views.mortgage_home, name='mortgage'),
    ]