# hello/urls.py
from django.urls import path,include
from . import views
from .views import text_to_speech_view
from .views import fetch_and_store_azure_voices
from django.contrib.auth.views import LogoutView
from .views import logout_view, logged_out_view
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.shortcuts import redirect

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services_fun, name='services_fun'),
    path('contact/', views.contact, name='contact'),
    path('get_poem/', views.get_poem, name='get_poem'),
    path('submit-form/', views.submit_form, name='submit_form'),  # Add this line
    path('success/', views.success, name='success'),
    path('HL7Parser/', views.HL7Parser, name='HL7Parser'),
    path('Hl7Parserfun/', views.Hl7Parserfun, name='Hl7Parserfun'),
    path('Outlook/', views.Outlook, name='Outlook'),
    path('outlookextract/', views.outlookextract, name='outlookextract'),
    path('edit/<int:id>/', views.edit_text_description, name='edit_text_description'),
    path('delete/<int:id>/', views.delete_text_description, name='delete_text_description'),
    path('chat/', views.chat, name='chat'),  # AJAX POST endpoint
    path('chatbot/', views.chatbot_page, name='chatbot_page'),  # New route
    path('chat/delete/<int:pk>/', views.delete_message, name='delete_message'),
    path('contact/', views.contact_page, name='contact'),
    path('send-message/', views.send_message, name='send_message'),
    path('health-analyzer/', views.health_analyzer, name='health_analyzer'),
    path('analyze-photo/', views.analyze_photo, name='analyze_photo'),
    path('tts/', text_to_speech_view, name='text_to_speech'),
    path("tts/delete/", views.delete_audio, name="delete_audio"),  # ✅ This is the fix
    path('saved-audios/', views.saved_audios_page, name='saved_audios_page'),
    path('tts/rename_page/', views.rename_page, name='rename_page'),
    path('fetch-azure-voices/', fetch_and_store_azure_voices, name='fetch_azure_voices'),
    path("tts/", views.tts_view, name="tts"),
    path("vc/", views.voice_changer_view, name="vc"),
    path('', views.home, name='home'),  # default route
    path('text_to_image/', views.text_to_image, name='text_to_image'),
    #path('login/', views.login_view, name='login'),
      path('login/', auth_views.LoginView.as_view(
        template_name='hello/login.html',
        redirect_authenticated_user=True,
        next_page='/tts/'
    ), name='login'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('dashboard/', views.dashboard_view, name='dashboard'),
   # path('logout/', LogoutView.as_view(), name='logout'),
   # path('logout/', logout_view, name='logout'),
    #path('logout/', auth_views.LogoutView.as_view(next_page='/tts/'), name='logout'),
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('tts')), name='logout'),
    path('logged-out/', logged_out_view, name='logged_out'),
    path('users/', views.user_list_view, name='user_list'),
   # path('save-favorite/', views.save_favorite_voice, name='save_favorite_voice'),
    path("save_favorite/", views.save_favorite, name="save_favorite"),
    path("get_favorites/", views.get_favorites, name="get_favorites"),
    path("delete_favorite/", views.delete_favorite_view, name="delete_favorite"),
    path('reset_voice_settings/', views.reset_voice_settings, name='reset_voice_settings'),
    path("delete_page/", views.delete_page, name="delete_page"),
    path("shorten_url/", views.shorten_url_view, name="shorten_url"),
    path("s/<str:short_hash>", views.redirect_short_url, name="redirect_short_url"),

]
