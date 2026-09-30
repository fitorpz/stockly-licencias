from django.contrib import admin

from .models import (
    Activacion,
    Dispositivo,
    Licencia,
    Plan,
    Renovacion,
)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "creditos",
        "meses_vigencia",
        "precio",
        "activo",
    )

    list_filter = ("activo",)

    search_fields = ("nombre",)


@admin.register(Licencia)
class LicenciaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "cliente",
        "creditos",
        "bonificacion",
        "estado",
        "fecha_activacion",
        "fecha_vencimiento",
        "creado_por",
    )

    list_filter = ("estado",)

    search_fields = (
        "codigo",
        "cliente__nombre",
        "cliente__razon_social",
        "cliente__nit_documento",
    )

    autocomplete_fields = ("cliente",)

    readonly_fields = (
        "fecha_creacion",
        "actualizado_en",
    )


@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = (
        "installation_id",
        "licencia",
        "nombre_dispositivo",
        "plataforma",
        "version_app",
        "activo",
        "primera_activacion",
    )

    list_filter = (
        "activo",
        "plataforma",
    )

    search_fields = (
        "installation_id",
        "nombre_dispositivo",
        "licencia__codigo",
    )


@admin.register(Activacion)
class ActivacionAdmin(admin.ModelAdmin):
    list_display = (
        "licencia",
        "dispositivo",
        "fecha",
        "ip",
        "version_app",
        "exitosa",
    )

    list_filter = (
        "exitosa",
        "fecha",
    )

    search_fields = (
        "licencia__codigo",
        "dispositivo__installation_id",
        "ip",
    )

    readonly_fields = ("fecha",)


@admin.register(Renovacion)
class RenovacionAdmin(admin.ModelAdmin):
    list_display = (
        "licencia",
        "creditos",
        "bonificacion",
        "fecha",
        "vencimiento_anterior",
        "nuevo_vencimiento",
        "monto",
        "creado_por",
    )

    list_filter = ("fecha",)

    search_fields = (
        "licencia__codigo",
        "licencia__cliente__nombre",
    )

    readonly_fields = ("fecha",)