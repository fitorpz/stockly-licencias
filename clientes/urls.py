from django.urls import path

from . import views

urlpatterns = [
    path(
        "clientes/",
        views.cliente_lista,
        name="cliente_lista",
    ),
    path(
        "clientes/nuevo/",
        views.cliente_crear,
        name="cliente_crear",
    ),
    path(
        "clientes/<int:pk>/editar/",
        views.cliente_editar,
        name="cliente_editar",
    ),
    path(
        "clientes/<int:pk>/estado/",
        views.cliente_cambiar_estado,
        name="cliente_cambiar_estado",
    ),
]
