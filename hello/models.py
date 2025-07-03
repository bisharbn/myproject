from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class TextDescription(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title
    

class ChatMessage(models.Model):
    sender = models.CharField(max_length=10)  # "user" or "bot"
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M')}] {self.sender}: {self.message[:50]}"

class AudioPage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ✅ add this
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    default_voice = models.CharField(max_length=100, default='en-US-JennyNeural')

    def __str__(self):
        return self.name    


class GeneratedAudio(models.Model):
    page = models.ForeignKey(AudioPage, on_delete=models.CASCADE, related_name='audios')
    text = models.TextField()
    filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    voice = models.CharField(max_length=100, default='en-US-JennyNeural')
    style = models.CharField(max_length=100, blank=True, null=True)
    rate = models.CharField(max_length=50, default='0%', null=True, blank=True)
    pitch = models.CharField(max_length=50, default='0%', null=True, blank=True)
    volume = models.CharField(max_length=20, default='default', null=True, blank=True)

    def __str__(self):
        return self.filename

class AzureVoice(models.Model):
    short_name = models.CharField(max_length=100, unique=True)
    locale = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    style_list = models.TextField(blank=True)

    def __str__(self):
        return f"{self.short_name} ({self.locale}, {self.gender})"




class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_id = models.CharField(max_length=255, blank=True)
    profile_pic = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    is_first_login = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

class LoginAudit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    location = models.CharField(max_length=255, blank=True)
    device = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

class FavoriteVoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voice = models.CharField(max_length=100)
    style = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'voice', 'style')  # prevent duplicates

    def __str__(self):
        return f"{self.voice} ({self.style})"
page = models.ForeignKey(AudioPage, on_delete=models.CASCADE, related_name='audios', null=True)


class SiteSetting(models.Model):
    show_news_bar = models.BooleanField(default=True)
    news_text = models.TextField(default="🔊 This is a totally free Text-to-Audio tool. Contact support@melticetechnology.com for professional tools.")
    start_date = models.DateField(default=timezone.now)
    show_days = models.PositiveIntegerField(default=30)

    scroll_speed = models.PositiveIntegerField(default=20, help_text="Time (in seconds) for one full scroll loop.")
    scroll_direction = models.CharField(
        max_length=20,
        choices=[("left", "Right to Left"), ("right", "Left to Right")],
        default="right"
    )
    show_close_button = models.BooleanField(default=True)

    def is_active(self):
        return self.show_news_bar and timezone.now().date() <= (self.start_date + timedelta(days=self.show_days))

    def __str__(self):
        return "Global Site Settings"
