from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "razon_social",
        "nit_documento",
        "telefono",
        "ciudad",
        "activo",
    )
    list_filter = (
        "tipo",
        "activo",
        "ciudad",
    )

    search_fields = (
        "nombre",
        "razon_social",
        "nit_documento",
        "telefono",
        "email",
    )

    ordering = ("nombre",)
