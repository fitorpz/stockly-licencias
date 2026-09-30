from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from clientes.models import Cliente
from licencias.models import Licencia


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(
                request,
                "Debe ingresar usuario y contraseña.",
            )
            return render(request, "auth/login.html")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            messages.error(
                request,
                "Usuario o contraseña incorrectos.",
            )
            return render(request, "auth/login.html")

        if not user.is_active:
            messages.error(
                request,
                "El usuario se encuentra inactivo.",
            )
            return render(request, "auth/login.html")

        login(request, user)
        return redirect("dashboard")

    return render(request, "auth/login.html")


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")

    return redirect("dashboard")


@login_required
def dashboard_view(request):
    ahora = timezone.now()
    limite_por_vencer = ahora + timedelta(days=30)

    clientes_total = Cliente.objects.filter(
        activo=True,
    ).count()

    licencias_activas = Licencia.objects.filter(
        estado=Licencia.Estado.ACTIVA,
        fecha_vencimiento__gt=ahora,
    ).count()

    licencias_por_vencer = Licencia.objects.filter(
        estado=Licencia.Estado.ACTIVA,
        fecha_vencimiento__gt=ahora,
        fecha_vencimiento__lte=limite_por_vencer,
    ).count()

    licencias_vencidas = Licencia.objects.filter(
        estado=Licencia.Estado.ACTIVA,
        fecha_vencimiento__lte=ahora,
    ).count()

    context = {
        "clientes_total": clientes_total,
        "licencias_activas": licencias_activas,
        "licencias_por_vencer": licencias_por_vencer,
        "licencias_vencidas": licencias_vencidas,
    }

    return render(
        request,
        "dashboard/index.html",
        context,
    )