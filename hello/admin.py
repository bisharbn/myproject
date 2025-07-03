from django.contrib import admin
from .models import LoginAudit
from .models import SiteSetting  # Adjust if models are in a different app

@admin.register(LoginAudit)
class LoginAuditAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time', 'ip_address', 'location', 'device')
    list_filter = ('user', 'device', 'location')
    search_fields = ('user__username', 'ip_address', 'location', 'user_agent')
    ordering = ('-login_time',)
    readonly_fields = ('user', 'login_time', 'logout_time', 'ip_address', 'location', 'device', 'user_agent')

    def has_add_permission(self, request):
        return False  # Prevent manual addition

    def has_change_permission(self, request, obj=None):
        return False  # Make records read-only
from django.contrib import admin
from .models import SiteSetting

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'show_news_bar',
        'news_text',
        'scroll_speed',
        'scroll_direction',
        'show_close_button',
        'start_date',
        'show_days',
    )
    list_display_links = ('id',)
    list_editable = (
        'show_news_bar',
        'news_text',
        'scroll_speed',
        'scroll_direction',
        'show_close_button',
        'start_date',
        'show_days',
    )
