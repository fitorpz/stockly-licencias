from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("base.urls")),
    path("", include("usuarios.urls")),
    path("", include("clientes.urls")),
    path("", include("licencias.urls")),
    path("api/licencias/", include("licencias.api_urls"),),
    path(
        "",
        RedirectView.as_view(
            pattern_name="dashboard",
            permanent=False,
        ),
        name="inicio",
    ),
]
