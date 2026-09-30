from django.urls import path

from . import views

urlpatterns = [
    path(
        "licencias/",
        views.licencia_lista,
        name="licencia_lista",
    ),
    path(
        "licencias/nueva/",
        views.licencia_crear,
        name="licencia_crear",
    ),
    path(
        "licencias/<uuid:pk>/",
        views.licencia_detalle,
        name="licencia_detalle",
    ),
    path(
        "licencias/<uuid:pk>/renovar/",
        views.licencia_renovar,
        name="licencia_renovar",
    ),
]
