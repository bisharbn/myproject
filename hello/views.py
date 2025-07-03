# hello/views.py
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
import logging
import openai
from .forms import TextDescriptionForm
from .models import TextDescriptionf
from django.core.paginator import Paginator
import hl7
from datetime import datetime
import re
import win32com.client
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import json
from .models import ChatMessage
import markdown
import bleach
import html  # For unescaping HTML entities
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, render_template, redirect
import base64
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import base64
from .photoenchancer import LinkedinPhotoEnhancer  # Adjust import based on your file structure
import uuid
from gtts import gTTS
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import glob
from django.shortcuts import redirect
from django.shortcuts import render
from .models import GeneratedAudio,AudioPage,AzureVoice,FavoriteVoice,SiteSetting
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from django.utils.timesince import timesince
import requests
import xml.etree.ElementTree as ET
from .utils.voice_utils import get_flag_emoji, get_language_display
from .models import UserProfile
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
import hashlib
from django.shortcuts import redirect


logger = logging.getLogger(__name__)

favorite_voices = []
SHORT_URL_MAP = {}
@login_required
def get_favorites(request):
    favorites = FavoriteVoice.objects.filter(user=request.user)
    voice_map = {v.short_name: f"{get_flag_emoji(v.locale)} {get_language_display(v.locale)} - {v.short_name.split('-')[-1].replace('Neural', '')} ({v.gender[0]})" for v in VOICE_CHOICES}
    return JsonResponse({
        "favorites": list(favorites.values("voice")),
        "voice_display_map": voice_map,
    })



@login_required
def save_favorite(request):
    if request.method == "POST":
        data = json.loads(request.body)
        voice = data.get("voice")
        if voice:
            FavoriteVoice.objects.get_or_create(user=request.user, voice=voice)
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

@login_required
def delete_favorite_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        voice = data.get("voice", "").strip().replace("{", "").replace("}", "")
        logger.info(f"🗑️ Deleting favorite voice: '{voice}' for user {request.user.username}")
        
        if voice:
            deleted_count, _ = FavoriteVoice.objects.filter(user=request.user, voice=voice).delete()
            logger.info(f"✅ Deleted {deleted_count} voice(s)")
            return JsonResponse({"success": True})
    
    return JsonResponse({"success": False}, status=400)


def user_list_view(request):
    users = User.objects.all()
    return render(request, 'hello/user_list.html', {'users': users})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Already logged in, go to dashboard
    return render(request, 'hello/login.html')

def logout_view(request):
    logout(request)
    return redirect('logged_out')  # Redirect to custom page

def logged_out_view(request):
    return render(request, 'hello/loggedout.html')


def dashboard_view(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None

    return render(request, 'hello/dashboard.html', {'profile': profile})
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Already logged in, go to dashboard
    return render(request, 'hello/login.html')

def text_to_image(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '').strip()

            if not prompt:
                return JsonResponse({'error': "Prompt is required."}, status=400)
            logger.info(f"Generating image for prompt: {prompt}")
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                n=1
            )

            image_url = response.data[0].url
            return JsonResponse({'image_url': image_url})

        except Exception as e:
            return JsonResponse({'error': f"Image generation failed: {str(e)}"}, status=500)

    elif request.method == 'GET':
        return render(request, "hello/text_to_image.html")  # your form page

    return HttpResponseNotAllowed(['GET', 'POST'])











AZURE_TTS_KEY = '9puxjTqOVfvLt5nys1wx5Qr7LT9nHv3ObzLNNoWNMfPuyCDM9TyzJQQJ99BFACYeBjFXJ3w3AAAYACOGkhCL'
AZURE_TTS_REGION = 'eastus'
#AZURE_ENDPOINT = f"https://{AZURE_TTS_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
#AZURE_ENDPOINT = f"https://{AZURE_TTS_REGION}.api.cognitive.microsoft.com"
#AZURE_ENDPOINT = "https://eastus.tts.speech.microsoft.com/cognitiveservices/v1"
AZURE_ENDPOINT = "https://eastus.api.cognitive.microsoft.com/cognitiveservices/v1"
AZURE_ENDPOINT = f"https://{AZURE_TTS_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"


AUDIO_DIR = "media/audio"

AUDIO_DIR = os.path.join(settings.MEDIA_ROOT, "audio")
AUDIO_URL = os.path.join(settings.MEDIA_URL, "audio")

voice_lang_map = {
    "en": "en",
    "en-uk": "en-uk",
    "en-us": "en-us",
    "fr": "fr",
    "de": "de",
    "hi": "hi",
    "ar": "ar",
    "ml": "ml",  # ✅ Malayalam
}

VOICE_CHOICES = AzureVoice.objects.all().order_by('locale', 'short_name')


# VOICE_CHOICES = [
#     'en-US-JennyNeural',
#     'en-US-GuyNeural',
#     'en-IN-NeerjaNeural',
#     'en-IN-PrabhatNeural',
#     'ml-IN-MidhunNeural',
#     'ml-IN-SobhanaNeural'
# ]

STYLE_CHOICES = [
    'cheerful', 'angry', 'sad', 'excited', 'friendly', 'empathetic'
]

@csrf_exempt
def text_to_speech_view(request):
    audio_url = None
    audio_list = []    
    is_authenticated = request.user.is_authenticated
    user = request.user if is_authenticated else None

    pages = AudioPage.objects.filter(user=user).order_by('-created_at') if is_authenticated else []

    try:
        setting = SiteSetting.objects.first()
        show_news_bar = setting.is_active()
        news_text = setting.news_text
        scroll_speed = setting.scroll_speed
        scroll_direction = setting.scroll_direction
        show_close_button = setting.show_close_button
    except:
        show_news_bar = False
        news_text = ""
        scroll_speed = 20
        scroll_direction = "left"
        show_close_button = True



    # 🆕 Create default page for new users
    if is_authenticated and not pages.exists():
        AudioPage.objects.create(
            user=user,
            name="My First Page",
            default_voice="en-US-JennyNeural"
        )
    if request.user.is_authenticated:
        favorite_voices = FavoriteVoice.objects.filter(user=request.user).values("voice", "style")

        pages = AudioPage.objects.filter(user=user).order_by('-created_at')

    selected_page_id = request.GET.get("page") or (pages.first().id if pages else None)

    # Default voice settings (even for anonymous users, from session)
    selected_voice = request.session.get("selected_voice", "en-US-JennyNeural")
    selected_style = request.session.get("selected_style", "")
    selected_rate = request.session.get("selected_rate", "0%")
    if selected_rate.endswith('%'):
        selected_rate = selected_rate[:-1]
    selected_pitch = request.session.get("selected_pitch", "0%")
    selected_volume = request.session.get("selected_volume", "default")
    logger.info(f"Selected voice: {selected_voice}, style: {selected_style}, rate: {selected_rate}, pitch: {selected_pitch}, volume: {selected_volume}")  
    if request.method == "POST":
        if not is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"error": "Authentication required"}, status=403)
            return redirect('/auth/login/google-oauth2/?next=/tts/')

        if "generate" in request.POST:
            text = request.POST.get("text")
            page_id = request.POST.get("page_id")
            if not page_id or not page_id.isdigit():
                return redirect('/tts/')
            page_id = int(page_id)

            voice = request.POST.get("voice") or selected_voice
            style = request.POST.get("style") or selected_style
            rate = request.POST.get("rate") + "%" or  selected_rate
            pitch = request.POST.get("pitch") + "%" or  selected_pitch
            volume = map_slider_to_volume(int(request.POST.get("volume"))) or "default"
              
            request.session["selected_voice"] = voice
            request.session["selected_style"] = style
            request.session["selected_rate"] = rate
            request.session["selected_pitch"] = pitch
            request.session["selected_volume"] = volume

            page = AudioPage.objects.get(id=page_id, user=user)
            page.default_voice = voice
            page.save()

            filename = f"{uuid.uuid4().hex}.mp3"
            filepath = os.path.join(AUDIO_DIR, filename)
            os.makedirs(AUDIO_DIR, exist_ok=True)

            ET.register_namespace('', "http://www.w3.org/2001/10/synthesis")
            ET.register_namespace('mstts', "http://www.w3.org/2001/mstts")

            speak = ET.Element('speak', version='1.0', xmlns='http://www.w3.org/2001/10/synthesis', attrib={'xml:lang': 'en-US'})
            voice_elem = ET.SubElement(speak, 'voice', name=voice)
            if style:
                express_as = ET.SubElement(voice_elem, '{http://www.w3.org/2001/mstts}express-as', attrib={'style': style})
                prosody = ET.SubElement(express_as, 'prosody', rate=rate, pitch=pitch, volume=volume)
            else:
                prosody = ET.SubElement(voice_elem, 'prosody', rate=rate, pitch=pitch, volume=volume)
            prosody.text = text
            ssml = ET.tostring(speak, encoding='utf8').decode()

            headers = {
                "Ocp-Apim-Subscription-Key": AZURE_TTS_KEY,
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
                "User-Agent": "MyDjangoApp"
            }
            response = requests.post(AZURE_ENDPOINT, headers=headers, data=ssml.encode('utf-8'))
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)

                audio_url = f"/media/audio/{filename}"
                logger.info(f"Generated audio file: {audio_url} for user {user.username}")
                GeneratedAudio.objects.create(
                    page=page, text=text, filename=filename,
                    voice=voice, style=style, rate=rate, pitch=pitch, volume=volume
                )
               
                #return redirect(f"/tts/?page={page_id}")
            # ✅ FIX: Return JSON if it's AJAX request
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({"audio_url": audio_url})
                else:
                    return redirect(f"/tts/?page={page_id}")
        elif "new_page" in request.POST and is_authenticated:
            new_page = AudioPage.objects.create(user=user, name=f"Page {pages.count() + 1}")
            return redirect(f"/tts/?page={new_page.id}")

        
        elif "preview" in request.POST:                     
            text = request.POST.get("text")
            voice = request.POST.get("voice") or selected_voice
            style = request.POST.get("style") or selected_style
            rate = request.POST.get("rate") + "%"
            pitch = request.POST.get("pitch") + "%"
            volume_raw = request.POST.get("volume", "100")
            volume = map_slider_to_volume(int(volume_raw)) if volume_raw.isdigit() else "default"


            request.session["selected_voice"] = voice
            request.session["selected_style"] = style
            request.session["selected_rate"] = rate
            request.session["selected_pitch"] = pitch
            request.session["selected_volume"] = volume

            if text:
                filename = f"preview_{uuid.uuid4().hex}.mp3"
                filepath = os.path.join(AUDIO_DIR, filename)
                os.makedirs(AUDIO_DIR, exist_ok=True)

                # SSML
                speak = ET.Element('speak', version='1.0', xmlns='http://www.w3.org/2001/10/synthesis', attrib={'xml:lang': 'en-US'})
                voice_elem = ET.SubElement(speak, 'voice', name=voice)

                if style:
                    express_as = ET.SubElement(voice_elem, '{http://www.w3.org/2001/mstts}express-as', attrib={'style': style})
                    prosody = ET.SubElement(express_as, 'prosody', rate=rate, pitch=pitch, volume=volume)
                else:
                    prosody = ET.SubElement(voice_elem, 'prosody', rate=rate, pitch=pitch, volume=volume)

                prosody.text = text
                ssml = ET.tostring(speak, encoding='utf8').decode()

                headers = {
                    "Ocp-Apim-Subscription-Key": AZURE_TTS_KEY,
                    "Content-Type": "application/ssml+xml",
                    "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
                    "User-Agent": "PreviewClient"
                }

                response = requests.post(AZURE_ENDPOINT, headers=headers, data=ssml.encode('utf-8'))

                if response.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(response.content)

                    audio_preview_url = f"/media/audio/{filename}"

                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({"audio_preview_url": audio_preview_url})
                    

            elif  "save_favorite" in request.POST and is_authenticated:
                voice = request.POST.get("voice")
                style = request.POST.get("style", "")

                if voice:
                    FavoriteVoice.objects.get_or_create(user=request.user, voice=voice, style=style)
                    logger.success(request, f"Voice '{voice}' with style '{style}' saved to favorites.")
                return redirect('/tts/')
    
    if selected_page_id and is_authenticated:
        for index, entry in enumerate(GeneratedAudio.objects.filter(page_id=selected_page_id).order_by('-created_at'), start=1):
            audio_list.append({
                "index": index,
                "url": f"/media/audio/{entry.filename}",
                "name": entry.filename,
                "path": os.path.join("media/audio", entry.filename),
                "text": entry.text,
                "id": entry.id,
                "created_at": timesince(entry.created_at, now()) + " ago",
                "voice": entry.voice,
                "style": entry.style,
                "rate": entry.rate,
                "pitch": entry.pitch,
                "volume": entry.volume
            })

    gender_groups = ["Female", "Male"]
    voice_display_map = {
        v.short_name: f"{get_flag_emoji(v.locale)} {get_language_display(v.locale)} - {v.short_name.split('-')[-1].replace('Neural', '')} ({v.gender[0]})"
        for v in VOICE_CHOICES
    }
    
    if request.user.is_authenticated:
     favorite_voices = FavoriteVoice.objects.filter(user=request.user)
    else:
     favorite_voices = []
   
    return render(request, "hello/text_to_speech.html", {
        "audio_url": audio_url,
        "audio_list": audio_list,
        "pages": pages,
        "selected_page_id": int(selected_page_id) if selected_page_id else None,
        "selected_voice": selected_voice,
        "selected_style": selected_style,
        "selected_rate": selected_rate,
        "selected_pitch": selected_pitch,
        "selected_volume": selected_volume,
        "voice_choices": VOICE_CHOICES,
        "voice": VOICE_CHOICES,
        "gender_groups": gender_groups,
        "voice_display_map": voice_display_map,
        "style_choices": STYLE_CHOICES,
        "is_authenticated": is_authenticated,
        "favorite_voices": favorite_voices,
        "favorite_list": FavoriteVoice.objects.filter(user=request.user) if request.user.is_authenticated else [],
        "show_news_bar": show_news_bar,
        "news_text": news_text,
        "scroll_speed": scroll_speed,
        "scroll_direction": scroll_direction,
        "show_close_button": show_close_button,
    })

import os
from django.conf import settings

@login_required
def delete_page(request):
    if request.method == "POST":
        page_id = request.POST.get("page_id")
        try:
            page = AudioPage.objects.get(id=page_id, user=request.user)
            audios = GeneratedAudio.objects.filter(page=page)
            for audio in audios:
                file_path = os.path.join(settings.MEDIA_ROOT, "audio", audio.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                audio.delete()
            page.delete()
        except AudioPage.DoesNotExist:
            pass
    return JsonResponse({"success": True})

SHORT_URL_MAP = {}

def shorten_url_view(request):
    long_url = request.GET.get("long_url")
    if not long_url:
        return JsonResponse({"error": "Missing URL"}, status=400)

    short_hash = hashlib.md5(long_url.encode()).hexdigest()[:6]
    short_url = request.build_absolute_uri(f"/s/{short_hash}")
    SHORT_URL_MAP[short_hash] = long_url

    return JsonResponse({"short_url": short_url})


def redirect_short_url(request, short_hash):
    long_url = SHORT_URL_MAP.get(short_hash)
    if long_url:
        return redirect(long_url)
    return JsonResponse({"error": "URL not found"}, status=404)

@csrf_exempt
def reset_voice_settings(request):
    if request.method == "POST" and request.user.is_authenticated:
        request.session["selected_rate"] = "0"
        request.session["selected_pitch"] = "0"
        request.session["selected_volume"] = "default"
        request.session["selected_style"] = ""
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

def tts_view(request):
    # your context setup here
    context = {
        # 'pages': ..., 'selected_page_id': ..., etc.
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'hello/tts_image.html', context)
    return render(request, 'hello/tts_image.html', context)



def voice_changer_view(request):
    # your context setup here
    context = {
        # 'pages': ..., 'selected_page_id': ..., etc.
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'hello/tts_image.html', context)
    return render(request, 'hello/tts_image.html', context)

def home(request):
    last_page = Page.objects.filter(user=request.user).last()
    context = {
        'pages': Page.objects.filter(user=request.user),
        'selected_page_id': last_page.id if last_page else None,
        # plus voice, style, audio_list etc.
    }
    return render(request, 'hello/text_to_speech.html', context)


def map_slider_to_volume(slider_value):
    """
    Maps a slider value (0–200) to Azure TTS volume values.
    Returns a string suitable for SSML, e.g., 'x-soft', 'medium', or '+10.00dB'
    """
    if slider_value <= 20:
        return "silent"
    elif slider_value <= 40:
        return "x-soft"
    elif slider_value <= 70:
        return "soft"
    elif slider_value <= 120:
        return "medium"
    elif slider_value <= 160:
        return "loud"
    else:
        return "x-loud"


@csrf_exempt
def fetch_and_store_azure_voices(request):
    url =f"https://{AZURE_TTS_REGION}.tts.speech.microsoft.com/cognitiveservices/voices/list"
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TTS_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices = response.json()
        AzureVoice.objects.all().delete()  # Clear old entries
        for v in voices:
            AzureVoice.objects.create(
                short_name=v['ShortName'],
                locale=v['Locale'],
                gender=v['Gender'],
                style_list=", ".join(v.get('StyleList', []))
            )
        return redirect("/tts/")
    else:
        logger.error("Failed to fetch voices from Azure")
        return redirect("/tts/")



@csrf_exempt
def rename_page(request):
    page_id = request.POST.get("page_id")
    new_name = request.POST.get("new_name")
    if page_id and new_name:
        try:
            page = AudioPage.objects.get(pk=page_id)
            page.name = new_name
            page.save()
        except AudioPage.DoesNotExist:
            pass
    return redirect(f"/tts/?page={page_id}")

@csrf_exempt
def delete_audio(request):
    audio_id = request.POST.get("audio_id")
    if audio_id:
        try:
            audio = GeneratedAudio.objects.get(pk=audio_id)
            file_path = os.path.join("media/audio", audio.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            audio.delete()
        except GeneratedAudio.DoesNotExist:
            pass
    return redirect("text_to_speech")


def saved_audios_page(request):
    audios = GeneratedAudio.objects.order_by('-created_at')
    return render(request, 'hello/saved_audios.html', {'audios': audios})




def analyze_photo(request):
 if request.method == 'POST' and request.FILES.get('photo'):
        photo = request.FILES['photo']

        # Save uploaded photo to /media/upload/
        upload_folder = os.path.join(settings.MEDIA_ROOT, 'upload')
        os.makedirs(upload_folder, exist_ok=True)

        fs = FileSystemStorage(location=upload_folder, base_url='/media/upload/')
        original_filename = fs.save(photo.name, photo)
        uploaded_image_url = fs.url(original_filename)

        # Path for enhanced image
        input_image_path = os.path.join(upload_folder, original_filename)
        enhanced_filename = f"enhanced_{original_filename}"
        enhanced_image_path = os.path.join(upload_folder, enhanced_filename)

        # Enhance photo
        enhancer = LinkedinPhotoEnhancer()
        enhancer.enhance_photo(input_image_path, enhanced_image_path)

        enhanced_image_url = fs.url(enhanced_filename)

        return render(request, 'hello/health_analyzer.html', {
            'uploaded_image': uploaded_image_url,
            'enhanced_image': enhanced_image_url,
            'analysis_result': "Image enhanced successfully for professional LinkedIn appearance."
        })


    

def health_analyzer(request):
    return render(request, 'hello/health_analyzer.html')

def contact_page():
    return render_template("contact.html")


def send_message(request):  # ✅ Add request parameter
    if request.method == 'POST':
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        sender_email = "connectbishar@gmail.com"
        sender_password = "dowl siih dpdk vxjs"
        recipient_email = "bnbishar@gmail.com"

        subject = f"New Contact Message from {name}"
        body = f"""
        Name: {name}
        Email: {email}
        Message: {message}
        """

        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = recipient_email

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

            return HttpResponse("<h3>✅ Message sent successfully! We'll get back to you soon.</h3>")
        except Exception as e:
            return HttpResponse(f"<h3>❌ Failed to send message: {str(e)}</h3>")
    
    return HttpResponse("<h3>❌ Invalid request method. Only POST is allowed.</h3>", status=405)

def services_fun(request):
    if request.method == "POST":
        form = TextDescriptionForm(request.POST)
        if form.is_valid():  # Form validation
            form.save()  # Saving to the database
            return redirect('services_fun')  # Redirect to success page after saving
        else:          
            print(form.errors)  # Log errors to console if form is invalid
    else:
        form = TextDescriptionForm()    

    # Retrieve all text descriptions with pagination
    text_descriptions = TextDescription.objects.all()
    paginator = Paginator(text_descriptions, 5)  # Show 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'hello/services.html', {'form': form, 'page_obj': page_obj})

def edit_text_description(request, id):
    text_description = get_object_or_404(TextDescription, id=id)
    if request.method == "POST":
        form = TextDescriptionForm(request.POST, instance=text_description)
        if form.is_valid():
            form.save()
            return redirect('services_fun')  # Redirect back to the list page
    else:
        form = TextDescriptionForm(instance=text_description)
     # Retrieve all text descriptions with pagination
    text_descriptions = TextDescription.objects.all()
    paginator = Paginator(text_descriptions, 5)  # Show 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'hello/services.html', {'form': form, 'page_obj': page_obj})

# views.py
def delete_text_description(request, id):
    text_description = get_object_or_404(TextDescription, id=id)
    if request.method == "POST":
        text_description.delete()
        return redirect('services_fun')  # Redirect back to the list page
    
      # Retrieve all text descriptions with pagination
    text_descriptions = TextDescription.objects.all()
    paginator = Paginator(text_descriptions, 5)  # Show 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'hello/services.html', {'page_obj': page_obj})


def success(request):
    return render(request, 'hello/success.html')


def Outlook(request):
        # Fetch all the TextDescription entries from the database
    text_descriptions = TextDescription.objects.all()    
    # Pass the entries to the template context
    return render(request, 'hello/outlook.html', {'text_descriptions': text_descriptions,})
    
def home(request):
        # Fetch all the TextDescription entries from the database
    text_descriptions = TextDescription.objects.all()    
    # Pass the entries to the template context
    return render(request, 'hello/home.html', {'text_descriptions': text_descriptions,})
    

def about(request):
    return render(request, 'hello/about.html', {'title': 'About Us'})

#def services(request):
#    return render(request, 'hello/services.html', {'title': 'Our Services'})
def HL7Parser(request):
        # Fetch all the TextDescription entries from the database
    text_descriptions = TextDescription.objects.all()    
    # Pass the entries to the template context
    return render(request, 'hello/HL7Parser.html', {'text_descriptions': text_descriptions,})
    
def Hl7Parserfun(request):
    if request.method == 'GET':      
        try: 
            # Example ORU HL7 message as a string
            description = request.GET.get('description',"")  
              
            hl7_message = """
            MSH|^~\\&|^PureNet|^PureNet|||20241028123923||ORU^R01|PN173010476359713||2.3.1\r
            PID|1||1810992^^^SK MRN|A1234566|ZZZTEST^TEST||20060914|M||||||0|1|||22156865^^^SK FIN|~|||||||||ANGOLAN\r
            PV1|1|O||||||||||||||N|||22156865^^^SK FIN|||||||||||||||||||||||||20241028123923\r
            ORC|RE|11865102183|4754057||||||20241028112800||^Dr. Stephan Weber\r
            OBR|1|11865102183|4754057|98271464^Activated Partial Thromboplastin Time (aPTT)^^98271464||20241028112800|20241028123838|||||||||^Dr. Stephan Weber|||000022024302000017|||20241028123838|||F\r
            OBX|1|NM|PT^Prothrombin Time (PT)^^5902-2||12.5|second(s)|11.0 - 14.0|N|||F|||20241028123838|||||||||ABU DHABI REF LAB\r
            OBX|2|NM|INR^Prothrombin Time (PT)||12.00|||N|||F|||20241028123838|||||||||ABU DHABI REF LAB\r
            OBX|3|ST|Anticoagulant?^Prothrombin Time (PT)||Heparin|||N|||F|||20241028123838|||||||||ABU DHABI REF LAB\r
            OBX|4|NM|FIB Activity^Fibrinogen||2.300|g/L|g/L|N|||F|||20241028123838|||||||||ABU DHABI REF LAB\r
            OBX|5|ST|Anticoagulant?^Fibrinogen||Heparin|||N|||F|||20241028123838|||||||||ABU DHABI REF LAB\r
            OBX|6|NM|D-DIMER^D-Dimer||4.50|||N|||F|||20241028123838|||||||||ABU DHABI REF LAB\r
            OBX|7|ST|Anticoagulant?^D-Dimer||LMWH|||N|||F|||20241028123838|||||||||ABU DHABI REF LAB\r
            OBX|8|NM|aPTT^Activated Partial Thromboplastin Time (aPTT)^^3173-2||31.0|second(s)|28.0 - 42.0|N|||F|||20241028123838|||||||||ABU DHABI REF LAB\r
            OBX|9|ST|Anticoagulant?^Activated Partial Thromboplastin Time (aPTT)||Warfarin|||N|||F|||20241028123838|||||||||ABU DHABI REF LAB\r
            """            
            hl7_message = """"""+ description +""""""
            print("......Orginal Description.........")    
            print(description)     
            print("......Orginal End  Description.........")    
            
        
            # Split message into segments
            segments = hl7_message.split('\n')

            # Iterate through segments
            hl7_message=""
            for segment in segments:
                #fields = segment.split('|') 
                if( len(segment)>0):
                    hl7_message=hl7_message + segment +"\r"
                    print('Segment ' +segment)


            print("......Hl7 Message.........     ") 
            #print(description)   
            print(hl7_message)   
            print("......Hl7 End here Message.........     ") 
            #hl7_message= "" +description +""
            # Parse the HL7 message
            #hl7_message = hl7_message.replace('\r', '\n')
            # Use regex to replace '\r' with '\n' 
            hl7_message_cleaned = re.sub(r'\r', '\n', hl7_message)

            parsed_message = hl7.parse(hl7_message)

            #print(hl7_message_cleaned)
            message_length = len(parsed_message) 
            print(f"The length of parsed_message is: {message_length}")
            # Extract required fields
            results = []           
            for segment in parsed_message:   
                #print(segment[0])   
                #print(str(segment[0]).strip())              
                  if str(segment).strip().startswith('MSH'):   # Check if it's an OBX segment           
                    mesage_controlid=segment[10][0]                             
                  if str(segment).strip().startswith('PV1'):   # Check if it's an OBX segment    
                    print(segment[0])       
                    fin_num=segment[19][0][0]                 
                  if  str(segment).strip().startswith('OBR'):   # Check if it's an OBX segment                                                   
                    order_code = str(segment[4][0][0]) # Order Code  
                    order_name = segment[4][0][1]  # Order Code 
                    order_id = segment[2][0]  # Order Code 
                    order_placerid = segment[3][0]  # Order Code       
                    order_datetime=segment[6][0]  # Order Code      
                  if str(segment).strip().startswith('OBX'):   # Check if it's an OBX segment              
                # order_code = segment[3][0][0]  # Order Code       
                    result_code = segment[3][0][1]  # Result Code
                    result_name = segment[3][0]  # Result Code
                    result_value = segment[5][0]  # Result Value
                    unit = segment[6][0] if len(segment[6]) > 0 else ""  # Unit
                    abnormal_flag = segment[8][0] if len(segment[8]) > 0 else ""  # Abnormal Flag
                    reference_range = segment[7][0] if len(segment[7]) > 0 else ""  # Reference Range
                    results.append({    
                        "MsgContID": mesage_controlid,
                        "Order Code": order_code,
                        "Order Name": order_name,
                        "Order_datetime":datetime.strptime(order_datetime, "%Y%m%d%H%M%S"),
                        "Order Id": order_id,
                        "Placerid": order_placerid,  
                        "Fin Num" : fin_num,     
                        "Result Code": result_code,
                        "DTA": result_name,
                        "Result Value": result_value,
                        "Unit": unit,
                        "Abnormal Flag": abnormal_flag,
                        "Reference Range": reference_range
                    })       
                #results_new=str(mesage_controlid) +','+ordercode
            
               

            # Convert results to a DataFrame
            print(results)
            df = pd.DataFrame(results)           
            df_string=  df.to_string()           
            # Save to CSV
            df.to_csv("HL7_Parsed_Results.csv", index=False)
           

            return JsonResponse({'data': results})
           # Retrieve all text descriptions with pagination
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)


def chatbot_page(request):
    messages = ChatMessage.objects.order_by('timestamp')

    allowed_tags = bleach.sanitizer.ALLOWED_TAGS.union({'p', 'pre', 'code', 'br', 'strong', 'em', 'ul', 'li', 'ol'})
    for msg in messages:
        html_content = markdown.markdown(msg.message)
        sanitized = bleach.clean(html_content, tags=allowed_tags)
        msg.message = html.unescape(sanitized)  # ✅ Unescape things like \u003C into <

    return render(request, 'hello/chatbot.html', {'messages': messages})

@csrf_protect
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()

            if not user_message:
                return JsonResponse({'reply': "Please enter a message."}, status=400)

            # Save user message
            ChatMessage.objects.create(sender="user", message=user_message)

            # OpenAI call
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ],
                timeout=10
            )

            raw_reply = response.choices[0].message.content.strip()

            # ✅ Render markdown -> sanitize -> unescape
            rendered = markdown.markdown(raw_reply)
            safe_html = bleach.clean(rendered, tags=bleach.sanitizer.ALLOWED_TAGS.union({'p', 'ul', 'ol', 'li', 'pre', 'code', 'strong', 'em', 'br'}))
            clean_reply = html.unescape(safe_html)

            # ✅ Save bot reply
            ChatMessage.objects.create(sender="bot", message=clean_reply)

            return JsonResponse({'reply': clean_reply})

        except Exception as e:         
            return JsonResponse({'reply': "Something went wrong."}, status=500)

    return HttpResponseNotAllowed(['POST'], 'Only POST method is allowed.')



@require_http_methods(["DELETE"])
@csrf_protect
def delete_message(request, pk):
    try:
        msg = ChatMessage.objects.get(pk=pk)
        msg.delete()
        return JsonResponse({"status": "deleted"})
    except ChatMessage.DoesNotExist:
        return JsonResponse({"error": "Message not found"}, status=404)
    

def contact(request):
    return render(request, 'hello/contact.html', {'title': 'Contact Us'})

def get_poem(request):    
    # form = TextDescriptionForm(request.GET)
    # if form.is_valid():  # Form validation
    #     form.save()  # Saving to the database
    #     return redirect('services_fun')  # Redirect to success page after saving
    # else:          
    #     print(form.errors)  # Log errors to console if form is invalid

    if request.method == 'GET':
        title = request.GET.get('title',"Artifical intellegence and programing using python")
        description = request.GET.get('description',"use cases of ai in healthcare ")
          # Print the values for debugging
        #logger.debug("Topic: " + topic)
        #logger.debug("Description: " + description)

        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": title},
                    {"role": "user", "content": description }
                ]
            )
            poem = completion.choices[0].message['content']
            return JsonResponse({'poem': poem})
           # Retrieve all text descriptions with pagination
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)
     
    

def outlookextract(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    title = request.GET.get('title', "Default Title")
    description = request.GET.get('description', "Default Description")

    try:
        
        # Placeholder for external API call
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": title},
                {"role": "user", "content": description}
            ]
        )
        poem = completion.choices[0].message['content']

        return JsonResponse({'poem': poem})

    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return JsonResponse({'error': 'OpenAI API error', 'details': str(e)}, status=500)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)


def outlookextract_old(request):    
    if request.method == 'GET':
        title = request.GET.get('title', "Artificial intelligence and programming using Python")
        description = request.GET.get('description', "Use cases of AI in healthcare")

        try:
            # Connect to Outlook and fetch emails
            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            inbox = outlook.GetDefaultFolder(6)  # 6 refers to the Inbox folder
            messages = inbox.Items
            messages.Sort("[ReceivedTime]", True)  # Sort by received time (newest first)

            # Initialize data collection
            email_data = []
            email_subjects = []

            for message in messages:
                if message.Class == 43:  # Ensure it's a MailItem
                    subject = message.Subject
                    body = message.Body
                    print("subject: " + subject)
                    # Store subjects for summary
                    email_subjects.append(subject)

                    # Pass email content to ChatGPT
                    completion = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": title},
                            {"role": "user", "content": f"{description}\n\nEmail Subject: {subject}\nEmail Body: {body}"}
                        ]
                    )

                    response = completion.choices[0].message['content']
                    email_data.append({
                        'subject': subject,
                        'response': response
                    })

                    # Process a limited number of emails (e.g., 10 for performance reasons)
                    if len(email_data) >= 10:
                        break

            # Summarize processed email subjects
            summary = {
                "total_emails_processed": len(email_data),
                "subjects": email_subjects
            }

            return JsonResponse({'email_data': email_data, 'summary': summary})

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        logger.error(f"Error processing request: {str(e)}")
        return JsonResponse({'error': 'Invalid method'}, status=405)
     
    


def submit_form(request):
    if request.method == 'POST':
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
                    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
                ]
            )
            poem = response['choices'][0]['message']['content']
            return JsonResponse({'poem': poem})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)