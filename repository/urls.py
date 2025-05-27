from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from papers.views import get_current_language

urlpatterns = [
    path('i18n/', set_language, name='set_language'),
    path('debug-language/', get_current_language, name='debug_language'),
] + i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('papers.urls')),
    prefix_default_language=True,  # Ensure the default language (uk) gets a prefix
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)