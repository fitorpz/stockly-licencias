from django.urls import path

from . import api_views


urlpatterns = [
    path(
        "activar/",
        api_views.activar,
        name="api_licencia_activar",
    ),

    path(
        "validar/",
        api_views.validar,
        name="api_licencia_validar",
    ),
]