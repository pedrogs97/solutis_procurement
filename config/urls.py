"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

from src.supplier.urls.attachment import urlpatterns as attachment_urls
from src.supplier.urls.domain import urlpatterns as domain_urls
from src.supplier.urls.responsibility_matrix import (
    urlpatterns as responsibility_matrix_urls,
)
from src.supplier.urls.supplier import urlpatterns as supplier_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(supplier_urls)),
    path("api/", include(attachment_urls)),
    path("api/", include(responsibility_matrix_urls)),
    path("api/domain/", include(domain_urls)),
    path("api/", lambda request: HttpResponse(status=200), name="healthcheck"),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
