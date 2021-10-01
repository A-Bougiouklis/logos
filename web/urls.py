from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from web.core.views import home


urlpatterns = [
                url(r"^admin/", admin.site.urls),
                path(route="home/", view=home, name="health"),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
