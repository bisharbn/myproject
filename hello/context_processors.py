from .models import SiteSetting

def site_settings(request):
    try:
        setting = SiteSetting.objects.first()
        return {
            "show_news_bar": setting.is_active(),
            "news_text": setting.news_text,
        }
    except:
        return {
            "show_news_bar": False,
            "news_text": "",
        }
 