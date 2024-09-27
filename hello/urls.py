# hello/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('get_poem/', views.get_poem, name='get_poem'),
    path('submit-form/', views.submit_form, name='submit_form'),  # Add this line
]
