from django.contrib import admin
from django.urls import path, include
from donationapp import views  # Import your app views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('donationapp/', include('donationapp.urls')),  # Keep this for other app routes
    path('', views.home, name='home'),  # Redirect root URL to index page
    path('captcha/', include('captcha.urls')),
]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
