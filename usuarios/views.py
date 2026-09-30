from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    UsuarioCrearForm,
    UsuarioEditarForm,
    UsuarioPasswordForm,
)


@login_required
def usuario_lista(request):
    buscar = request.GET.get("buscar", "").strip()
    estado = request.GET.get("estado", "").strip()

    usuarios = User.objects.all().order_by("username")

    if buscar:
        usuarios = usuarios.filter(
            Q(username__icontains=buscar)
            | Q(first_name__icontains=buscar)
            | Q(last_name__icontains=buscar)
            | Q(email__icontains=buscar)
        )

    if estado == "activo":
        usuarios = usuarios.filter(is_active=True)

    elif estado == "inactivo":
        usuarios = usuarios.filter(is_active=False)

    context = {
        "usuarios": usuarios,
        "buscar": buscar,
        "estado": estado,
    }

    return render(
        request,
        "usuarios/lista.html",
        context,
    )


@login_required
def usuario_crear(request):
    if request.method == "POST":
        form = UsuarioCrearForm(request.POST)

        if form.is_valid():
            usuario = form.save()

            messages.success(
                request,
                f"El usuario {usuario.username} fue creado correctamente.",
            )

            return redirect("usuario_lista")

    else:
        form = UsuarioCrearForm(
            initial={
                "is_active": True,
            }
        )

    return render(
        request,
        "usuarios/formulario.html",
        {
            "form": form,
            "titulo": "Nuevo usuario",
            "texto_boton": "Crear usuario",
        },
    )


@login_required
def usuario_editar(request, pk):
    usuario = get_object_or_404(
        User,
        pk=pk,
    )

    if request.method == "POST":
        form = UsuarioEditarForm(
            request.POST,
            instance=usuario,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Usuario actualizado correctamente.",
            )

            return redirect("usuario_lista")

    else:
        form = UsuarioEditarForm(
            instance=usuario,
        )

    return render(
        request,
        "usuarios/formulario.html",
        {
            "form": form,
            "titulo": "Editar usuario",
            "texto_boton": "Guardar cambios",
            "usuario_editado": usuario,
        },
    )


@login_required
def usuario_password(request, pk):
    usuario = get_object_or_404(
        User,
        pk=pk,
    )

    if request.method == "POST":
        form = UsuarioPasswordForm(request.POST)

        if form.is_valid():
            usuario.set_password(
                form.cleaned_data["password1"]
            )

            usuario.save(
                update_fields=["password"]
            )

            messages.success(
                request,
                f"Contraseña de {usuario.username} actualizada correctamente.",
            )

            return redirect("usuario_lista")

    else:
        form = UsuarioPasswordForm()

    return render(
        request,
        "usuarios/password.html",
        {
            "form": form,
            "usuario_editado": usuario,
        },
    )


@login_required
@require_POST
def usuario_cambiar_estado(request, pk):
    usuario = get_object_or_404(
        User,
        pk=pk,
    )

    if usuario.pk == request.user.pk:
        messages.error(
            request,
            "No puede desactivar su propio usuario.",
        )

        return redirect("usuario_lista")

    usuario.is_active = not usuario.is_active

    usuario.save(
        update_fields=["is_active"]
    )

    if usuario.is_active:
        messages.success(
            request,
            f"El usuario {usuario.username} fue activado.",
        )
    else:
        messages.warning(
            request,
            f"El usuario {usuario.username} fue desactivado.",
        )

    return redirect("usuario_lista")