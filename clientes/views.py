from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClienteForm
from .models import Cliente


@login_required
def cliente_lista(request):
    buscar = request.GET.get("buscar", "").strip()

    clientes = Cliente.objects.all()

    if buscar:
        clientes = clientes.filter(
            Q(nombre__icontains=buscar)
            | Q(razon_social__icontains=buscar)
            | Q(nit_documento__icontains=buscar)
            | Q(telefono__icontains=buscar)
            | Q(email__icontains=buscar)
        )

    context = {
        "clientes": clientes,
        "buscar": buscar,
    }

    return render(
        request,
        "clientes/lista.html",
        context,
    )


@login_required
def cliente_crear(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)

        if form.is_valid():
            cliente = form.save()

            messages.success(
                request,
                f"Cliente {cliente.nombre} registrado correctamente.",
            )

            return redirect("cliente_lista")
    else:
        form = ClienteForm()

    return render(
        request,
        "clientes/formulario.html",
        {
            "form": form,
            "titulo": "Nuevo cliente",
        },
    )


@login_required
def cliente_editar(request, pk):
    cliente = get_object_or_404(
        Cliente,
        pk=pk,
    )

    if request.method == "POST":
        form = ClienteForm(
            request.POST,
            instance=cliente,
        )

        if form.is_valid():
            cliente = form.save()

            messages.success(
                request,
                f"Cliente {cliente.nombre} actualizado correctamente.",
            )

            return redirect("cliente_lista")
    else:
        form = ClienteForm(
            instance=cliente,
        )

    return render(
        request,
        "clientes/formulario.html",
        {
            "form": form,
            "cliente": cliente,
            "titulo": "Editar cliente",
        },
    )


@login_required
def cliente_cambiar_estado(request, pk):
    cliente = get_object_or_404(
        Cliente,
        pk=pk,
    )

    if request.method == "POST":
        cliente.activo = not cliente.activo
        cliente.save(
            update_fields=[
                "activo",
                "actualizado_en",
            ]
        )

        estado = "activado" if cliente.activo else "desactivado"

        messages.success(
            request,
            f"Cliente {estado} correctamente.",
        )

    return redirect("cliente_lista")
