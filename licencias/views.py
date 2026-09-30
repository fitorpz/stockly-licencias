from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LicenciaForm, RenovacionForm
from .models import Licencia
from .services import crear_licencia, renovar_licencia


@login_required
def licencia_lista(request):
    buscar = request.GET.get("buscar", "").strip()
    estado = request.GET.get("estado", "").strip()

    licencias = Licencia.objects.select_related(
        "cliente",
        "creado_por",
    ).all()

    if buscar:
        licencias = licencias.filter(
            Q(codigo__icontains=buscar)
            | Q(cliente__nombre__icontains=buscar)
            | Q(cliente__razon_social__icontains=buscar)
            | Q(cliente__nit_documento__icontains=buscar)
        )

    if estado:
        licencias = licencias.filter(estado=estado)

    context = {
        "licencias": licencias,
        "buscar": buscar,
        "estado": estado,
        "estados": Licencia.Estado.choices,
    }

    return render(
        request,
        "licencias/lista.html",
        context,
    )


@login_required
def licencia_crear(request):
    if request.method == "POST":
        form = LicenciaForm(request.POST)

        if form.is_valid():
            licencia = crear_licencia(
                cliente=form.cleaned_data["cliente"],
                creditos=form.cleaned_data["creditos"],
                bonificacion=form.cleaned_data["bonificacion"],
                usuario=request.user,
                observaciones=form.cleaned_data["observaciones"],
            )

            messages.success(
                request,
                f"Licencia {licencia.codigo} generada correctamente.",
            )

            return redirect(
                "licencia_detalle",
                pk=licencia.pk,
            )
    else:
        form = LicenciaForm()

    return render(
        request,
        "licencias/formulario.html",
        {
            "form": form,
        },
    )


@login_required
def licencia_detalle(request, pk):
    licencia = get_object_or_404(
        Licencia.objects.select_related(
            "cliente",
            "creado_por",
        ),
        pk=pk,
    )

    dispositivos = licencia.dispositivos.all()

    renovaciones = licencia.renovaciones.select_related("creado_por",).all()

    context = {
        "licencia": licencia,
        "dispositivos": dispositivos,
        "renovaciones": renovaciones,
    }

    return render(
        request,
        "licencias/detalle.html",
        context,
    )

@login_required
def licencia_renovar(request, pk):
    licencia = get_object_or_404(
        Licencia,
        pk=pk,
    )

    if request.method == "POST":
        form = RenovacionForm(request.POST)

        if form.is_valid():
            try:
                licencia = renovar_licencia(
                    licencia=licencia,
                    creditos=form.cleaned_data["creditos"],
                    bonificacion=form.cleaned_data["bonificacion"],
                    monto=form.cleaned_data["monto"],
                    usuario=request.user,
                    observaciones=form.cleaned_data["observaciones"],
                )

                messages.success(
                    request,
                    "Licencia renovada correctamente.",
                )

                return redirect(
                    "licencia_detalle",
                    pk=licencia.pk,
                )

            except ValueError as error:
                messages.error(
                    request,
                    str(error),
                )
    else:
        form = RenovacionForm(
            initial={
                "creditos": 1,
                "bonificacion": 0,
                "monto": 0,
            }
        )

    return render(
        request,
        "licencias/renovar.html",
        {
            "licencia": licencia,
            "form": form,
        },
    )