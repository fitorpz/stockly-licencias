from django.urls import path

from . import views


urlpatterns = [
    path(
        "usuarios/",
        views.usuario_lista,
        name="usuario_lista",
    ),
    path(
        "usuarios/nuevo/",
        views.usuario_crear,
        name="usuario_crear",
    ),
    path(
        "usuarios/<int:pk>/editar/",
        views.usuario_editar,
        name="usuario_editar",
    ),
    path(
        "usuarios/<int:pk>/password/",
        views.usuario_password,
        name="usuario_password",
    ),
    path(
        "usuarios/<int:pk>/estado/",
        views.usuario_cambiar_estado,
        name="usuario_cambiar_estado",
    ),
]